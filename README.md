# ETL Pipeline - Fashion Competitor

ETL (Extract, Transform, Load) pipeline for scraping and processing fashion competitor data, with outputs to CSV, Google Sheets, and PostgreSQL.

## Project Structure

```
.
├── main.py                 # Entry point for the ETL pipeline
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (DB, GSheets credentials)
├── google-sheets-api.json  # Service account JSON for GSheets
├── data/
│   ├── raw/               # Raw scraped data (CSV)
│   └── processed/         # Transformed data (CSV)
├── utils/
│   ├── extract/           # Extraction modules
│   │   ├── __init__.py
│   │   └── web_scraper.py
│   ├── transform/         # Transformation modules
│   │   ├── __init__.py
│   │   └── data_cleaner.py
│   └── load/              # Loading modules
│       ├── __init__.py
│       └── db_loader.py
└── tests/                 # Unit tests (coverage ~91%)
    ├── test_extract.py
    ├── test_transform.py
    ├── test_load.py
    ├── test_db_loader_extra.py
    └── test_web_scraper_extra.py
```

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure `.env`

```
DB_USERNAME=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432
DB_NAME=fashion_db

GSHEETS_CREDENTIAL_FILE=google-sheets-api.json
GSHEETS_SPREADSHEET_NAME=Fashion Competitor Data
```

The `fashion_db` database will be created automatically when the pipeline runs if it does not exist.

### 3. Run the Pipeline

```bash
python main.py
```

Outputs will be stored in:
- `data/raw/products.csv` - Raw scraped data
- `data/processed/products.csv` - Transformed data
- `products.csv` - Final export
- Google Sheets - Auto-updated
- PostgreSQL - Table `fashion_products`

## ETL Pipeline

### Phase 1: EXTRACT (`utils/extract/web_scraper.py`)
Scrapes multiple pages from the target fashion website using BeautifulSoup. Extracted fields: Title, Price, Rating, Colors, Size, Gender, timestamp.

### Phase 2: TRANSFORM (`utils/transform/data_cleaner.py`)
Clean and normalize data:
- Price: remove `$`, convert to Rupiah (×16,000)
- Rating: filter invalid values, convert to float
- Colors: convert to integer
- General rules: drop "Unknown Product", duplicates, and NaN

### Phase 3: LOAD (`utils/load/db_loader.py`)
Store data into three targets: CSV, Google Sheets, and PostgreSQL (auto-create DB if needed).

## Testing & Coverage

```bash
# Run tests
pytest -q

# Coverage check (target ≥80%)
pytest --cov=utils --cov-report=term-missing -q
```

**Coverage Results:**
- `utils/extract/web_scraper.py`: 93%
- `utils/transform/data_cleaner.py`: 82%
- `utils/load/db_loader.py`: 95%
- **Total: 91%**

## Viewing Data

### PostgreSQL

**Method 1: Python + Pandas (Recommended)**

```bash
python -c "import pandas as pd; from sqlalchemy import create_engine; engine=create_engine('postgresql://postgres:admin@localhost:5432/fashion_db'); print(pd.read_sql('SELECT * FROM fashion_products LIMIT 10', engine))"
```

**Method 2: psql CLI**

```bash
psql -U postgres -h localhost -d fashion_db
# Then run: SELECT * FROM fashion_products LIMIT 10;
```

Useful SQL queries:

```sql
SELECT COUNT(*) FROM fashion_products;
SELECT * FROM fashion_products LIMIT 20;
SELECT AVG("Price") FROM fashion_products;
SELECT * FROM fashion_products ORDER BY "Price" DESC LIMIT 10;
```

### Google Sheets
Spreadsheet: https://docs.google.com/spreadsheets/d/1N8nqF0JyedSkSxsBMMxNT91eQNVKzPqHvvieyDPBDk0/edit?usp=sharing

Sheet "Sheet1" contains columns: Title, Price, Rating, Colors, Size, Gender, timestamp

## Notes for Review

### Expected Behavior
- Each `python main.py` run scrapes the latest data → database contents will update accordingly
- Tests are deterministic because they use mocks & temporary files (not a real DB)
- The `fashion_products` table is replaced (not appended) on each run

### Verify Project

```bash
pytest -q
pytest --cov=utils --cov-report=term-missing -q
python main.py
# Verify: CSV files, Google Sheets, PostgreSQL
```

### Google Sheets Requirements
- The spreadsheet must be shared with "Anyone with the link" as EDITOR
- The file `google-sheets-api.json` must be present (service account credentials)
- Data will be updated automatically when the pipeline runs

### Reset Database (Optional)

```python
from sqlalchemy import create_engine, text
engine = create_engine('postgresql://postgres:admin@localhost:5432/fashion_db')
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS fashion_products'))
    conn.commit()
print('Database reset')
```

## Dependencies

```
pandas
requests
beautifulsoup4
sqlalchemy
psycopg2-binary
gspread
oauth2client
python-dotenv
pytest
pytest-cov
```

## Troubleshooting

| Error | Solution |
|-------|---------|
| Database error | Ensure PostgreSQL is running and the `postgres` user has CREATE DATABASE privilege |
| Google Sheets error | Ensure `google-sheets-api.json` exists and the spreadsheet is shared with EDITOR access |
| Import error `utils.*` | Run from project root: `cd submission-pemda && python main.py` |
| `psql` not found | Add `C:\\Program Files\\PostgreSQL\\<version>\\bin` to Windows PATH |

## Notes

- Website target: `https://fashion-studio.dicoding.dev`
- Default: scrape 50 pages (configurable in `run_extraction()`)
- Duplicates & NaN are removed during transform
- Database is auto-created if missing
- All load operations replace existing data (not append)

## Author

ETL Pipeline Project - Dicoding
