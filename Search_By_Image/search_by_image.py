from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
# from invokes import invoke_http

app = Flask(__name__)
CORS(app)

product_URL = environ.get('product_URL') or "http://localhost:5000/product"
imageToKeyword_URL = environ.get('imageToKeyword_URL') or "http://localhost:5003/getkeyword"

@app.route("/searchimage", methods=['POST'])
def searchimage():
    print("in search_by_image.py")
    image = request.files['file']
    imageFile = {"file": image}

    print("passing image to image_to_keyword.py")
    image_results = requests.post(imageToKeyword_URL, files=imageFile)

    
    print('image_results:', image_results.json())
    if (image_results.json()['code'] != 200):
        errMsg = image_results.json()['description']
        return jsonify(
            {
            "code": 500,
            "description": "Error trying to retrieve products",
            "details": errMsg
            }
        ),500
    
    # print('image_results:', image_results.json()['keywords'])
    keywords = image_results.json()['keywords']

    all_products_res = requests.get(product_URL)
    # print(all_products_res.json()['data']['products'])
    all_products = all_products_res.json()['data']['products']
    # print('all_products:', all_products)
    filteredList = getProductsByKeyword(keywords, all_products)
    
    if len(filteredList) != 0:
        return jsonify({
            "data": filteredList,
            "keywords" : keywords
        }),200
    else:
        return jsonify({
            "data": filteredList,
            "keywords" : keywords
        }),404


def getProductsByKeyword(keywords, all_products):

    # Spliting keywords into a single word list
    single_word_list = []
    for keyword in keywords:
        # print("current keyword", keyword)
        split_list = keyword.split()
        for oneWord in split_list:
            if oneWord not in single_word_list:
                single_word_list.append(oneWord)

    filteredList = []
    for oneProdObj in all_products:
        # oneProd = all_products[oneProdObj]
        # print("oneProd", oneProdObj)
        for prodId in oneProdObj:
            # print("prodId:", prodId)
            name = oneProdObj[prodId]['Name'].lower()
            desc = oneProdObj[prodId]['Description'].lower()
            keywords = oneProdObj[prodId]['Keywords']
            for keyword in single_word_list:
                keyword = keyword.lower()
                # print(f'{keyword} : {name} : {desc}')
                if (keyword in name or keyword in desc or keyword in keywords) and oneProdObj not in filteredList:
                    filteredList.append(oneProdObj)

    print("filtered list: ", filteredList)
    return filteredList

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5300, debug=True)