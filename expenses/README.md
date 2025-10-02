# Bank Statement Expenses Service

This Django app provides automated processing of bank statement PDFs, extracting transaction data and storing it in the database.

## Features

- **PDF Upload & Storage**: Upload encrypted or unencrypted bank statement PDFs
- **Auto Decryption**: Automatically decrypt password-protected PDFs using stored keys
- **Transaction Extraction**: Parse transaction data from PDF text
- **REST API**: Full REST API for managing statements and transactions
- **User Isolation**: Each user only sees their own statements and transactions

## Models

### BankStatement
Stores uploaded bank statement PDFs and their processing status.

### Transaction
Stores individual transactions extracted from bank statements.

### DecryptionKey
Stores PDF decryption passwords (admin only).

## API Endpoints

### Bank Statements
- `GET /expenses/bank-statements/` - List all user's statements
- `POST /expenses/bank-statements/upload/` - Upload a new PDF
- `POST /expenses/bank-statements/{id}/process/` - Process a statement
- `GET /expenses/bank-statements/{id}/transactions/` - Get transactions for a statement
- `GET /expenses/bank-statements/stats/` - Get processing statistics

### Transactions
- `GET /expenses/transactions/` - List all user's transactions
- `GET /expenses/transactions/{id}/` - Get transaction details
- `GET /expenses/transactions/summary/` - Get transaction summary (with date filters)
- `GET /expenses/transactions/by_month/?year=2024` - Get monthly breakdown

### Decryption Keys (Admin only)
- `GET /expenses/decryption-keys/` - List all keys
- `POST /expenses/decryption-keys/` - Add a new key

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py makemigrations expenses
python manage.py migrate
```

### 3. Add Decryption Keys (if using encrypted PDFs)
Via Django admin or API:
```python
from expenses.models import DecryptionKey
DecryptionKey.objects.create(key="your-pdf-password", description="Main password", is_active=True)
```

### 4. Create Media Directory
```bash
mkdir media
```

## Usage

### Upload and Process a Statement

1. **Upload a PDF**:
```bash
curl -X POST http://localhost:8000/expenses/bank-statements/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@statement.pdf"
```

Response:
```json
{
  "id": 1,
  "message": "Bank statement uploaded successfully",
  "status": "pending"
}
```

2. **Process the Statement**:
```bash
curl -X POST http://localhost:8000/expenses/bank-statements/1/process/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **View Transactions**:
```bash
curl http://localhost:8000/expenses/transactions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Migration from Original Script

The original `monthly_BOP.py` script has been refactored into this Django service with the following improvements:

### Key Changes:
1. **Hardcoded Paths Removed**: Now uses Django's MEDIA_ROOT
2. **Database Integration**: Uses Django ORM instead of pymysql
3. **User Isolation**: Each user only sees their own data
4. **REST API**: Full REST API instead of CLI
5. **Error Handling**: Better error handling and logging
6. **File Management**: Uses Django's file storage backend
7. **Configuration**: Settings moved to Django settings/environment variables

### Original Functions Mapping:
- `notepad2data()` → `BankStatementProcessorService._parse_transactions_from_text()`
- `decryptPDF()` → `BankStatementProcessorService._decrypt_pdf()`
- `convertPDFtoTXT()` → `BankStatementProcessorService._convert_pdf_to_text()`
- `insertDataFrameToDatabase()` → `BankStatementProcessorService._save_transactions()`
- `generatefilelocation()` → Replaced by Django file upload handling

## Configuration

Add to your Django settings:
```python
# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Bank Statement Processing
BANK_STATEMENT_DEBUG = DEBUG  # Enable debug logging
```

## Notes

- The service expects bank statement PDFs in a specific format (Bank of Punjab format based on original script)
- For different bank formats, you'll need to modify the parsing logic in `_parse_transactions_from_text()`
- Decryption keys are stored in the database (make sure to secure your database)
- Processing is currently synchronous - for production, consider using Celery for async processing

## Future Enhancements

- [ ] Add Celery for async processing
- [ ] Support multiple bank statement formats
- [ ] Add export functionality (CSV, Excel)
- [ ] Add transaction categorization
- [ ] Add analytics and reporting
- [ ] Add duplicate detection
