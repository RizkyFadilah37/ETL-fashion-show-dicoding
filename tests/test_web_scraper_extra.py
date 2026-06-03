from bs4 import BeautifulSoup
import utils.extract.web_scraper as ws


def test_parse_product_missing_fields():
    html = """
    <div class="collection-card">
      <!-- missing title and price -->
      <div class="product-details">
        <p>Colors: 0 Colors</p>
      </div>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.find('div', class_='collection-card')
    result = ws.parse_product(item)
    assert result['Title'] is None
    assert result['Price'] is None
    assert 'timestamp' in result


def test_parse_product_full_fields():
    html = """
    <div class="collection-card">
      <h3 class="product-title">X</h3>
      <span class="price">$5</span>
      <div class="product-details">
        <p>Rating: ⭐ 5.0 / 5</p>
        <p>Colors: 1 Colors</p>
        <p>Size: Size: S</p>
        <p>Gender: Gender: Unisex</p>
      </div>
    </div>
    """
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.find('div', class_='collection-card')
    result = ws.parse_product(item)
    assert result['Title'] == 'X'
    assert result['Price'] == '$5'
    assert 'Rating' in result
