# Ebay Scraper
#### This script has 2 main functions:
1. Get the average price of a product based on already sold ones.
2. Get a list of products on sale.

## Requirements: ##

- **[BeautifulSoup4](https://pypi.org/project/beautifulsoup4/)**

## How to Use: ##

1. Install the requirements.
2. Add *EbayScraper.py* to your project directory.
3. Import it.

---

### Average Function:

Here we search for the average price at wich new Nintendo Switch are sold on eBay Canada. The first parameter is for the *search query*, the second one is for the *country* and the third one is for the *condition* of the item.
```PYTHON
import EbayScraper

averagePrice = EbayScraper.Average(query='Nintendo Switch', country='ca', condition='new')
print(averagePrice)
```
#### Output:
The output will be a **dictionary** with the average sold price, the average shipping price and the average total price of the item searched. Here we can see that the average price for a brand new Nintendo Switch on eBay, including the shipping, is **365.87 CAD**.
```PYTHON
{'price': 326.2, 'shipping': 39.67, 'total': 365.87}
```

---


### Items Function:

Like the **Average Function**, the first parameter is for the *search query*, the second one is for the *country* and the third one is for the *condition* of the item. The difference here is that this function return a **list** of **dictionary** with data about each item. Since the **list** returned is sorted by price + shipping, here we get the cheapest auction for an RTX 3060 in Canada.
```PYTHON
import EbayScraper

itemList = EbayScraper.Items(query='RTX 3060', country='ca', condition='new', type='auction')
print(itemList[0])
```
#### Output:
The output will be a **dictionary** with all the information about the item.
```PYTHON
{'title': 'MSI Gaming GeForce RTX 3060 12GB NEW SEALED', 'price': 339.04, 'shipping': 0, 'time-left': '3d 4h left', 'time-end': '(Sun, 12:25 p.m.)', 'bid-count': 14, 'reviews-count': 0, 'url': 'https://www.Ebay.ca/itm/...'}
```
