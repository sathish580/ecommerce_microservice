from re import U
# from tkinter.tix import Select
from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

product_URL = environ.get('product_URL') or "http://localhost:5000/product"
email_URL = environ.get('email_pricewatchers_URL') or "http://localhost:5200/email_pricewatchers"


@app.route("/price_change", methods=['POST'])    # Simple check of input format and data of the request are JSON
# @app.route("/price_change")    # Simple check of input format and data of the request are JSON
def selected_product():
    if request.is_json:
        try:
            SelectedProd = request.get_json()
            print("\nProduct is selected - received in JSON", SelectedProd)

            # do the actual work
            # 1. Send product info {product items}
            result = processUpdateProduct(SelectedProd) 
            return jsonify(result), result["code"]

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "place_order.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processUpdateProduct(SelectedProd):
    print(SelectedProd)
    # take out ID and price
    print('hie')
    product_id = SelectedProd['ProductID']
    new_price = str(SelectedProd['Price'])
    print(new_price)
    # set new product URL as product + / + ID
    new_product_URL = product_URL + '/' + product_id
    print(new_product_URL)
    # Send the product info {cart items}
    # Invoke the product microservice                                                     
    print('\n-----Invoking product microservice-----')
    updated_result = invoke_http(new_product_URL, method='PUT', json=SelectedProd)

    print(updated_result)
    # print('product_update_result:', updated_result) #publish message indicating price change      
    status = updated_result['data']
    if status == 'success':
        # print('\n\n-----Invoking PW microservice-----')
        # PW = "http://localhost:5002/pricewatching/" + product_id + "/" + new_price
        # PW_result = invoke_http(PW, method="GET", json=SelectedProd)
        # print("PW_result:", PW_result, '\n')  


        # new_email_URL = email_URL + product_id + '/' + new_price
        # Invoke the email pricewatchers microservice
        print('\n\n-----Invoking email_pricewatcher microservice-----')
        email_result = invoke_http(email_URL, method="POST", json=SelectedProd)
        print("email_result:", email_result, '\n')  

    # 7. Return created order, shipping record
    return {
        "code": 201,
        "data": {
            "updated_result:": updated_result,
        }
    }



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5100, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
