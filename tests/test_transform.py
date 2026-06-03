import pandas as pd
from utils.transform.data_cleaner import (
    run_transformation, clean_price, clean_rating, clean_colors,
    clean_text_columns, clean_general_rules, _transform_df
)


def test_run_transformation_file(tmp_path):
    # Prepare dummy raw data and write to CSV
    raw = [
        {"Title": "T-Shirt Keren", "Price": "$10.50", "Rating": "⭐ 4.8 / 5", "Colors": "3 Colors", "Size": "Size: L", "Gender": "Gender: Men", "timestamp": "2023-10-27"},
        {"Title": "Unknown Product", "Price": "$0.00", "Rating": "Invalid Rating / 5", "Colors": "0 Colors", "Size": "Size: M", "Gender": "Gender: Women", "timestamp": "2023-10-27"}
    ]

    raw_csv = tmp_path / "raw.csv"
    processed_csv = tmp_path / "processed.csv"
    pd.DataFrame(raw).to_csv(raw_csv, index=False)

    status = run_transformation(str(raw_csv), str(processed_csv))
    assert status is True

    dfp = pd.read_csv(processed_csv)
    assert 'Price' in dfp.columns
    # Price should be numeric after transform
    assert pd.api.types.is_numeric_dtype(dfp['Price'])
    # "Unknown Product" rows should be removed
    assert all(dfp['Title'] != 'Unknown Product')


def test_clean_price():
    df = pd.DataFrame([
        {"Price": "$10.50"},
        {"Price": "$1,234.00"},
        {"Price": "invalid"}
    ])
    df_clean = clean_price(df)
    assert pd.api.types.is_numeric_dtype(df_clean['Price'])
    assert df_clean['Price'].iloc[0] == 10.50 * 16000


def test_clean_rating():
    df = pd.DataFrame([
        {"Rating": "Rating: ⭐ 4.8 / 5"},
        {"Rating": "Invalid Rating"},
        {"Rating": "⭐ 3.5 / 5"}
    ])
    df_clean = clean_rating(df)
    assert len(df_clean) == 2  # Invalid row removed
    assert pd.api.types.is_numeric_dtype(df_clean['Rating'])


def test_clean_colors():
    df = pd.DataFrame([
        {"Colors": "5 Colors"},
        {"Colors": "0 Colors"},
        {"Colors": "None"}
    ])
    df_clean = clean_colors(df)
    assert 'Colors' in df_clean.columns


def test_clean_text_columns():
    df = pd.DataFrame([
        {"Size": "Size: L", "Gender": "Gender: Men"},
        {"Size": "Size: M", "Gender": "Gender: Women"}
    ])
    df_clean = clean_text_columns(df)
    assert df_clean['Size'].iloc[0] == 'L'
    assert df_clean['Gender'].iloc[0] == 'Men'


def test_clean_general_rules():
    df = pd.DataFrame([
        {"Title": "A", "Price": 100, "Rating": 4.5, "Colors": 2, "Size": "L", "Gender": "Men"},
        {"Title": "Unknown Product", "Price": 50, "Rating": 3.0, "Colors": 1, "Size": "M", "Gender": "Women"},
        {"Title": "A", "Price": 100, "Rating": 4.5, "Colors": 2, "Size": "L", "Gender": "Men"},  # Duplicate
        {"Title": "B", "Price": None, "Rating": 4.0, "Colors": 3, "Size": "L", "Gender": "Men"}  # NaN
    ])
    df_clean = clean_general_rules(df)
    assert len(df_clean) == 1  # Only first non-duplicate, non-unknown, non-null row
    assert df_clean['Title'].iloc[0] == 'A'


def test_transform_df_empty():
    df_empty = pd.DataFrame()
    result = _transform_df(df_empty)
    assert result.empty


def test_run_transformation_nonexistent_file():
    status = run_transformation('/nonexistent/path.csv', '/out.csv')
    assert status is False


def test_run_transformation_empty_csv(tmp_path):
    raw_csv = tmp_path / "empty.csv"
    processed_csv = tmp_path / "processed.csv"
    pd.DataFrame().to_csv(raw_csv, index=False)
    
    status = run_transformation(str(raw_csv), str(processed_csv))
    assert status is False
