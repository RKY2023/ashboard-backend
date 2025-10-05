# Expense Management System

## Overview
Automated expense tracking system that extracts expenses from bank statement transactions and categorizes them using keyword matching.

## Models

### Category
Stores expense categories with keyword-based matching.

**Fields:**
- `name`: Category name (e.g., "Grocery", "Travel")
- `keywords`: JSON array of keywords for auto-categorization
- `icon`: Emoji/icon for UI display
- `color`: Hex color code for UI
- `user`: FK to User (null for default categories)
- `is_default`: Boolean for system-wide categories

**Default Categories:**
1. Grocery (🛒) - bigbasket, bbnow, zepto, etc.
2. Travel (🚗) - uber, rapido, ola, etc.
3. Food (🍔) - zomato, swiggy, restaurant, etc.
4. Rent (🏠) - rent
5. Shopping (🛍️) - amazon, flipkart, myntra, etc.
6. Utilities (💡) - electricity, water, recharge, etc.
7. Entertainment (🎬) - netflix, prime, spotify, etc.
8. Personal Transfer (💸) - person names, share, payment
9. Healthcare (🏥) - medical, hospital, pharmacy, etc.
10. Miscellaneous (📦) - other, misc

### Expense
Auto-created from Transaction records with debit > 0.

**Fields:**
- `transaction`: OneToOne to Transaction
- `user`: FK to User
- `category`: FK to Category (nullable)
- `amount`: Decimal (same as transaction.debit)
- `date`: Date (same as transaction.date)
- `description`: Cleaned transaction reference
- `notes`: User's custom notes
- `is_auto_categorized`: Boolean
- `is_recurring`: Boolean
- `tags`: JSON array

## API Endpoints

### Categories
- `GET /expenses/categories/` - List all categories (default + user's custom)
- `POST /expenses/categories/` - Create custom category
- `GET /expenses/categories/{id}/` - Get category details
- `PATCH /expenses/categories/{id}/` - Update category
- `DELETE /expenses/categories/{id}/` - Delete custom category
- `GET /expenses/categories/stats/` - Category statistics with expense counts

### Expenses
- `GET /expenses/expenses/` - List all expenses
  - Query params: `category`, `date`, `min_amount`, `max_amount`, `is_recurring`
- `GET /expenses/expenses/{id}/` - Get expense details
- `PATCH /expenses/expenses/{id}/` - Update category/notes/tags
- `GET /expenses/expenses/summary/` - Get summary (total, avg, category breakdown)
  - Query params: `start_date`, `end_date`, `category`
- `GET /expenses/expenses/by_month/?year=2025` - Monthly expense breakdown
- `GET /expenses/expenses/by_category/` - Category-wise breakdown
  - Query params: `start_date`, `end_date`
- `GET /expenses/expenses/recurring/` - List recurring expenses
- `GET /expenses/expenses/uncategorized/` - List uncategorized expenses
- `GET /expenses/expenses/export/?format=excel` - Export expenses to Excel file
- `GET /expenses/expenses/export/?format=csv` - Export expenses to CSV file
  - Supports all filtering parameters (category, date, min_amount, max_amount, etc.)
  - Excel: Formatted file with styled headers and summary row
  - CSV: Plain text file with comma-separated values
- `GET /expenses/expenses/export_excel/` - Legacy Excel export (deprecated, use `/export/?format=excel`)

## Auto-Categorization

The `ExpenseCategoryMapper` service automatically:
1. Matches transaction references against category keywords (case-insensitive)
2. Extracts clean description from UPI/NEFT references
3. Creates Expense records when transactions are saved

**Matching Priority:**
- User's custom categories are checked first
- Then default categories
- First matching keyword wins

## Management Commands

### Seed Default Categories
```bash
python manage.py seed_categories
```
Creates/updates 10 default categories with predefined keywords.

### Backfill Expenses
```bash
python manage.py backfill_expenses [--user-id USER_ID]
```
Creates expense records from existing transactions (debit only).

## Workflow

1. **Upload Bank Statement** → PDF uploaded via API
2. **Process Statement** → Transactions extracted
3. **Auto-Create Expenses** → For each debit transaction:
   - Extract clean description
   - Match against category keywords
   - Create Expense record
4. **Manual Categorization** → User can update category via PATCH API
5. **Analytics** → Use summary/by_month/by_category endpoints

## Example Usage

### Get Monthly Expenses
```
GET /expenses/expenses/by_month/?year=2025
```

### Get Category Breakdown
```
GET /expenses/expenses/by_category/?start_date=2025-08-01&end_date=2025-08-31
```

### Update Expense Category
```
PATCH /expenses/expenses/123/
{
  "category": 5,
  "notes": "Office lunch",
  "is_recurring": true
}
```

### Export to Excel or CSV
```
# Export as Excel (default)
GET /expenses/expenses/export/
GET /expenses/expenses/export/?format=excel

# Export as CSV
GET /expenses/expenses/export/?format=csv

# With filters
GET /expenses/expenses/export/?format=excel&category=1&start_date=2025-08-01&end_date=2025-08-31
GET /expenses/expenses/export/?format=csv&min_amount=1000&is_recurring=true
```

**Excel Export Features:**
- Formatted headers (blue background, white text)
- All expense data (Date, Description, Amount, Category, Notes, Tags, etc.)
- Auto-adjusted column widths
- Total amount summary row
- Proper number formatting for amounts
- File: `expenses_{start_date}_to_{end_date}.xlsx`

**CSV Export Features:**
- Plain text format
- Comma-separated values
- All expense data (same fields as Excel)
- Total amount summary row
- File: `expenses_{start_date}_to_{end_date}.csv`
- Easy to import into spreadsheet applications

### Get Expense Summary
```
GET /expenses/expenses/summary/?start_date=2025-08-01&end_date=2025-08-31
```

Response:
```json
{
  "total_amount": 50000.00,
  "expense_count": 75,
  "avg_amount": 666.67,
  "category_breakdown": [
    {
      "category__name": "Grocery",
      "total": 5000.00,
      "count": 13
    },
    ...
  ],
  "uncategorized_count": 15
}
```

## Database Indexes
- User + Date (for filtering by user and date range)
- Category (for category-wise queries)
- Date (for chronological sorting)
- is_recurring (for recurring expense queries)
