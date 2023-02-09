import email
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from flask_cors import CORS

# Use a service account
cred = credentials.Certificate('leichachacha.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)
CORS(app)
 
 
@app.route("/pricewatching/<product_id>/<new_price>")
def find_by_product_price(product_id = None, new_price = None):
    
    
    # products = Pricewatching.query.filter_by(product_id=product_id).all()
    # list_t = []

    #only accesses email collection
    users_ref = db.collection(u'email')
    docs = users_ref.stream()
    all_pricewatchers = []


    for doc in docs:
        # print(f'{doc.id} => {doc.to_dict()}')
        all_pricewatchers.append(doc.to_dict())

    # print(all_pricewatchers)
    
    valid_email = []
    for watcher in all_pricewatchers:
        # print(watcher['email'])
        # print(watcher)
        if (watcher['product_id'] == product_id):
            watching_price = watcher['watching_price']
            product_name = watcher['name']
            # print(watcher['email'])
            

            print((new_price))
            if (watcher['watching_price'] >= float(new_price)):
              
                valid_email.append(watcher['email'])
    #             print("TEST",valid_email)
    # print(product_name)
 
    if len(valid_email) != 0:
        return jsonify(
            {
                "code": 200,
                "valid_email": valid_email, 
                "product_name": product_name
            }
        )
        
    return jsonify(
    {
        "code": 404,
            "message": "No eligible watchers"
        }
    ), 404

 

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)


