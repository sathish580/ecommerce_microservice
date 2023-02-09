from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import paypalrestsdk

import os, sys
from os import environ

# import Payment.amqp_setup as amqp_setup
import pika
import json
import amqp_setup


app = Flask(__name__, template_folder='templates')

paypalrestsdk.configure({
    "mode": "sandbox", # sandbox or live
    "client_id": "AcukAZbvVsgwhW784yFe7CFkmlAiZeaxjy3HcL60g9S24DO-hYz31JF2WbIml_zm-yREXan4sZhe_IHX",
    "client_secret": "EIc1dUG-nlHbMDCjjQMbjdLCgGvvKtgVeDso9WfCCHeIp9oN0IJQ_CX2fUsuCTHkSpD2PSyCFH3vQq2e" })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/payment', methods=['POST'])
def payment():
    payment = paypalrestsdk.Payment({
    "intent": "sale",
    "payer": {
        "payment_method": "paypal"},
    "redirect_urls": {
        "return_url": "http://127.0.0.1:5001/return",
        "cancel_url": "http://127.0.0.1:5001/cancel"},
    "transactions": [{
        "item_list": {
            "items": [{
                "name": request.form['name'],
                "price": request.form['price'],
                "currency": "USD",
                "quantity": request.form['quantity']}]},
        "amount": {
            "total": request.form['total_price'],
            "currency": "USD"
            },
        "description": "This is the payment transaction description."
        }]
    })

    amqp_setup.check_setup()

    if payment.create():
        print('Payment success!')
        print(payment)
    else:
        # print(payment.error)
        # code = payment.code
        code = 400
        
        print('\n\n-----Publishing the error message with routing_key=payment.error-----')
        # example of invalid: quantity 0, total price unmatched
        message = json.dumps({
            "code": 400,
            "error": payment.error,
            "customerId": request.form['customer_id'], 
            # Assume user account has email record
            "payerEmail": 'jiayi.fok.2020@scis.smu.edu.sg', 
            "state": 'creation failed'
        })
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="payment.email", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
        print("Payment creation status ({:d}) published to the RabbitMQ Exchange:".format(code), payment)
        
        # Return error
        return {
            "code": 400,
            "error": payment.error,
            "customerId": request.form['customer_id'],
            "message": "Payment creation error sent for error handling."
        }

    return jsonify(
        {
            "code": 201,
            "status": "created",
            "paymentID": payment.id,
            "customerID": request.form['customer_id']
        })



@app.route('/execute', methods=['POST'])
def execute():
    # success = False
    payment = paypalrestsdk.Payment.find(request.form['paymentID'])

    amqp_setup.check_setup()

    if payment.execute({'payer_id' : request.form['payerID']}):
        print('Execute Success!')
        # success = True

        print('\n\n-----Publishing the payment success confirmation with routing_key=payment.email-----')
        print(payment)
        code = 202
        message = json.dumps({
            "code": 202,
            "paymentID": payment.id,
            "state": payment.state,
            # "payerEmail": payment.payer.payer_info.email,
            # for demonstration purposes,
            "payerEmail": 'jiayi.fok.2020@scis.smu.edu.sg',
            "payerID": payment.payer.payer_info.payer_id, 
            
        })
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="payment.email", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))
        print("Payment execution status ({:d}) published to the RabbitMQ Exchange:".format(code), message)

        return jsonify({
            "code": 202,
            "state": payment.state,
            "paymentID": payment.id,
        })
        
    else:
        code = 400
        print(payment.error)
        
        print('\n\n-----Publishing the error message with routing_key=payment.error-----')
        message = json.dumps({
            "code": 400,
            "error": payment.error, 
            "payerEmail": 'jiaayi.lee@gmail.com',
            "state": 'execution failed'
        })
        amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="payment.email", 
            body=message, properties=pika.BasicProperties(delivery_mode = 2))
        print("Payment execution status ({:d}) published to the RabbitMQ Exchange:".format(code), payment)
        # Return error``
        return {
            "code": 400,
            "error": payment.error,
            "message": "Payment executing error sent for error handling."
        }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)