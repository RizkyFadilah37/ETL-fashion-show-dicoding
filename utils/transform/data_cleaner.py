import pandas as pd

def clean_price(df: pd.DataFrame) -> pd.DataFrame:
    """Clean price: remove $, convert to numeric, multiply to convert to Rupiah (×16,000)."""
    # Remove '$' symbol and commas
    df['Price'] = df['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    
    # Convert to numeric (change failed conversions to NaN)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    
    # Convert to Rupiah
    df['Price'] = df['Price'] * 16000
    
    return df

def clean_rating(df: pd.DataFrame) -> pd.DataFrame:
    """Clean rating: remove 'Invalid' markers and star symbols, convert to float."""
    # Filter out rows where Rating contains 'Invalid'
    df = df[~df['Rating'].astype(str).str.contains('Invalid', case=False, na=False)]
    
    # Clean text
    df['Rating'] = df['Rating'].astype(str).str.replace('Rating:', '', case=False)
    df['Rating'] = df['Rating'].str.replace('⭐', '', regex=False)
    df['Rating'] = df['Rating'].str.split('/').str[0].str.strip() # Take the number before '/'
    
    # Convert to float
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    
    return df

def clean_colors(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the Colors column: remove 'Colors' text and convert to integer."""
    df['Colors'] = df['Colors'].astype(str).str.replace('Colors', '', case=False).str.strip()
    df['Colors'] = pd.to_numeric(df['Colors'], errors='coerce').astype('Int64') # Int64 supports NA
    return df

def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Clean Size and Gender columns: remove 'Size:' and 'Gender:' prefixes."""
    df['Size'] = df['Size'].astype(str).str.replace('Size:', '', case=False).str.strip()
    df['Gender'] = df['Gender'].astype(str).str.replace('Gender:', '', case=False).str.strip()
    return df

def clean_general_rules(df: pd.DataFrame) -> pd.DataFrame:
    """Apply general cleaning rules: remove 'Unknown Product', duplicates, and rows with NaN."""
    # Remove invalid Title entries
    df = df[df['Title'] != 'Unknown Product']

    # Drop duplicates
    df = df.drop_duplicates()

    # Drop null values (including NaN from failed conversions)
    df = df.dropna()

    return df

def _transform_df(df: pd.DataFrame) -> pd.DataFrame:
    """Internal pipeline: run all cleaning steps on the DataFrame."""
    try:
        # If the dataframe is empty, return it immediately
        if df.empty:
            return df

        # call specific cleaning functions first to ensure all transformations are applied before general rules
        df = clean_price(df)
        df = clean_rating(df)
        df = clean_colors(df)
        df = clean_text_columns(df)

        # call general cleaning rules at the end to ensure all transformations are applied before filtering
        df = clean_general_rules(df)

        # Reset index after all transformations
        df = df.reset_index(drop=True)

        return df

    except Exception as e:
        print(f"[TRANSFORM ERROR] Failed to transform data: {e}")
        return pd.DataFrame()


def run_transformation(raw_csv_path: str, processed_csv_path: str) -> bool:
    """Read CSV -> transform -> save. Returns True on success, False on failure."""
    try:
        # Baca CSV mentah
        df_raw = pd.read_csv(raw_csv_path)

        # Transformasi
        df_processed = _transform_df(df_raw)

        # If processed result is empty, consider the transformation failed
        if df_processed.empty:
            print("Transformation resulted in an empty DataFrame.")
            return False

        # Save processed CSV
        df_processed.to_csv(processed_csv_path, index=False)
        print(f"Transformed data saved to: {processed_csv_path}")
        return True

    except Exception as e:
        print(f"[TRANSFORM ERROR] Failed to perform transformation (file): {e}")
        return False

# --- Manual test runner ---
if __name__ == "__main__":
    # Dummy data to test the transformation pipeline
    dummy_raw_data = [
        {"Title": "Cool T-Shirt", "Price": "$10.50", "Rating": "⭐ 4.8 / 5", "Colors": "3 Colors", "Size": "Size: L", "Gender": "Gender: Men", "timestamp": "2023-10-27"},
        {"Title": "Unknown Product", "Price": "$0.00", "Rating": "Invalid Rating / 5", "Colors": "0 Colors", "Size": "Size: M", "Gender": "Gender: Women", "timestamp": "2023-10-27"},
        {"Title": "Jacket", "Price": "$20", "Rating": "⭐ 4.5 / 5", "Colors": "2 Colors", "Size": "Size: XL", "Gender": "Gender: Unisex", "timestamp": "2023-10-27"},
        {"Title": "Jacket", "Price": "$20", "Rating": "⭐ 4.5 / 5", "Colors": "2 Colors", "Size": "Size: XL", "Gender": "Gender: Unisex", "timestamp": "2023-10-27"} # Duplicate
    ]

    # Build a DataFrame and run the internal transform pipeline for local testing
    df_dummy = pd.DataFrame(dummy_raw_data)
    result_df = _transform_df(df_dummy)
    print("Transformation Result:")
    print(result_df)
    print("\nData Types:")
    print(result_df.dtypes)