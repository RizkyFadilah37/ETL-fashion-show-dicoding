import os
import pandas as pd
from dotenv import load_dotenv
from utils.extract import run_extraction
from utils.transform import run_transformation
from utils.load import run_loading

def main():
    load_dotenv()
    print("=== Memulai ETL Pipeline ===")
    
    # Bikin folder otomatis kalau belum ada
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    raw_csv_path = "data/raw/products.csv"
    processed_csv_path = "data/processed/products.csv"
    
    # ==========================================
    # 1. EXTRACT
    # ==========================================
    print("\n[1] FASE EXTRACT")
    raw_data = run_extraction()
    
    if raw_data:
        # Simpan hasil scraping jadi CSV ke data/raw/
        pd.DataFrame(raw_data).to_csv(raw_csv_path, index=False)
        print(f"Data mentah berhasil disimpan di: {raw_csv_path}")
    else:
        print("Gagal mengekstrak data. Pipeline berhenti.")
        return

    # ==========================================
    # 2. TRANSFORM
    # ==========================================
    print("\n[2] FASE TRANSFORM")
    # Fungsi transform sekarang ngebaca dari file raw, dan nyimpen ke file processed
    status_transform = run_transformation(raw_csv_path, processed_csv_path)
    
    if not status_transform:
        print("Transformasi gagal. Pipeline berhenti.")
        return

    # ==========================================
    # 3. LOAD
    # ==========================================
    print("\n[3] FASE LOAD")
    GSHEETS_JSON = os.getenv("GSHEETS_CREDENTIAL_FILE")
    GSHEETS_NAME = os.getenv("GSHEETS_SPREADSHEET_NAME")
    
    DB_USER = os.getenv("DB_USERNAME")
    DB_PASS = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # Fungsi load sekarang tinggal ngebaca file yang ada di folder processed
    run_loading(processed_csv_path, GSHEETS_JSON, GSHEETS_NAME, DB_URL)
    
    print("\n=== ETL Pipeline Selesai ===")

if __name__ == "__main__":
    main()