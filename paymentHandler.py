import os
from flask import Flask, render_template, request
import stripe



stripe_keys = {
  'secret_key': os.environ['SECRET_KEY'],
  'publishable_key': os.environ['PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)

def charge():
    # Amount in cents
    amount = 500


    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

    print(charge)

    return render_template('charge.html', amount=amount)



if __name__ == '__main__':
    app.run(debug=True)
