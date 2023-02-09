import http.client
from itertools import product

from flask import Flask, request, jsonify
from flask_cors import CORS

import http.client
import os
import sys
import json

import requests
from invokes import invoke_http

import amqp_setup

app = Flask(__name__)
CORS(app)

# import Payment.amqp_setup as amqp_setup

monitorBindingKey='*.email'

conn = http.client.HTTPSConnection("rapidprod-sendgrid-v1.p.rapidapi.com")
headers = {
    'content-type': "application/json",
    'X-RapidAPI-Host': "rapidprod-sendgrid-v1.p.rapidapi.com",
    'X-RapidAPI-Key': "440c8c9142msh9504d3c95c2210bp1c8042jsnbf253026e225"
}

def receivePaymentStatus():
    amqp_setup.check_setup()
        
    queue_name = 'Email'
    
    # set up a consumer and start to wait for coming messages
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    amqp_setup.channel.start_consuming() # an implicit loop waiting to receive messages; 
    #it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return
    print("\nReceived a payment log by " + __file__)
    processPayment(json.loads(body))
    print() # print a new line feed

def processPayment(status):
    print("Recording a payment log:")
    print(status)
    
    
    state = status['state']

    if state == 'price_change':
        print("PRICE CHANGE PRINTING ON EMAILER ")
        pricewatcher_email = status['email']
        product_name = status['product_name']
        new_price = status['updated_price']


        body = "Dear Customer, \\n\\n" "Price of " + product_name + " has decreased to $"+ str(new_price) + "! Visit our website to place your order. \\n\\nThank you! "
        print(body)
        payload = "{\n    \"personalizations\": [\n        {\n            \"to\": [\n                {\n                    \"email\": \"" + pricewatcher_email +"\"\n                }\n            ],\n            \"subject\": \"Price Drop!\"\n        }\n    ],\n    \"from\": {\n        \"email\": \"sathish1kumar11@gmail.com\"\n    },\n    \"content\": [\n        {\n            \"type\": \"text/plain\",\n            \"value\":\"" + body + " \"\n        }\n    ]\n}"
        # headers = {
        #     'content-type': "application/json",
        #     'X-RapidAPI-Host': "rapidprod-sendgrid-v1.p.rapidapi.com",
        #     'X-RapidAPI-Key': "440c8c9142msh9504d3c95c2210bp1c8042jsnbf253026e225"
        # }

        conn.request("POST", "/mail/send", payload, headers)

    elif state == 'approved':
        payerEmail = status['payerEmail']
        body = "Dear Customer, \\n\\n" "Your Payment has been successful and your order is confirmed! \\n\\nThank you! "
        print(body)
        payload = "{\n    \"personalizations\": [\n        {\n            \"to\": [\n                {\n                    \"email\": \"" + payerEmail +"\"\n                }\n            ],\n            \"subject\": \"Order Placed!\"\n        }\n    ],\n    \"from\": {\n        \"email\": \"sathish1kumar11@gmail.com\"\n    },\n    \"content\": [\n        {\n            \"type\": \"text/plain\",\n            \"value\":\"" + body + " \"\n        }\n    ]\n}"
        # headers = {
        #     'content-type': "application/json",
        #     'X-RapidAPI-Host': "rapidprod-sendgrid-v1.p.rapidapi.com",
        #     'X-RapidAPI-Key': "440c8c9142msh9504d3c95c2210bp1c8042jsnbf253026e225"
        # }

        conn.request("POST", "/mail/send", payload, headers)
        res = conn.getresponse()
        data = res.read()

        print(data.decode("utf-8"))

        return True

    else:
        payerEmail = status['payerEmail']
        body = "Dear Customer, \\n\\n" "Your Payment was not successful! Please try again! \\n\\nThank you! "
        print(body)
        payload = "{\n    \"personalizations\": [\n        {\n            \"to\": [\n                {\n                    \"email\": \"" + payerEmail +"\"\n                }\n            ],\n            \"subject\": \"Order Placed!\"\n        }\n    ],\n    \"from\": {\n        \"email\": \"sathish1kumar11@gmail.com\"\n    },\n    \"content\": [\n        {\n            \"type\": \"text/plain\",\n            \"value\":\"" + body + " \"\n        }\n    ]\n}"
        # headers = {
        #     'content-type': "application/json",
        #     'X-RapidAPI-Host': "rapidprod-sendgrid-v1.p.rapidapi.com",
        #     'X-RapidAPI-Key': "440c8c9142msh9504d3c95c2210bp1c8042jsnbf253026e225"
        # }

        conn.request("POST", "/mail/send", payload, headers)



# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
        " for placing an order...")
    print(": monitoring routing key '{}' in exchange '{}' ...".format(monitorBindingKey, amqp_setup.exchangename))
    receivePaymentStatus()
    app.run(host="0.0.0.0", port=5400, debug=True)