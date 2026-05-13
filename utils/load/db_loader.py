import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import create_engine, exc as sa_exc
import psycopg2
from psycopg2 import sql as psql

def load_to_csv(df: pd.DataFrame, file_path: str = "products.csv") -> bool:
    """
    Menyimpan data ke format Flat File (CSV).
    """
    try:
        df.to_csv(file_path, index=False)
        print(f"[LOAD SUCCESS] Data berhasil disimpan ke CSV: {file_path}")
        return True
    except Exception as e:
        print(f"[LOAD ERROR] Gagal menyimpan ke CSV: {e}")
        return False

def load_to_gsheets(df: pd.DataFrame, credentials_file: str, sheet_name: str) -> bool:
    """
    Menyimpan data ke Google Sheets menggunakan Service Account API.
    Pastikan file credentials JSON sudah dilampirkan di folder submission.
    """
    try:
        # Menentukan scope untuk akses Google Drive dan Google Sheets
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Autentikasi menggunakan file JSON (Service Account)
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(creds)
        
        # Membuka Spreadsheet berdasarkan nama file (pastikan Service Account email sudah di-invite sebagai Editor)
        sheet = client.open(sheet_name).sheet1
        
        # Bersihkan sheet sebelum diisi data baru
        sheet.clear()
        
        # Masukkan header (nama kolom) dan isi datanya
        data_to_upload = [df.columns.values.tolist()] + df.values.tolist()
        sheet.update(data_to_upload)
        
        print(f"[LOAD SUCCESS] Data berhasil disimpan ke Google Sheets: {sheet_name}")
        return True
    except Exception as e:
        print(f"[LOAD ERROR] Gagal menyimpan ke Google Sheets: {e}")
        return False

def load_to_postgres(df: pd.DataFrame, db_url: str, table_name: str = "fashion_products") -> bool:
    """
    Menyimpan data ke Database PostgreSQL.
    """
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
                    print(f"[LOAD INFO] Database '{target_db}' dibuat otomatis.")
                finally:
                    cur.close()
                    conn.close()
        except Exception as e:
            print(f"[LOAD ERROR] Gagal memastikan database ada: {e}")
            raise

    try:
        # Ensure DB exists (create if needed)
        _ensure_database_exists(db_url)

        # Membuat koneksi engine menggunakan SQLAlchemy
        engine = create_engine(db_url)

        # Push data ke tabel (jika tabel sudah ada, akan ditimpa/replace)
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        print(f"[LOAD SUCCESS] Data berhasil disimpan ke PostgreSQL (tabel: {table_name})")
        return True
    except sa_exc.OperationalError as oe:
        print(f"[LOAD ERROR] Gagal menyimpan ke PostgreSQL (OperationalError): {oe}")
        return False
    except Exception as e:
        print(f"[LOAD ERROR] Gagal menyimpan ke PostgreSQL: {e}")
        return False

def run_loading(data_or_path, gsheets_json: str, sheet_name: str, db_url: str):
    """
    Fungsi orkestrator untuk proses penyimpanan ke 3 repositori.

    Parameter `data_or_path` dapat berupa `pandas.DataFrame` atau path ke CSV (str).
    """
    print("\n--- Memulai Proses Load (Target: Advanced) ---")

    # Jika diberikan path string, coba baca CSV
    df = None
    try:
        if isinstance(data_or_path, str):
            df = pd.read_csv(data_or_path)
        elif isinstance(data_or_path, pd.DataFrame):
            df = data_or_path
        else:
            print("[LOAD ERROR] Parameter pertama harus path CSV atau pandas.DataFrame")
            return
    except Exception as e:
        print(f"[LOAD ERROR] Gagal membaca input data: {e}")
        return

    if df is None or df.empty:
        print("Data kosong, proses Load dibatalkan.")
        return

    # 1. Load ke CSV
    load_to_csv(df, "products.csv")

    # 2. Load ke Google Sheets
    load_to_gsheets(df, gsheets_json, sheet_name)

    # 3. Load ke PostgreSQL
    load_to_postgres(df, db_url)