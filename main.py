import EbayScraper

itemList = EbayScraper.Items(query='comics books', country='us', type='auction', location="world", check_dup=True)
# print(itemList)

# for i in itemList:
#     print(f"Title: {i['title']} ---- Price: {i['price']}, ---- Shipping: {i['shipping']}")

print(len(itemList), itemList[0])
