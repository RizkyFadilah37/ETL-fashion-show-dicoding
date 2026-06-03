import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_html(url: str):
    """Fetch the HTML of a page and return a BeautifulSoup object. Returns None on failure."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"[EXTRACT ERROR] Failed to fetch page {url}: {e}")
        return None

def parse_product(item) -> dict:
    """Extract a single product's data from a card element. Returns a dict with 7 keys (6 fields + timestamp)."""
    # Waktu scraping sesuai kriteria Skilled
    extracted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Ekstrak Title & Price
    title_elem = item.find('h3', class_='product-title')
    title = title_elem.text.strip() if title_elem else None
    
    price_elem = item.find('span', class_='price')
    price = price_elem.text.strip() if price_elem else None
    
    # Default value for fields that may not be present
    rating = None
    colors = None
    size = None
    gender = None
    
    # Extract Rating, Colors, Size, Gender
    details = item.find('div', class_='product-details')
    if details:
        p_tags = details.find_all('p')
        for p in p_tags:
            text = p.text.strip()
            if 'Rating' in text:
                rating = text
            elif 'Colors' in text:
                colors = text
            elif 'Size:' in text:
                size = text
            elif 'Gender:' in text:
                gender = text
                
    return {
        "Title": title,
        "Price": price,
        "Rating": rating,
        "Colors": colors,
        "Size": size,
        "Gender": gender,
        "timestamp": extracted_at
    }

def run_extraction(base_url: str = "https://fashion-studio.dicoding.dev", max_pages: int = 50) -> list:
    """Loop scraping from page 1 to max_pages. Stops if a page is empty or on error. Returns a list of products."""
    all_data = []
    
    # Loop page 1 to 50 
    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{base_url}/"
        else:
            url = f"{base_url}/page{page}"
            
        print(f"Scraping page {page}...")
        soup = get_html(url)
        
        # Jika HTML gagal diambil, hentikan scraping
        if not soup:
            break
            
        items = soup.find_all('div', class_='collection-card')
        
        # If the page has no products, stop scraping
        if not items:
            break
            
        for item in items:
            product_dict = parse_product(item)
            all_data.append(product_dict)
            
    return all_data

# --- Manual test runner ---
if __name__ == "__main__":
    results = run_extraction()
    print(f"Total items collected: {len(results)}")