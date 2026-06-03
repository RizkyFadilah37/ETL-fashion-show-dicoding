import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import create_engine, exc as sa_exc
import psycopg2
from psycopg2 import sql as psql

def load_to_csv(df: pd.DataFrame, file_path: str = "products.csv") -> bool:
    """Save DataFrame to a CSV file. Returns True on success."""
    try:
        df.to_csv(file_path, index=False)
        print(f"[LOAD SUCCESS] Data saved to CSV: {file_path}")
        return True
    except Exception as e:
        print(f"[LOAD ERROR] Failed to save to CSV: {e}")
        return False

def load_to_gsheets(df: pd.DataFrame, credentials_file: str, sheet_name: str) -> bool:
    """Upload DataFrame to Google Sheets using a Service Account. Returns True on success."""
    try:
        # Define the scope for Google Sheets and Drive API
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Autentikasi menggunakan file JSON (Service Account)
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(creds)
        
        # Open the spreadsheet by name (ensure the Service Account email is invited as an Editor)
        sheet = client.open(sheet_name).sheet1

        # Clear the sheet before inserting new data
        sheet.clear()

        # Insert header (column names) and the data rows
        data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
        sheet.update(data_to_upload)
        
        print(f"[LOAD SUCCESS] Data saved to Google Sheets: {sheet_name}")
        return True
    except Exception as e:
        print(f"[LOAD ERROR] Failed to save to Google Sheets: {e}")
        return False

def load_to_postgres(df: pd.DataFrame, db_url: str, table_name: str = "fashion_products") -> bool:
    """Insert DataFrame into PostgreSQL. Auto-create DB if it does not exist. Returns True on success."""
    def _ensure_database_exists(db_url: str):
        """Create the target database if it does not exist."""
        try:
            from sqlalchemy.engine import make_url
            url = make_url(db_url)
            target_db = url.database
            if not target_db or target_db.lower() == 'postgres':
                return

            # Try connecting directly to target DB to see if it exists
            try:
                psycopg2.connect(dbname=target_db, user=url.username, password=url.password, host=url.host, port=url.port).close()
                return
            except psycopg2.OperationalError:
                # Connect to default DB to create the target one
                default_db = 'postgres'
                conn = psycopg2.connect(dbname=default_db, user=url.username, password=url.password, host=url.host, port=url.port)
                conn.autocommit = True
                cur = conn.cursor()
                try:
                    cur.execute(psql.SQL("CREATE DATABASE {};").format(psql.Identifier(target_db)))
                    print(f"[LOAD INFO] Database '{target_db}' created automatically.")
                finally:
                    cur.close()
                    conn.close()
        except Exception as e:
            print(f"[LOAD ERROR] Failed to ensure database exists: {e}")
            raise

    try:
        # Ensure DB exists (create if needed)
        _ensure_database_exists(db_url)

        # Create SQLAlchemy engine
        engine = create_engine(db_url)

        # Push data to the table (if table exists it will be replaced)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"[LOAD SUCCESS] Data saved to PostgreSQL (table: {table_name})")
        return True
    except sa_exc.OperationalError as oe:
        print(f"[LOAD ERROR] Failed to save to PostgreSQL (OperationalError): {oe}")
        return False
    except Exception as e:
        print(f"[LOAD ERROR] Failed to save to PostgreSQL: {e}")
        return False

def run_loading(data_or_path, gsheets_json: str, sheet_name: str, db_url: str):
    """Orchestrator for loading: save to CSV, GSheets, and PostgreSQL. Accepts DataFrame or CSV path."""
    print("\n--- Starting Load Process (Target: Advanced) ---")

    # if data_or_path is a string, treat it as a CSV path; if it's a DataFrame, use it directly; otherwise, error
    df = None
    try:
        if isinstance(data_or_path, str):
            df = pd.read_csv(data_or_path)
        elif isinstance(data_or_path, pd.DataFrame):
            df = data_or_path
        else:
            print("[LOAD ERROR] First parameter must be a CSV path or a pandas.DataFrame")
            return
    except Exception as e:
        print(f"[LOAD ERROR] Failed to read input data: {e}")
        return

    if df is None or df.empty:
        print("Empty data, load process canceled.")
        return

    # 1. Load to CSV
    load_to_csv(df, "products.csv")

    # 2. Load to Google Sheets
    load_to_gsheets(df, gsheets_json, sheet_name)

    # 3. Load to PostgreSQL
    load_to_postgres(df, db_url)