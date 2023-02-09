from flask import Flask, request, jsonify
from flask_cors import CORS

import firebase_admin
from firebase_admin import credentials, firestore, storage
import pyrebase
# import os
import tempfile
import json
# from collections.abc import Mapping


app = Flask(__name__)
CORS(app) 


# for pyrebase --> for storing imagespython pr
firebaseConfig = {
  "apiKey": "AIzaSyDqjzQgQ9TUFUda5a0F5PQAWRWGLL4P8XQ",
  "authDomain": "leichachacha.firebaseapp.com",
  "projectId": "leichachacha",
  "storageBucket": "leichachacha.appspot.com",
  "serviceAccount": "leichachacha.json",
  "databaseURL" : ""
}
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

# Use a service account
cred = credentials.Certificate('leichachacha.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
# bucket = storage.bucket()

@app.route("/product", methods=['POST'])
def create_product():
    try:
        # auto generate a productID 
        doc_ref = db.collection(u'product').document()

        # get the generated productID
        productID = doc_ref.id

        # all product images will be in the product folder, name is ProductID
        productPath = "product/" + productID
        
        # use previously generated product ID to create a product
        product = json.loads(request.form['data'])
        product['ProductID'] = productID


        # create a new product in the product collection 
        doc_ref.set(product)

        # get file from request body with key name "image" ( postman's body tab > form-data > key: image (file type) )
        productImage = request.files['image']

        # create a temp png file so that we can upload it to firebase
        # delete=True so that the temp file is deleted as soon as it is closed
        temp = tempfile.NamedTemporaryFile(delete=False,suffix='.png')
        productImage.save(temp.name)

        # upload image to storage 
        storage.child(productPath).put(temp.name)
        # print(storage.child("product/DIntxfvnMajJjZnkFy9Q").get_url(None))

        # close the temp file
        temp.close
        
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred creating the product.",
                "error log": str(e)
            }
        ), 500
    return jsonify(
        {
            "code": 201,
            "productID": productID,
            "message": "Product successfully created."

        }
    ), 201

@app.route("/getallproducts")
def get_all():
    productlist = db.collection(u'product').stream()
    listOfProducts = []
    for product in productlist:
        oneProd = {}
        oneProd[product.id] = product.to_dict()
        
        # get img url from storage and add it to the object that is going to be sent back
        storagePath = 'product/' + product.id
        oneProd[product.id]['imgUrl'] = storage.child(storagePath).get_url(None)
        print(storage.child(storagePath).get_url(None))
        
        print(f'{product.id} => {product.to_dict()}')
        listOfProducts.append(oneProd)

    if len(listOfProducts):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "products": listOfProducts
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no products."
        }
    ), 404

@app.route("/product/<productID>", methods=['PUT'])
def update_book(productID):
    productlist = db.collection(u'product').document(productID)

    product = productlist.get()

    if product.exists:
        data = request.get_json()
        print(data)

        # for each variable that needs to be changed, loop thru and update the product in firebase
        for item in data:
            print(item)
            productlist.update( {item: data[item]} )

        # db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": "success"
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "productID": productID
            },
            "message": "Product not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
