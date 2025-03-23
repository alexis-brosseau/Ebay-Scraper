# --- v1.1: Updates
# --- v1.1: Loop through multiple pages and extract the data
# --- v1.1: Adding location parameters for getting most of products [world, us, default]
# --- v1.1: Getting rid of duplicate products using hashes
# --- v1.1: Image URL added in product dictionay


import re
import urllib.parse
import urllib.request
import hashlib
from bs4 import BeautifulSoup

countryDict = {
    'au': '.com.au',
    'at': '.at',
    'be': '.be',
    'ca': '.ca',
    'ch': '.ch',
    'de': '.de',
    'es': '.es',
    'fr': '.fr',
    'hk': '.com.hk',
    'ie': '.ie',
    'it': '.it',
    'my': '.com.my',
    'nl': '.nl',
    'nz': '.co.nz',
    'ph': '.ph',
    'pl': '.pl',
    'sg': '.com.sg',
    'uk': '.co.uk',
    'us': '.com',
}

product_location = {
    "default": "98",
    "us": "1",
    "world": "2",
    "north_america": "3"
}


conditionDict = {
    'all': '',
    'new': '&LH_ItemCondition=1000',
    'opened': '&LH_ItemCondition=1500',
    'refurbished': '&LH_ItemCondition=2500',
    'used': '&LH_ItemCondition=3000'
}

typeDict = {
    'all': '&LH_All=1',
    'auction': '&LH_Auction=1',
    'bin': '&LH_BIN=1',
    'offers': '&LH_BO=1'
}

stored_hashes = set() 



def fast_hash(text: str, algorithm: str = "md5") -> str:
    """
    Generate a fast hash for the given text using the specified algorithm.
    :param text: The input text to hash.
    :param algorithm: The hashing algorithm ('md5', 'sha1', 'sha256').
    :return: The hashed value as a hexadecimal string.
    """
    try: return hashlib.new(algorithm, text.encode()).hexdigest()
    except ValueError: return text




def Items(query, country='us', condition='all', type='all', location="world", max_pages=4, check_dup=True):

    if country not in countryDict:
        raise Exception('Country not supported, please use one of the following: ' + ', '.join(countryDict.keys()))

    if condition not in conditionDict:
        raise Exception('Condition not supported, please use one of the following: ' + ', '.join(conditionDict.keys()))
        
    if type not in typeDict:
        raise Exception('Type not supported, please use one of the following: ' + ', '.join(typeDict.keys()))
    
    soup = __GetHTML(query, country, condition, type, alreadySold=False, location=location)

    #  --- Get total products [Products Pagess]
    total_products = soup.find("h1", {"class": 'srp-controls__count-heading'}).find_all('span', {"class": 'BOLD'})[0].get_text(strip=True)
    total_products = int(total_products.replace(",", ''))
    total_pages = max(1, int(total_products / 240))                             # Each Page contains 240 Product
    print(f"Total Products: {total_products} PAGES: 1/{total_pages}")
    
    data = __ParseItems(soup, check_dup=check_dup)

    #  --- Getting products data from multiple pages
    if total_products>0:
        for page in range(2, total_products+1):
            if page >= max_pages: break
            soup = __GetHTML(query, country, condition, type, alreadySold=False, page=page)
            data = data + __ParseItems(soup, check_dup=check_dup)
    
    return data
    



def Average(query, country='us', condition='all'):
    
    if country not in countryDict:
        raise Exception('Country not supported, please use one of the following: ' + ', '.join(countryDict.keys()))

    if condition not in conditionDict:
        raise Exception('Condition not supported, please use one of the following: ' + ', '.join(conditionDict.keys()))
    
    soup = __GetHTML(query, country, condition, type='all', alreadySold=True)
    data = __ParsePrices(soup)
    
    avgPrice = round(__Average(data['price-list']), 2)
    avgShipping = round(__Average(data['shipping-list']), 2)

    return {
        'price': avgPrice,
        'shipping': avgShipping,
        'total': round(avgPrice + avgShipping, 2)
    }




def __GetHTML(query, country, condition='', type='all', alreadySold=True, location="world", page=1):
    
    alreadySoldString = '&LH_Complete=1&LH_Sold=1' if alreadySold else ''
    
    # Build the URL
    parsedQuery = urllib.parse.quote(query).replace('%20', '+')

    # --- Added Page & Location Parameter
    url = f'https://www.ebay{countryDict[country]}/sch/i.html?_from=R40&_nkw=' + parsedQuery + alreadySoldString + conditionDict[condition] + typeDict[type] + "&_ipg=240" + f"&LH_PrefLoc={product_location[location]}{'&_pgn='+str(page) if page>1 else ''}"

    # Get the web page HTML
    request = urllib.request.urlopen(url)
    soup = BeautifulSoup(request.read(), 'html.parser')

    return soup




