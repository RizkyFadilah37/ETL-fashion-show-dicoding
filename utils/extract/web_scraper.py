import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_html(url: str):
    """
    Fungsi khusus untuk melakukan request HTTP.
    Mengembalikan objek BeautifulSoup jika sukses, atau None jika gagal.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"[EXTRACT ERROR] Gagal mengambil halaman {url}: {e}")
        return None

def parse_product(item) -> dict:
    """
    Fungsi khusus untuk mengekstrak data dari satu elemen kartu produk.
    Mengembalikan dictionary berisi 6 kolom yang diminta + timestamp.
    """
    # Waktu scraping sesuai kriteria Skilled
    extracted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Ekstrak Title & Price
    title_elem = item.find('h3', class_='product-title')
    title = title_elem.text.strip() if title_elem else None
    
    price_elem = item.find('span', class_='price')
    price = price_elem.text.strip() if price_elem else None
    
    # Default value untuk detail lainnya
    rating = None
    colors = None
    size = None
    gender = None
    
    # Ekstrak Rating, Colors, Size, Gender
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
    """
    Fungsi orkestrator untuk nge-loop halaman 1 sampai max_pages.
    """
    all_data = []
    
    # Loop halaman 1 sampai 50 sesuai Kriteria Basic
    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{base_url}/"
        else:
            url = f"{base_url}/page{page}"
            
        print(f"Scraping halaman {page}...")
        soup = get_html(url)
        
        # Jika HTML gagal diambil, hentikan scraping
        if not soup:
            break
            
        items = soup.find_all('div', class_='collection-card')
        
        # Jika halaman kosong tidak ada produk, hentikan scraping
        if not items:
            break
            
        for item in items:
            product_dict = parse_product(item)
            all_data.append(product_dict)
            
    return all_data

# --- Buat test jalanin manual ---
if __name__ == "__main__":
    hasil = run_extraction()
    print(f"Total data terkumpul: {len(hasil)}")