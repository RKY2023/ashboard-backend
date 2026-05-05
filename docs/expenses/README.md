# Expenses Module

App: `expenses`. Mounted at `/expenses/`.

End-to-end flow: upload a bank statement PDF → parse transactions → derive expenses → categorise.

## Models (`expenses/models.py`)

| Model | Purpose |
|---|---|
| `BankStatement` | Uploaded PDF metadata: `file`, `original_filename`, `is_encrypted`, processing `status` (`pending`/`processing`/`completed`/`failed`), `error_message`, `processed_at`. |
| `Transaction` | Parsed row from a statement: `date`, `transaction_id_ref`, `cheque_ref_no`, `credit`, `debit`, `balance`. Linked to its parent `BankStatement`. |
| `DecryptionKey` | Stored keys used to unlock password-protected PDFs. Active keys (`is_active=True`) are tried during parsing. |
| `Category` | Expense category with keyword list (`keywords` JSON). System-wide defaults have `is_default=True`; user-owned have a `user` FK. |
| `Expense` | One-to-one with a debit `Transaction`. Carries `category`, `amount`, `date`, `description`, `notes`, `is_auto_categorized`, `is_recurring`, `tags`. |

## Endpoints

Registered via `DefaultRouter` (see `expenses/urls.py`):

| Resource | Path |
|---|---|
| Bank statements | `/expenses/bank-statements/` |
| Transactions | `/expenses/transactions/` |
| Decryption keys | `/expenses/decryption-keys/` |
| Categories | `/expenses/categories/` |
| Expenses | `/expenses/expenses/` |

## Statement processing

PDF parsing logic lives in `expenses/services.py` (currently being iterated on). Toggle verbose logging with `BANK_STATEMENT_DEBUG` in `blogs/settings.py` (defaults to `DEBUG`).

Recent change: periodic statement support and a new `Transaction` table backing PDF imports (commit `a48cf57`).
