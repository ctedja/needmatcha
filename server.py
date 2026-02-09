import os
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import stripe

load_dotenv()  # loads variables from .env into environment

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Product Price ID from Stripe Dashboard
PRICE_ID = os.getenv('PRICE_ID')

app = Flask(__name__,
            static_url_path='',
            static_folder='.')

YOUR_DOMAIN = os.getenv('YOUR_DOMAIN', 'http://localhost:4242')

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            ui_mode='embedded',
            payment_method_types=['card'],
            line_items=[
                {
                    'price': PRICE_ID,
                    'quantity': 1,
                },
            ],
            mode='payment',
            return_url=YOUR_DOMAIN + '/return.html?session_id={CHECKOUT_SESSION_ID}',
        )
    except Exception as e:
        return jsonify(error=str(e)), 400

    return jsonify(clientSecret=session.client_secret)

@app.route('/session-status', methods=['GET'])
def session_status():
    session = stripe.checkout.Session.retrieve(request.args.get('session_id'))
    return jsonify(status=session.status, customer_email=session.customer_details.email)

if __name__ == '__main__':
    app.run(port=4242)