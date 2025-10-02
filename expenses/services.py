import os
import re
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

from django.core.files.base import ContentFile
from django.conf import settings
from django.utils import timezone
import pandas as pd
from pypdf import PdfReader, PdfWriter
import PyPDF2

from .models import BankStatement, Transaction, DecryptionKey

logger = logging.getLogger(__name__)


class BankStatementProcessorService:
    """
    Service class to process bank statement PDFs.
    Handles decryption, text extraction, and transaction parsing.
    """

    def __init__(self, bank_statement: BankStatement):
        self.bank_statement = bank_statement
        self.debug = getattr(settings, 'BANK_STATEMENT_DEBUG', False)

    def process_statement(self) -> bool:
        """
        Main method to process a bank statement.
        Returns True if successful, False otherwise.
        """
        try:
            self.bank_statement.status = 'processing'
            self.bank_statement.save()

            # Get the file path
            file_path = self.bank_statement.file.path

            # Check if PDF is encrypted and decrypt if needed
            decrypted_path = None
            if self._is_pdf_encrypted(file_path):
                self.bank_statement.is_encrypted = True
                self.bank_statement.save()
                decrypted_path = self._decrypt_pdf(file_path)
                if not decrypted_path:
                    raise Exception("Failed to decrypt PDF")
                file_path = decrypted_path

            # Convert PDF to text
            text_content = self._convert_pdf_to_text(file_path)

            # Parse transactions from text
            dataframe = self._parse_transactions_from_text(text_content)

            # Save transactions to database
            self._save_transactions(dataframe)

            # Clean up temporary files
            if decrypted_path and os.path.exists(decrypted_path):
                os.remove(decrypted_path)

            # Update status
            self.bank_statement.status = 'completed'
            self.bank_statement.processed_at = timezone.now()
            self.bank_statement.save()

            logger.info(f"Successfully processed bank statement: {self.bank_statement.id}")
            return True

        except Exception as e:
            logger.error(f"Error processing bank statement {self.bank_statement.id}: {str(e)}")
            self.bank_statement.status = 'failed'
            self.bank_statement.error_message = str(e)
            self.bank_statement.save()
            return False

    def _is_pdf_encrypted(self, file_path: str) -> bool:
        """Check if PDF is encrypted"""
        try:
            reader = PdfReader(file_path)
            return reader.is_encrypted
        except Exception as e:
            logger.error(f"Error checking PDF encryption: {str(e)}")
            return False

    def _decrypt_pdf(self, file_path: str) -> Optional[str]:
        """
        Decrypt PDF using available decryption keys.
        Returns path to decrypted file or None if decryption fails.
        """
        try:
            reader = PdfReader(file_path)
            writer = PdfWriter()

            # Get active decryption keys from database
            keys = DecryptionKey.objects.filter(is_active=True).values_list('key', flat=True)

            if not keys:
                logger.error("No decryption keys available in database")
                return None

            # Try each key
            decrypted = False
            for key in keys:
                if reader.is_encrypted:
                    decrypt_status = reader.decrypt(key)
                    if decrypt_status == 2:  # 2 = success
                        decrypted = True
                        break

            if not decrypted:
                logger.error(f"Could not decrypt PDF with any available key")
                return None

            # Add all pages to the writer
            for page in reader.pages:
                writer.add_page(page)

            # Create temporary file for decrypted PDF
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            with open(temp_file.name, 'wb') as f:
                writer.write(f)

            logger.info(f"Successfully decrypted PDF: {file_path}")
            return temp_file.name

        except Exception as e:
            logger.error(f"Error decrypting PDF: {str(e)}")
            return None

    def _convert_pdf_to_text(self, file_path: str) -> str:
        """Convert PDF to text content"""
        try:
            content = ''
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pages = len(pdf_reader.pages)

                for page_num in range(pages):
                    page_obj = pdf_reader.pages[page_num]
                    text = page_obj.extract_text()
                    if self.debug:
                        logger.debug(f"Page {page_num}: {text}")
                    content += text

            logger.info(f"Extracted text from {pages} pages")
            return content

        except Exception as e:
            logger.error(f"Error converting PDF to text: {str(e)}")
            raise

    def _parse_transactions_from_text(self, text: str) -> pd.DataFrame:
        """
        Parse transaction data from text content.
        Based on the original notepad2data function.
        """
        lines = text.split('\n')

        date_arr = []
        trans_ref_arr = []
        chq_ref_arr = []
        credit_arr = []
        debit_arr = []
        bal_arr = []

        temp_line = ''

        for line_no, line in enumerate(lines):
            if line_no <= 72:  # Skip header lines
                continue

            line = line.replace('TRANSACTION OVERVIEW', '')

            if temp_line == '':
                date = line[:8] if len(line) >= 8 else ''
                # Check if first 8 chars are date
                date_match = re.search(r"^(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[012])[\/\-]\d{2}$", date)
                if not date_match:
                    continue

            # Check if line ends with a number (balance)
            number_match = re.search(r"\d{1,}\.\d{2}\n", line)
            if not number_match:
                temp_line = line
                continue
            else:
                line = temp_line + line
                temp_line = ''

            # Extract date
            date = line[:8]
            # Convert date format from DD-MM-YY to YYYY-MM-DD
            date = f"20{date[6:8]}-{date[3:5]}-{date[:2]}"
            date_arr.append(date)

            line = line[8:].strip()

            # Split transaction text and numbers
            dash_pos = line.find('- ')
            trans_ref_text = line[:dash_pos] if dash_pos != -1 else ''

            match = ' ' + line[dash_pos:] if dash_pos != -1 else ' ' + line
            match = match.split(' ')

            if len(match) != 5:  # Special case handling
                numbers_found = re.findall(r"(\d{1,}\.\d{2})", line)
                match = ['0'] * 5

                # Find cheque number position
                check_match = re.search(r"([-]|[ ])[0-9]*([-]|[ ])*[0-9]*($|\.\d{2})", line)
                if check_match:
                    check_no = line[check_match.start():].lstrip().split(' ')[0]
                    trans_ref_text = trans_ref_text[:check_match.start()]
                    match[1] = check_no
                    if len(numbers_found) >= 2:
                        match[2] = numbers_found[0]  # credit
                        match[4] = numbers_found[1]  # balance

            trans_ref_arr.append(trans_ref_text.strip())
            chq_ref_arr.append(match[1].replace('-', ''))
            credit_arr.append(match[2].replace('-', '0'))
            debit_arr.append(match[3].replace('-', '0'))
            bal_arr.append(match[4].replace('-', '0'))

        # Create DataFrame
        df = pd.DataFrame({
            'date': date_arr,
            'transactionIdRef': trans_ref_arr,
            'chequeRefNo': chq_ref_arr,
            'credit': credit_arr,
            'debit': debit_arr,
            'balance': bal_arr
        })

        logger.info(f"Parsed {len(df)} transactions")
        return df

    def _save_transactions(self, dataframe: pd.DataFrame) -> None:
        """Save transactions to database"""
        transactions = []

        for _, row in dataframe.iterrows():
            transaction = Transaction(
                bank_statement=self.bank_statement,
                user=self.bank_statement.user,
                date=row['date'],
                transaction_id_ref=row['transactionIdRef'],
                cheque_ref_no=row['chequeRefNo'],
                credit=float(row['credit']),
                debit=float(row['debit']),
                balance=float(row['balance'])
            )
            transactions.append(transaction)

        # Bulk create for better performance
        Transaction.objects.bulk_create(transactions)
        logger.info(f"Saved {len(transactions)} transactions to database")


class BankStatementHelper:
    """Helper methods for bank statement processing"""

    @staticmethod
    def get_filename_metadata(file_path: str) -> Dict[str, str]:
        """Extract filename metadata from absolute path"""
        file_parts = file_path.replace('/', '\\').split('\\')
        filename = file_parts[-1]
        name_parts = filename.split('.')

        return {
            'file': filename,
            'filename': name_parts[0] if len(name_parts) > 0 else '',
            'ext': name_parts[1] if len(name_parts) > 1 else '',
            'path': file_path.replace(filename, '')
        }

    @staticmethod
    def parse_date_from_filename(filename: str) -> Optional[datetime]:
        """
        Parse date from filename if it follows the pattern: YYYY_MM_DD_description
        """
        try:
            parts = filename.split('_')
            if len(parts) >= 3:
                year = int(parts[0])
                month = int(parts[1])
                day = int(parts[2])
                return datetime(year, month, day)
        except (ValueError, IndexError):
            pass
        return None
