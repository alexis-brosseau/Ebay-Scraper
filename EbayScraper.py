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
    dataList = __parse(soup)
    averagePrice = __average(dataList)
    
    return averagePrice

def __getData(query, country, condition=''):
    
    parsedQuery = urllib.parse.quote(query).replace('%20', '+')
    url = f'https://www.ebay{countryDict[country]}/sch/i.html?_from=R40&_nkw=' + parsedQuery + '&LH_Complete=1&LH_Sold=1' + conditionDict[condition]
    request = urllib.request.urlopen(url)
    soup = BeautifulSoup(request.read(), 'html.parser')

    return soup

def __parse(soup):
    
    rawPrices = [item.get_text(strip=True) for item in soup.find_all(class_="s-item__price")]
    averageLength = sum(map(len, rawPrices)) / len(rawPrices)
    
    soldPrices = [item for item in rawPrices if not(len(item) < averageLength-1) and not(len(item) > averageLength+1)]
    soldPrices = [int("".join(filter(str.isdigit, price))) / 100 for price in soldPrices]
    
    shippingPrices = [item.get_text(strip=True) for item in soup.find_all(class_="s-item__shipping s-item__logisticsCost")]
    shippingPrices = [int("".join(filter(str.isdigit, price))) / 100 for price in shippingPrices if ("".join(filter(str.isdigit, price)) != '')]
    
    data = {
        'soldPrices': soldPrices,
        'shippingPrices': shippingPrices
    }
    
    return data


def __average(data):
    
    averageSold = sum(data['soldPrices']) / len(data['soldPrices'])
    averageShipping = sum(data['shippingPrices']) / len(data['shippingPrices'])
    
    averagePrice = {
        'soldPrice': round(averageSold, 2),
        'shippingPrice': round(averageShipping, 2),
        'total': round(averageSold + averageShipping, 2)
    }

    return averagePrice
