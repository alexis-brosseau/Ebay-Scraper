import re
import urllib.parse
import urllib.request
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
    'ph': '.ph',
    'pl': '.pl',
    'sg': '.com.sg',
    'uk': '.co.uk',
    'us': '.com',
    'nz': '.co.nz',
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

def Items(query, country='us', condition='all', type='all'):
    
    if country not in countryDict:
        raise Exception('Country not supported, please use one of the following: ' + ', '.join(countryDict.keys()))

    if condition not in conditionDict:
        raise Exception('Condition not supported, please use one of the following: ' + ', '.join(conditionDict.keys()))
        
    if type not in typeDict:
        raise Exception('Type not supported, please use one of the following: ' + ', '.join(typeDict.keys()))
    
    soup = __GetHTML(query, country, condition, type, alreadySold=False)
    data = __ParseItems(soup)
    
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

def __GetHTML(query, country, condition='', type='all', alreadySold=True):
    
    alreadySoldString = '&LH_Complete=1&LH_Sold=1' if alreadySold else ''
    
    # Build the URL
    parsedQuery = urllib.parse.quote(query).replace('%20', '+')
    url = f'https://www.ebay{countryDict[country]}/sch/i.html?_from=R40&_nkw=' + parsedQuery + alreadySoldString + conditionDict[condition] + typeDict[type]

    # Get the web page HTML
    request = urllib.request.urlopen(url)
    soup = BeautifulSoup(request.read(), 'html.parser')

    return soup

def __ParseItems(soup):
    rawItems = soup.find_all('div', {'class': 's-item__info clearfix'})
    data = []

    for item in rawItems[1:]:
        
        #Get item data
        title = item.find(class_="s-item__title").find('span').get_text(strip=True)
        
        price = __ParseRawPrice(item.find('span', {'class': 's-item__price'}).get_text(strip=True))
        
        try: shipping = __ParseRawPrice(item.find('span', {'class': 's-item__shipping s-item__logisticsCost'}).find('span', {'class': 'ITALIC'}).get_text(strip=True))
        except: shipping = 0
        
        try: timeLeft = item.find(class_="s-item__time-left").get_text(strip=True)
        except: timeLeft = ""
        
        try: timeEnd = item.find(class_="s-item__time-end").get_text(strip=True)
        except: timeEnd = ""
        
        try: bidCount = int("".join(filter(str.isdigit, item.find(class_="s-item__bids s-item__bidCount").get_text(strip=True))))
        except: bidCount = 0
        
        try: reviewCount = int("".join(filter(str.isdigit, item.find(class_="s-item__reviews-count").find('span').get_text(strip=True))))
        except: reviewCount = 0
        
        url = item.find('a')['href']

        itemData = {
            'title': title,
            'price': price,
            'shipping': shipping,
            'time-left': timeLeft,
            'time-end': timeEnd,
            'bid-count': bidCount,
            'reviews-count': reviewCount,
            'url': url
        }
        
        data.append(itemData)
    
    # Remove item with prices too high or too low
    priceList = [item['price'] for item in data]
    parsedPriceList = __StDevParse(priceList)
    data = [item for item in data if item['price'] in parsedPriceList]
    
    return sorted(data, key=lambda dic: dic['price'] + dic['shipping'])

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
