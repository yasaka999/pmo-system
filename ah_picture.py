import json
file = "../files/6000007338.json"

with open (file) as data:
    json_data = json.load(data)
    codes_with_empty_pictures = []

    for item in json_data['epgCategorydtl']:
        if item['type'] == 'outlink' and not item['pictures']:
            codes_with_empty_pictures.append(item['title'])

    if  codes_with_empty_pictures:
        print ("missing picture: %s" %file)
        for i in codes_with_empty_pictures:
            print(i)
    else:
        print ("no missing picture")
