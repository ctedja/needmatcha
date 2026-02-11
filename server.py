import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import stripe

load_dotenv()  # loads variables from .env into environment

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Product Price ID from Stripe Dashboard
PRICE_ID = os.getenv('PRICE_ID')

app = Flask(__name__)
CORS(app, origins=[
    "https://needmatcha.com.au",
    "https://www.needmatcha.com.au",
    "http://localhost:4242"
])

YOUR_DOMAIN = os.getenv('YOUR_DOMAIN', 'http://localhost:4242')

@app.route('/')
def home():
    return "NEEDMATCHA Backend Active"

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        data = request.get_json(silent=True) or {}
        quantity = data.get('quantity', 1)

        # Basic validation / anti-abuse
        if not isinstance(quantity, int) or quantity < 1 or quantity > 10:
            return jsonify(error='Quantity must be an integer between 1 and 10.'), 400
        
        if quantity > 1:
            shipping_cost = 0
            shipping_label = 'Free Shipping'
            shipping_message = '🎉 Free shipping applied for ordering more than one item!'
        else:
            shipping_cost = 1000
            shipping_label = 'Standard Shipping'
            shipping_message = '💡 Order 1 more item to unlock Free Shipping!'

        session = stripe.checkout.Session.create(
            ui_mode='embedded',
            payment_method_types=['card'],
            line_items=[
                {
                    'price': PRICE_ID,
                    'quantity': quantity,
                },
            ],
            mode='payment',
            shipping_address_collection={
                'allowed_countries': ['AU'],
            },
            shipping_options=[
                {
                    'shipping_rate_data': {
                        'type': 'fixed_amount',
                        'fixed_amount': {
                            'amount': shipping_cost,
                            'currency': 'aud',
                        },
                        'display_name': shipping_label,
                        'delivery_estimate': {
                            'minimum': {'unit': 'business_day', 'value': 2},
                            'maximum': {'unit': 'business_day', 'value': 5},
                        },
                    },
                },
            ],
            custom_text={
                "shipping_address": {"message": shipping_message}
            },
            return_url=YOUR_DOMAIN + '/return.html?session_id={CHECKOUT_SESSION_ID}',
        )
    except Exception as e:
        return jsonify(error=str(e)), 400

    return jsonify(clientSecret=session.client_secret)

@app.route('/session-status', methods=['GET'])
def session_status():
    session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
    return jsonify(status=session.status, customer_email=session.customer_details.email)

@app.route('/health', methods=['GET'])
def health():
    return jsonify(status="ok")

if __name__ == '__main__':
    app.run(port=4242)