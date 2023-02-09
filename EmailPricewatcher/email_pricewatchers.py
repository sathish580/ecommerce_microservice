from flask import Flask, request, jsonify
from flask_cors import CORS

import http.client
import os
import sys
import json
from os import environ
import amqp_setup, pika
import requests
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

pricewatching_URL = environ.get('pricewatching_URL') or "http://localhost:5002/pricewatching"
email_notification_URL = environ.get('email_notification_URL') or "http://localhost:5400/sendgrid"

@app.route("/email_pricewatchers", methods=['POST'])
def email_pricewatchers():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            product = request.get_json()
            print("\nReceived an order in JSON:", product)
            print(type(product))
            # order = json.dumps(order)
            # print(type(order))
            # do the actual work
            # 1. Send order info {cart items}
            result = processProductChange(product)
            print(result, "RESULTTTTTT")
            if result == True:
                return {
                    "status": "202",
                    "description": "Customers have been notified"
                }
            elif result['code'] == 404:
                return result
            return {
                "status": '504',
                "description": "Error in notifiying all customers"
            }

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + \
                fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "email_pricewatchers.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processProductChange(product):
    print("PRODUCT IN EMAIL PRICEWATCHERS")
    print(product)
    product_id = product['ProductID']
    # print(product_id)
    new_price = product['Price']
    print(new_price)

    price_watchers = invoke_http(
        pricewatching_URL + "/" + product_id + "/" + str(new_price), method="GET")

    print(type (price_watchers['code']),"CODEEEE")

    if price_watchers['code']  == 404:
        print(price_watchers,"WATCHERS")
        return price_watchers
    
    price_watchers_email = price_watchers['valid_email']
    product_name = price_watchers['product_name']


    amqp_setup.check_setup()
    email_count = 0
    # print(product_name,price_watchers_email)
    for email in price_watchers_email:
        print(email,"EMAIL")
        json_data = {
        "updated_price": new_price,
        "email": email,
        "product_name": product_name,
        "state": "price_change"
        }
        print(json_data)
        # emailRes = invoke_http(
        # "http://localhost:5400/sendgrid" , method="POST", json=json_data)
        json_data = json.dumps(json_data)

        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="pricewatch.email", 
        body=json_data, properties=pika.BasicProperties(delivery_mode = 2)) 

        print("Payment creation status published to the RabbitMQ Exchange:", json_data)
    
        email_count += 1

    if email_count == len(price_watchers_email):
        return True

    # print(emailRes['code'])

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing an order...")
    app.run(host="0.0.0.0", port=5200, debug=True)
