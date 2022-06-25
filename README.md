# EbayScraper
Get the average price of any product on Ebay.
```PYTHON
import EbayScraping

price = EbayScraping.search('Nintendo Switch', 'ca', 'new')
print(price)
```
```PYTHON
Output: {'soldPrice': 326.2, 'shippingPrice': 39.67, 'total': 365.87}
```
