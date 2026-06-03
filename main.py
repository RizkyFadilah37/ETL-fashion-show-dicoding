import os
import pandas as pd
from dotenv import load_dotenv
from utils.extract import run_extraction
from utils.transform import run_transformation
from utils.load import run_loading

def main():
    """Orchestrator ETL pipeline: Extract → Transform → Load."""
    load_dotenv()
    print("=== Starting ETL Pipeline ===")

    # Create folders if they do not exist
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    
    raw_csv_path = "data/raw/products.csv"
    processed_csv_path = "data/processed/products.csv"
    
    # ==========================================
    # 1. EXTRACT
    # ==========================================
    print("\n[1] PHASE: EXTRACT")
    raw_data = run_extraction()
    
    if raw_data:
        # Simpan hasil scraping jadi CSV ke data/raw/
        pd.DataFrame(raw_data).to_csv(raw_csv_path, index=False)
        print(f"Raw data successfully saved to: {raw_csv_path}")
    else:
        print("Failed to extract data. Pipeline stopped.")
        return

    # ==========================================
    # 2. TRANSFORM
    # ==========================================
    print("\n[2] PHASE: TRANSFORM")
    # The transform function reads from the raw file and writes to the processed file
    status_transform = run_transformation(raw_csv_path, processed_csv_path)
    
    if not status_transform:
        print("Transformation failed. Pipeline stopped.")
        return

    # ==========================================
    # 3. LOAD
    # ==========================================
    print("\n[3] PHASE: LOAD")
    GSHEETS_JSON = os.getenv("GSHEETS_CREDENTIAL_FILE")
    GSHEETS_NAME = os.getenv("GSHEETS_SPREADSHEET_NAME")
    
    DB_USER = os.getenv("DB_USERNAME")
    DB_PASS = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # The load orchestrator reads the processed file and loads to targets
    run_loading(processed_csv_path, GSHEETS_JSON, GSHEETS_NAME, DB_URL)
    
    print("\n=== ETL Pipeline Finished ===")

if __name__ == "__main__":
    main()