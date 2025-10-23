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

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available. Table extraction will use fallback method.")

from .models import BankStatement, Transaction, DecryptionKey, Category, Expense

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

            # If no transactions found, try table extraction middleware
            if len(dataframe) == 0:
                logger.info("No transactions found with text parsing. Attempting table extraction...")
                dataframe = self._extract_transactions_from_table(file_path)

            # Check if any transactions were found after both methods
            if len(dataframe) == 0:
                raise Exception(
                    "No transactions found in the bank statement. "
                    "Please ensure the PDF contains valid transaction data in a supported format. "
                    "Supported formats: State Bank of India statement with Date, Transaction Reference, and Balance columns."
                )

            # Save transactions to database
            transaction_count = self._save_transactions(dataframe)

            # Verify transactions were actually saved
            if transaction_count == 0:
                raise Exception("Failed to save transactions to database. No transactions were created.")

            # Clean up temporary files
            if decrypted_path and os.path.exists(decrypted_path):
                os.remove(decrypted_path)

            # Update status
            self.bank_statement.status = 'completed'
            self.bank_statement.processed_at = timezone.now()
            self.bank_statement.save()

            logger.info(f"Successfully processed bank statement: {self.bank_statement.id} with {transaction_count} transactions")
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

        # Find where transaction data starts by looking for the table header
        start_parsing = False

        for line_no, line in enumerate(lines):
            # Start parsing after we find the transaction table header
            if not start_parsing:
                if 'Date' in line and 'Transaction Reference' in line and 'Balance' in line:
                    start_parsing = True
                    if self.debug:
                        logger.debug(f"Start parsing at line {line_no}: {line}")
                # Date (Value Date) Narration Ref/Cheque No. Debit Credit Balance
                if 'Date' in line and 'Narration' in line and 'Balance' in line:
                    start_parsing = True
                    if self.debug:
                        logger.debug(f"Start parsing at line {line_no}: {line}")
                continue

            if self.debug:
                logger.debug(f"Parsing line {line_no}: {line}")

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

            if self.debug:
                logger.debug(f"Parsed transaction - Date: {date}, Ref: {trans_ref_text.strip()}, Balance: {match[4]}")

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

    def _extract_transactions_from_table(self, file_path: str) -> pd.DataFrame:
        """
        Middleware function to extract transactions from tables in PDF.
        Uses pdfplumber for proper table detection and extraction.
        This is a fallback when the text-based parsing fails.

        Note: Header is detected only once (usually on first page).
        Subsequent pages contain only data rows using the same column structure.
        """
        logger.info("Starting table extraction middleware...")

        if not PDFPLUMBER_AVAILABLE:
            logger.warning("pdfplumber not available, falling back to text-based table extraction")
            return self._extract_transactions_from_text_table(file_path)

        date_arr = []
        trans_ref_arr = []
        chq_ref_arr = []
        credit_arr = []
        debit_arr = []
        bal_arr = []

        # Column indices - set once when header is found
        date_col = None
        narration_col = None
        debit_col = None
        credit_col = None
        balance_col = None
        ref_col = None
        header_found = False

        try:
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"Processing {len(pdf.pages)} pages with pdfplumber")

                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract tables from the page
                    tables = page.extract_tables()

                    if not tables:
                        logger.debug(f"No tables found on page {page_num}")
                        continue

                    logger.info(f"Found {len(tables)} table(s) on page {page_num}")

                    for table_num, table in enumerate(tables, 1):
                        if not table:
                            continue

                        logger.debug(f"Processing table {table_num} on page {page_num}")

                        # If header not found yet, check if THIS table has the header
                        if not header_found:
                            # Look for header row in this table
                            has_transaction_header = False

                            for idx, row in enumerate(table):
                                if not row:
                                    continue

                                # Convert row to lowercase for comparison
                                row_lower = [str(cell).lower().strip() if cell else '' for cell in row]
                                print('==>', row_lower)

                                # Check if this row contains the transaction table headers
                                has_date = any(keyword in cell for cell in row_lower
                                                  for keyword in ['date', 'date (value date)'])
                                has_narration = any(keyword in cell for cell in row_lower
                                                  for keyword in ['narration', 'transaction', 'description', 'particulars'])
                                has_debit = any('debit' in cell or 'withdrawal' in cell for cell in row_lower)
                                has_credit = any('credit' in cell or 'deposit' in cell for cell in row_lower)
                                has_balance = any('balance' in cell for cell in row_lower)

                                # If we find at least 4 of these key columns, it's the transaction header
                                key_columns_found = sum([has_date, has_narration, has_debit, has_credit, has_balance])

                                if key_columns_found >= 4:
                                    header_row_index = idx
                                    logger.info(f"✓ Found transaction table header at row {idx} in table {table_num} on page {page_num}")
                                    logger.info(f"Header columns: {row}")

                                    # Find column indices from the header
                                    for col_idx, col_name in enumerate(row_lower):
                                        # if 'date' in col_name and 'value' not in col_name:
                                        #     date_col = col_idx
                                        if 'date' in col_name:
                                            date_col = col_idx
                                        elif 'transaction' in col_name or 'narration' in col_name or 'description' in col_name or 'particulars' in col_name:
                                            narration_col = col_idx
                                        elif 'debit' in col_name or 'withdrawal' in col_name:
                                            debit_col = col_idx
                                        elif 'credit' in col_name or 'deposit' in col_name:
                                            credit_col = col_idx
                                        elif 'balance' in col_name:
                                            balance_col = col_idx
                                        elif 'ref' in col_name or 'cheque' in col_name:
                                            ref_col = col_idx

                                    # Validate we have minimum required columns
                                    if date_col is not None and balance_col is not None:
                                        has_transaction_header = True
                                        header_found = True  # Set global flag - won't check any more tables
                                        logger.info(f"✓ Header detected! Column positions saved globally:")
                                        logger.info(f"  Date:{date_col}, Narration:{narration_col}, Debit:{debit_col}, Credit:{credit_col}, Balance:{balance_col}, Ref:{ref_col}")
                                        logger.info(f"  All subsequent tables will use this column structure")

                                        # Process remaining rows in this table (after header)
                                        start_row = header_row_index + 1
                                        for row_num, row in enumerate(table[start_row:], start_row + 1):
                                            self._process_transaction_row(
                                                row, row_num, page_num, table_num,
                                                date_col, narration_col, debit_col, credit_col, balance_col, ref_col,
                                                date_arr, trans_ref_arr, chq_ref_arr, credit_arr, debit_arr, bal_arr
                                            )
                                    else:
                                        logger.warning(f"Header-like row found but missing required columns (date or balance)")

                                    break  # Stop scanning this table

                            # If this table doesn't have transaction header, skip it
                            if not has_transaction_header:
                                logger.debug(f"Table {table_num} on page {page_num} is not a transaction table - skipping")
                                continue

                        else:
                            # Header already found in a previous table
                            # Process ALL rows in this table as data rows (no header check)
                            logger.info(f"✓ Processing data table {table_num} on page {page_num} (using saved column structure from earlier)")

                            for row_num, row in enumerate(table, 1):
                                self._process_transaction_row(
                                    row, row_num, page_num, table_num,
                                    date_col, narration_col, debit_col, credit_col, balance_col, ref_col,
                                    date_arr, trans_ref_arr, chq_ref_arr, credit_arr, debit_arr, bal_arr
                                )

        except Exception as e:
            logger.error(f"Error during table extraction: {str(e)}")
            # Fall back to text-based extraction
            return self._extract_transactions_from_text_table(file_path)

        # Create DataFrame
        df = pd.DataFrame({
            'date': date_arr,
            'transactionIdRef': trans_ref_arr,
            'chequeRefNo': chq_ref_arr,
            'credit': credit_arr,
            'debit': debit_arr,
            'balance': bal_arr
        })

        logger.info(f"Table extraction middleware found {len(df)} transactions")

        if len(df) > 0:
            logger.info(f"Sample transaction: {df.iloc[0].to_dict()}")

        return df

    def _process_transaction_row(self, row, row_num, page_num, table_num,
                                  date_col, narration_col, debit_col, credit_col, balance_col, ref_col,
                                  date_arr, trans_ref_arr, chq_ref_arr, credit_arr, debit_arr, bal_arr):
        """
        Helper method to process a single transaction row.
        Extracts date, narration, amounts and appends to arrays.
        """
        if not row or len(row) <= max(filter(None, [date_col, balance_col])):
            return

        try:
            # Extract date
            date_str = str(row[date_col]).strip() if row[date_col] else ''
            if not date_str or date_str.lower() in ['none', '']:
                return

            # Parse date - handle multiple formats
            # Format 1: DD-MM-YY or DD/MM/YY
            date_match = re.search(r'(\d{2})[/-](\d{2})[/-](\d{2,4})', date_str)

            # Format 2: DD-Mon-YY (e.g., 04-Mar-25)
            if not date_match:
                date_match = re.search(r'(\d{2})-([A-Za-z]{3})-(\d{2,4})', date_str)
                if date_match:
                    day, month_str, year = date_match.groups()
                    # Convert month name to number
                    month_map = {
                        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
                        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
                        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
                    }
                    month = month_map.get(month_str.lower(), '01')
                    if len(year) == 2:
                        year = f"20{year}"
                    formatted_date = f"{year}-{month}-{day.zfill(2)}"
                else:
                    return  # Skip if no valid date
            else:
                day, month, year = date_match.groups()
                if len(year) == 2:
                    year = f"20{year}"
                formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            # Extract narration/transaction reference
            narration = ''
            if narration_col is not None and narration_col < len(row):
                narration = str(row[narration_col]).strip() if row[narration_col] else ''

            # Extract reference/cheque number
            chq_ref = ''
            if ref_col is not None and ref_col < len(row):
                chq_ref = str(row[ref_col]).strip() if row[ref_col] else ''
                # Clean up None/null values
                if chq_ref.lower() in ['none', 'null', '']:
                    chq_ref = ''

            # Extract amounts (clean up commas and handle None/empty)
            def clean_amount(value):
                if not value or str(value).lower() in ['none', 'null', '']:
                    return '0'
                # Remove commas and whitespace
                cleaned = str(value).replace(',', '').strip()
                # Remove any currency symbols
                cleaned = re.sub(r'[₹$€£]', '', cleaned)
                # Extract just the number
                match = re.search(r'(\d+\.?\d*)', cleaned)
                return match.group(1) if match else '0'

            debit = '0'
            if debit_col is not None and debit_col < len(row):
                debit = clean_amount(row[debit_col])

            credit = '0'
            if credit_col is not None and credit_col < len(row):
                credit = clean_amount(row[credit_col])

            balance = clean_amount(row[balance_col]) if balance_col < len(row) else '0'

            # Skip rows with invalid balance
            if balance == '0' or not balance:
                return

            # Add to arrays
            date_arr.append(formatted_date)
            trans_ref_arr.append(narration[:500] if narration else 'N/A')
            chq_ref_arr.append(chq_ref)
            credit_arr.append(credit)
            debit_arr.append(debit)
            bal_arr.append(balance)

            if self.debug:
                logger.debug(
                    f"Page {page_num}, Row {row_num}: Date={formatted_date}, "
                    f"Narration={narration[:50]}, Debit={debit}, Credit={credit}, Balance={balance}"
                )

        except Exception as e:
            logger.warning(f"Failed to parse row {row_num} on page {page_num}, table {table_num}: {str(e)}")

    def _extract_transactions_from_text_table(self, file_path: str) -> pd.DataFrame:
        """
        Fallback text-based table extraction when pdfplumber is not available.
        Extracts text first, then parses table structure from text.
        """
        logger.info("Using fallback text-based table extraction...")

        # Extract text from PDF
        text_content = self._convert_pdf_to_text(file_path)
        lines = text_content.split('\n')

        date_arr = []
        trans_ref_arr = []
        chq_ref_arr = []
        credit_arr = []
        debit_arr = []
        bal_arr = []

        header_found = False

        for line_no, line in enumerate(lines):
            line_lower = line.lower()

            # Look for table headers
            if not header_found:
                headers_present = sum([
                    'date' in line_lower,
                    'transaction' in line_lower or 'narration' in line_lower or 'description' in line_lower,
                    'debit' in line_lower,
                    'credit' in line_lower,
                    'balance' in line_lower
                ])

                if headers_present >= 3:
                    header_found = True
                    logger.info(f"Table header found at line {line_no}: {line}")
                    continue

            # Parse data rows
            if header_found:
                if not line.strip():
                    continue

                date_match = re.match(r'^(\d{2}[/-]\d{2}[/-]\d{2,4})', line.strip())

                if date_match:
                    try:
                        date_str = date_match.group(1)
                        date_parts = re.split(r'[/-]', date_str)

                        if len(date_parts) == 3:
                            day, month, year = date_parts
                            if len(year) == 2:
                                year = f"20{year}"

                            formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

                            # Extract amounts
                            amounts = re.findall(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', line)
                            amounts = [amt.replace(',', '') for amt in amounts]

                            if len(amounts) >= 1:
                                balance = amounts[-1]
                                debit = '0'
                                credit = '0'

                                if len(amounts) >= 3:
                                    debit = amounts[-3]
                                    credit = amounts[-2]
                                elif len(amounts) == 2:
                                    if re.search(r'\bdr\b|\bdebit\b', line, re.IGNORECASE):
                                        debit = amounts[-2]
                                    else:
                                        credit = amounts[-2]

                                # Extract narration
                                line_without_date = line[date_match.end():].strip()
                                trans_ref = line_without_date
                                for amt in amounts:
                                    trans_ref = trans_ref.replace(amt, '').replace(',', '')
                                trans_ref = ' '.join(trans_ref.split())

                                # Extract cheque ref
                                chq_ref = ''
                                chq_match = re.search(r'\b(\d{6,})\b', trans_ref)
                                if chq_match:
                                    chq_ref = chq_match.group(1)

                                date_arr.append(formatted_date)
                                trans_ref_arr.append(trans_ref[:500])
                                chq_ref_arr.append(chq_ref)
                                credit_arr.append(credit)
                                debit_arr.append(debit)
                                bal_arr.append(balance)

                    except Exception as e:
                        logger.warning(f"Failed to parse line {line_no}: {str(e)}")
                        continue

        df = pd.DataFrame({
            'date': date_arr,
            'transactionIdRef': trans_ref_arr,
            'chequeRefNo': chq_ref_arr,
            'credit': credit_arr,
            'debit': debit_arr,
            'balance': bal_arr
        })

        logger.info(f"Text-based table extraction found {len(df)} transactions")
        return df

    def _save_transactions(self, dataframe: pd.DataFrame) -> int:
        """
        Save transactions to database and create expenses for debits.
        Returns the number of transactions saved.
        """
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

        # Bulk create transactions for better performance
        created_transactions = Transaction.objects.bulk_create(transactions)
        transaction_count = len(created_transactions)
        logger.info(f"Saved {transaction_count} transactions to database")

        # Create expenses for debit transactions
        expense_mapper = ExpenseCategoryMapper(self.bank_statement.user)
        expenses_created = 0

        for transaction in created_transactions:
            if transaction.debit > 0:
                expense = expense_mapper.create_expense_from_transaction(transaction)
                if expense:
                    expenses_created += 1

        logger.info(f"Created {expenses_created} expenses from {transaction_count} transactions")

        return transaction_count


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


class ExpenseCategoryMapper:
    """Service to categorize expenses based on transaction references"""

    def __init__(self, user):
        self.user = user
        # Cache categories for this user (default + user's custom)
        self._categories_cache = None

    def _get_categories(self):
        """Get all applicable categories (default + user custom)"""
        if self._categories_cache is None:
            from django.db.models import Q
            self._categories_cache = list(
                Category.objects.filter(
                    Q(is_default=True) | Q(user=self.user)
                ).order_by('-is_default', 'name')  # Prioritize user custom over default
            )
        return self._categories_cache

    def categorize_transaction(self, transaction_ref: str) -> Optional[Category]:
        """
        Match transaction reference against category keywords.
        Returns the first matching category (case-insensitive).
        """
        if not transaction_ref:
            return None

        transaction_ref_lower = transaction_ref.lower()

        for category in self._get_categories():
            for keyword in category.keywords:
                if keyword.lower() in transaction_ref_lower:
                    logger.debug(f"Matched category '{category.name}' with keyword '{keyword}'")
                    return category

        return None

    def extract_description(self, transaction_ref: str) -> str:
        """
        Extract clean description from transaction reference.
        Removes UPI/DR/ prefixes and cleans up the text.
        """
        if not transaction_ref:
            return "Unknown"

        # Remove common prefixes
        description = transaction_ref
        prefixes = ['UPI/DR/', 'UPI/CR/', 'NEFT*', 'CHQ TRFR FROM', 'ACHDr NACH']
        for prefix in prefixes:
            if description.startswith(prefix):
                description = description[len(prefix):]
                break

        # Extract merchant/payee name (usually first meaningful part)
        # Pattern: transaction_id/merchant_name/bank/...
        parts = description.split('/')
        if len(parts) >= 2:
            # Second part is usually merchant name
            merchant = parts[1].strip()
            if merchant:
                # Clean up merchant name
                merchant = merchant.replace('_', ' ').title()
                return merchant

        # Fallback: just clean up the first 100 chars
        description = description[:100].strip()
        return description if description else "Unknown"

    def create_expense_from_transaction(self, transaction: Transaction) -> Optional[Expense]:
        """
        Create an Expense record from a Transaction.
        Only for debit transactions (expenses).
        """
        # Only process debit transactions
        if transaction.debit <= 0:
            return None

        # Check if expense already exists
        if hasattr(transaction, 'expense'):
            logger.debug(f"Expense already exists for transaction {transaction.id}")
            return transaction.expense

        # Categorize
        category = self.categorize_transaction(transaction.transaction_id_ref)
        is_auto_categorized = category is not None

        # Extract description
        description = self.extract_description(transaction.transaction_id_ref)

        # Create expense
        expense = Expense.objects.create(
            transaction=transaction,
            user=transaction.user,
            category=category,
            amount=transaction.debit,
            date=transaction.date,
            description=description,
            is_auto_categorized=is_auto_categorized
        )

        logger.info(
            f"Created expense: {expense.id} - {description[:30]} - "
            f"₹{expense.amount} - Category: {category.name if category else 'Uncategorized'}"
        )

        return expense
