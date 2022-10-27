# Ebay Scraper
Get the average price of any product on Ebay based on items already sold.

## Requirements: ##

- **[BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)**

## How to Use: ##

1. Add *EbayScraper.py* to your project directory.
2. Import it.
3. Your Done! You can now search for anything. *(See the exemple for more details)*

### Exemple:

Here we search for a new Nintendo switch on Ebay Canada. The first parameter is for the **search query**, the second one is for the **country** and the third one is for the **condition** of the item.
```PYTHON
import EbayScraping

price = EbayScraping.Average('Nintendo Switch', 'ca', 'new')
print(price)
```
#### Output:
The output will be a **dictionary** with the average sold price, the average shipping price and the average total price of the item searched. Here we can see that the average price for a brand new Nintendo Switch on ebay, including the shipping, is **365.87 CAD**.
```PYTHON
{'soldPrice': 326.2, 'shippingPrice': 39.67, 'total': 365.87}
```