def __ParseItems(soup, check_dup=True):
    try:

        data = []
        global stored_hashes
        
        # --- Start from Products Container -> Including Image & Products Section
        products_container = soup.find_all('div', {"class": 's-item__wrapper clearfix'})

        for product in products_container:
            
            try:
                # --- Adding Products Image
                product_image = product.find("div", class_="s-item__image-wrapper image-treatment").find("img")
                if product_image: img_url = product_image["src"]
                else: img_url = None
                
                rawItem = product.find('div', {'class': 's-item__info clearfix'})

                title = rawItem.find(class_="s-item__title").find('span').get_text(strip=True)
                if "shop on ebay" in title.lower(): continue

                try: price = __ParseRawPrice(rawItem.find('span', {'class': 's-item__price'}).get_text(strip=True))
                except: continue

                # --- Create a hash of product TITLE + PRICE so that no other product with matching get duplicated
                hash_value = fast_hash(title + "--" + str(int(price)))
                if check_dup and hash_value in stored_hashes: continue
                stored_hashes.add(hash_value)
                # --- Add the new_hash to old hashes

                try:  shipping = __ParseRawPrice(rawItem.find('span', {'class': 's-item__logisticsCost'}).get_text(strip=True))
                except: shipping = 0

                try: timeEnd = rawItem.find(class_="s-item__time-end").get_text(strip=True)
                except: timeEnd = ""

                try: timeLeft = rawItem.find(class_="s-item__time-left").get_text(strip=True)
                except: timeLeft = ""
                
                try: bidCount = int("".join(filter(str.isdigit, rawItem.find(class_="s-item__bids s-item__bidCount").get_text(strip=True))))
                except: bidCount = 0
                
                try: reviewCount = int("".join(filter(str.isdigit, rawItem.find(class_="s-item__reviews-count").find('span').get_text(strip=True))))
                except: reviewCount = 0

                url = rawItem.find('a')['href']

                itemData = {
                    'title': title,
                    'price': price,
                    'shipping': shipping,
                    'time-left': timeLeft,
                    'time-end': timeEnd,
                    'bid-count': bidCount,
                    'reviews-count': reviewCount,
                    "image_url": img_url,
                    'url': url
                }
                data.append(itemData)
            
            except: continue
        
        # Remove item with prices too high or too low
        priceList = [item['price'] for item in data]
        parsedPriceList = __StDevParse(priceList)
        data = [item for item in data if item['price'] in parsedPriceList]
        return sorted(data, key=lambda dic: dic['price'] + dic['shipping'] if dic['shipping'] else 0.0)
    
    except Exception as e:
        print(e) 
        return []
    


def __ParsePrices(soup):
    
    # Get item prices
    rawPriceList = [price.get_text(strip=True) for price in soup.find_all(class_="s-item__price")]
    priceList = [price for price in map(lambda rawPrice:__ParseRawPrice(rawPrice), rawPriceList) if price != None]
    
    # Get shipping prices
    rawShippingList = [item.get_text(strip=True) for item in soup.find_all(class_="s-item__shipping s-item__logisticsCost")]
    shippingList = map(lambda rawPrice:__ParseRawPrice(rawPrice), rawShippingList)
    shippingList = [0 if price == None else price for price in shippingList]

    # Remove prices too high or too low
    priceList = __StDevParse(priceList)
    shippingList = __StDevParse(shippingList)

    data = {
        'price-list': priceList,
        'shipping-list': shippingList
    }
    return data




def __ParseRawPrice(string):
    # print("Got String: ", string)
    parsedPrice = re.search('(\d+(.\d+)?)', string.replace(',', '.'))
    if (parsedPrice):
        return float(parsedPrice.group())
    else:
        return None



def __Average(numberList):

    if len(list(numberList)) == 0: return 0
    return sum(numberList) / len(list(numberList))



def __StDev(numberList):
    
    if len(list(numberList)) <= 1: return 0
    
    nominator = sum(map(lambda x: (x - sum(numberList) / len(numberList)) ** 2, numberList))
    stdev = (nominator / ( len(numberList) - 1)) ** 0.5

    return stdev



def __StDevParse(numberList):
    
    avg = __Average(numberList)
    stdev = __StDev(numberList)
    
    # Remove prices too high or too low; Accept Between -1 StDev to +1 StDev
    numberList = [nmbr for nmbr in numberList if (avg + stdev >= nmbr >= avg - stdev)]

    return numberList
