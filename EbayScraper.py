import re
import urllib.parse
import requests
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
}

conditionDict = {
    'all': '',
    'new': '&LH_ItemCondition=1000',
    'opened': '&LH_ItemCondition=1500',
    'refurbished': '&LH_ItemCondition=2500',
    'used': '&LH_ItemCondition=3000'
}

    
def search(query, country='us', condition='all'):
    
    if country not in countryDict:
        raise Exception('Country not supported, please use one of the following: ' + ', '.join(countryDict.keys()))

    if condition not in conditionDict:
        raise Exception('Condition not supported, please use one of the following: ' + ', '.join(conditionDict.keys()))
    
    soup = __getData(query, country, condition)
    productList = __parse(soup)
    averagePrice = __average(productList)
    
    return averagePrice

def __getData(query, country, condition=''):
    
    parsedQuery = urllib.parse.quote(query).replace('%20', '+')
    url = f'https://www.ebay{countryDict[country]}/sch/i.html?_from=R40&_nkw=' + parsedQuery + '&LH_Complete=1&LH_Sold=1' + conditionDict[condition]
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html')
    
    return soup

def __parse(soup):
    results = soup.find_all('div', {'class': 's-item__info clearfix'})
    productList = []
    
    for item in results:
        
        if (item.find('span', {'class': 's-item__shipping s-item__logisticsCost'}) is not None) and ('to' not in item.find('span', {'class': 's-item__price'}).text):
            
            soldPrice = int(''.join(filter(str.isdigit, item.find('span', {'class': 's-item__price'}).text))) / 100
            #soldPrice = int(re.sub('[^0-9]', "", item.find('span', {'class': 's-item__price'}).text)) / 100
            shippingPrice = re.sub('[^0-9]', "",str(item.find('span', {'class': 's-item__shipping s-item__logisticsCost'}).find('span', {'class': 'ITALIC'})))
            
            if (shippingPrice != ''):
                shippingPrice = int(shippingPrice) / 100
            else: 
                shippingPrice = 0
            
            product = {
                'soldPrice': soldPrice,
                'shippingPrice': shippingPrice
            }
            productList.append(product)
            
    return productList

def __average(list):
    averageSold = 0
    averageShipping = 0
    
    for i in list:
        averageSold += i['soldPrice']
        averageShipping += i['shippingPrice']

    averageSold /= len(list)
    averageShipping /= len(list)
    
    averagePrice = {
        'soldPrice': round(averageSold, 2),
        'shippingPrice': round(averageShipping, 2),
        'total': round(averageSold + averageShipping, 2)
    }

    return averagePrice
