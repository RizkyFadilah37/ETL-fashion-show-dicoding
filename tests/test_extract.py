import pytest
from bs4 import BeautifulSoup
import utils.extract.web_scraper as ws
import requests


def sample_html():
    return """
    <div class="collection-card">
      <h3 class="product-title">Prod A</h3>
      <span class="price">$10</span>
      <div class="product-details">
        <p>Rating: ⭐ 4.5 / 5</p>
        <p>Colors: 3 Colors</p>
        <p>Size: Size: M</p>
        <p>Gender: Gender: Men</p>
      </div>
    </div>
    <div class="collection-card">
      <h3 class="product-title">Prod B</h3>
      <span class="price">$20</span>
      <div class="product-details">
        <p>Rating: ⭐ 4.0 / 5</p>
        <p>Colors: 2 Colors</p>
        <p>Size: Size: L</p>
        <p>Gender: Gender: Women</p>
      </div>
    </div>
    """


def test_run_extraction_monkeypatch(monkeypatch):
    # Patch network call to return predictable HTML
    monkeypatch.setattr(ws, 'get_html', lambda url: BeautifulSoup(sample_html(), 'html.parser'))

    results = ws.run_extraction(base_url='http://example', max_pages=1)

    assert isinstance(results, list)
    assert len(results) == 2
    for r in results:
        assert 'Title' in r and 'Price' in r and 'timestamp' in r


def test_get_html_success(monkeypatch):
    class FakeResponse:
        text = sample_html()
        def raise_for_status(self):
            pass

    monkeypatch.setattr(requests, 'get', lambda url, timeout: FakeResponse())
    result = ws.get_html('http://example')
    assert result is not None
    assert isinstance(result, BeautifulSoup)


def test_get_html_failure_timeout(monkeypatch):
    def fake_get(url, timeout):
        raise requests.exceptions.Timeout()
    monkeypatch.setattr(requests, 'get', fake_get)
    result = ws.get_html('http://example')
    assert result is None


def test_get_html_failure_httperror(monkeypatch):
    def fake_get(url, timeout):
        raise requests.exceptions.HTTPError()
    monkeypatch.setattr(requests, 'get', fake_get)
    result = ws.get_html('http://example')
    assert result is None


def test_parse_product_no_details_div():
    html = '''<div class="collection-card"><h3 class="product-title">X</h3><span class="price">$5</span></div>'''
    soup = BeautifulSoup(html, 'html.parser')
    item = soup.find('div', class_='collection-card')
    result = ws.parse_product(item)
    assert result['Title'] == 'X'
    assert result['Rating'] is None and result['Colors'] is None


def test_run_extraction_empty_items(monkeypatch):
    monkeypatch.setattr(ws, 'get_html', lambda url: BeautifulSoup('<html></html>', 'html.parser'))
    results = ws.run_extraction(base_url='http://example', max_pages=1)
    assert len(results) == 0
