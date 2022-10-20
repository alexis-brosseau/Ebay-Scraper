import urllib.parse
import urllib.request
import statistics
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
    
    soup = __getHTML(query, country, condition)
    data = __parsePrices(soup)

    averagePrice = {
        'soldPrice': round(statistics.mean(data['soldPrices']), 2),
        'shippingPrice': round(statistics.mean(data['shippingPrices']), 2),
        'total': round(statistics.mean(data['soldPrices']) + statistics.mean(data['shippingPrices']), 2)
    }
    
    return averagePrice

def __getHTML(query, country, condition=''):
    
    # Build the URL
    parsedQuery = urllib.parse.quote(query).replace('%20', '+')
    url = f'https://www.ebay{countryDict[country]}/sch/i.html?_from=R40&_nkw=' + parsedQuery + '&LH_Complete=1&LH_Sold=1' + conditionDict[condition]
    
    # Get the web page HTML
    request = urllib.request.urlopen(url)
    soup = BeautifulSoup(request.read(), 'html.parser')

    return soup

def __parsePrices(soup):
    
    # Get item prices
    rawSoldPrices = [item.get_text(strip=True) for item in soup.find_all(class_="s-item__price")]
    soldPrices = [int("".join(filter(str.isdigit, price))) / 100 for price in rawSoldPrices]
    
    # Get shipping prices
    rawShippingPrices = [item.get_text(strip=True) for item in soup.find_all(class_="s-item__shipping s-item__logisticsCost")]
    shippingPrices = [int("".join(filter(str.isdigit, price))) / 100 for price in rawShippingPrices if ("".join(filter(str.isdigit, price)) != '')]
    
    # Remove prices too high or too low
    soldPrices = [price for price in soldPrices if (price > statistics.mean(soldPrices) - statistics.stdev(soldPrices)) and (price < statistics.mean(soldPrices) + statistics.stdev(soldPrices))]
    shippingPrices = [price for price in shippingPrices if (price > statistics.mean(shippingPrices) - statistics.stdev(shippingPrices)) and (price < statistics.mean(shippingPrices) + statistics.stdev(shippingPrices))]
    
    data = {
        'soldPrices': soldPrices,
        'shippingPrices': shippingPrices
    }
    return data
