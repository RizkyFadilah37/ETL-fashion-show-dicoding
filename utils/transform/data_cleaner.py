import pandas as pd

def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan kolom Price:
    - Menghapus simbol '$' dan koma.
    - Mengonversi tipe data menjadi numerik.
    - Mengonversi mata uang (dikali Rp16.000).
    """
    # Hapus simbol '$' dan koma
    df['Price'] = df['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    
    # Konversi ke numerik (ubah yang gagal jadi NaN)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    
    # Konversi ke Rupiah
    df['Price'] = df['Price'] * 16000
    
    return df

def clean_rating(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan kolom Rating:
    - Menghapus baris yang berisi "Invalid Rating".
    - Menghapus simbol bintang '⭐' dan teks ' / 5'.
    - Mengubah tipe data menjadi float.
    """
    # Filter data yang bertuliskan "Invalid"
    df = df[~df['Rating'].astype(str).str.contains('Invalid', case=False, na=False)]
    
    # Bersihkan teks
    df['Rating'] = df['Rating'].astype(str).str.replace('Rating:', '', case=False)
    df['Rating'] = df['Rating'].str.replace('⭐', '', regex=False)
    df['Rating'] = df['Rating'].str.split('/').str[0].str.strip() # Mengambil angka sebelum '/'
    
    # Konversi ke float
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    
    return df

def clean_colors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan kolom Colors:
    - Menghapus teks " Colors".
    - Mengonversi tipe data menjadi integer (angka saja).
    """
    df['Colors'] = df['Colors'].astype(str).str.replace('Colors', '', case=False).str.strip()
    df['Colors'] = pd.to_numeric(df['Colors'], errors='coerce').astype('Int64') # Int64 support NaN sementara
    return df

def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membersihkan kolom Size dan Gender:
    - Menghapus awalan teks "Size: " dan "Gender: ".
    - Memastikan tipe data string.
    """
    df['Size'] = df['Size'].astype(str).str.replace('Size:', '', case=False).str.strip()
    df['Gender'] = df['Gender'].astype(str).str.replace('Gender:', '', case=False).str.strip()
    return df

def clean_general_rules(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menjalankan aturan general (basic):
    - Hapus produk yang bernama "Unknown Product".
    - Hapus data duplikat.
    - Hapus data yang bernilai null (NaN).
    """
    # Hapus invalid data di Title
    df = df[df['Title'] != 'Unknown Product']
    
    # Drop duplicates
    df = df.drop_duplicates()
    
    # Drop null values (termasuk NaN hasil dari pd.to_numeric yang gagal)
    df = df.dropna()
    
    return df

def _transform_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Internal helper: jalankan pipeline pembersihan pada DataFrame.
    """
    try:
        # Jika data kosong dari awal, langsung kembalikan dataframe kosong
        if df.empty:
            return df

        # Panggil fungsi-fungsi modular secara berurutan
        df = clean_price(df)
        df = clean_rating(df)
        df = clean_colors(df)
        df = clean_text_columns(df)

        # Panggil pembersihan general (Null & Duplikat) paling akhir
        df = clean_general_rules(df)

        # Reset index setelah banyak baris yang dihapus
        df = df.reset_index(drop=True)

        return df

    except Exception as e:
        print(f"[TRANSFORM ERROR] Gagal melakukan transformasi data: {e}")
        return pd.DataFrame()


def run_transformation(raw_csv_path: str, processed_csv_path: str) -> bool:
    """
    Fungsi publik yang sesuai dengan `main.py`:
    - Membaca `raw_csv_path` sebagai CSV
    - Menjalankan pipeline transformasi
    - Menyimpan hasil ke `processed_csv_path`
    Mengembalikan True jika berhasil, False jika gagal.
    """
    try:
        # Baca CSV mentah
        df_raw = pd.read_csv(raw_csv_path)

        # Transformasi
        df_processed = _transform_df(df_raw)

        # Jika hasil kosong, anggap transformasi gagal
        if df_processed.empty:
            print("Transformasi menghasilkan DataFrame kosong.")
            return False

        # Simpan hasil ke CSV processed
        df_processed.to_csv(processed_csv_path, index=False)
        print(f"Data tertransformasi berhasil disimpan di: {processed_csv_path}")
        return True

    except Exception as e:
        print(f"[TRANSFORM ERROR] Gagal melakukan transformasi (file): {e}")
        return False

# --- Buat test jalanin manual ---
if __name__ == "__main__":
    # Dummy data buat ngetes transformasinya jalan atau ngga
    dummy_raw_data = [
        {"Title": "T-Shirt Keren", "Price": "$10.50", "Rating": "⭐ 4.8 / 5", "Colors": "3 Colors", "Size": "Size: L", "Gender": "Gender: Men", "timestamp": "2023-10-27"},
        {"Title": "Unknown Product", "Price": "$0.00", "Rating": "Invalid Rating / 5", "Colors": "0 Colors", "Size": "Size: M", "Gender": "Gender: Women", "timestamp": "2023-10-27"},
        {"Title": "Jaket", "Price": "$20", "Rating": "⭐ 4.5 / 5", "Colors": "2 Colors", "Size": "Size: XL", "Gender": "Gender: Unisex", "timestamp": "2023-10-27"},
        {"Title": "Jaket", "Price": "$20", "Rating": "⭐ 4.5 / 5", "Colors": "2 Colors", "Size": "Size: XL", "Gender": "Gender: Unisex", "timestamp": "2023-10-27"} # Duplikat
    ]
    
    hasil_df = run_transformation(dummy_raw_data)
    print("Hasil Transformasi:")
    print(hasil_df)
    print("\nTipe Data:")
    print(hasil_df.dtypes)