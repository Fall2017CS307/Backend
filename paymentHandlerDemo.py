from flask import Flask, render_template, request, redirect, url_for
import stripe
from userHandler import userHandler
from utils.dbConn import dbConn
import MySQLdb
from jsonReturn import apiDecorate
import json
import models
import os


app = Flask(__name__)

pub_key = 'pk_test_fOAnrRLEB5cDZMCipafCb71E'
secret_key = 'sk_test_I54z4p3XASvKZAfuwhmDPvlN'

stripe.api_key = secret_key

@app.route('/')
def index():
    print pub_key
    return render_template('index.html', pub_key=pub_key)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/failure')
def failure():
    return render_template('failure.html')

@app.route('/pay', methods=['POST'])
def pay():

    customer = stripe.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=99,
        currency='usd',
        description='The Product'

    )

    #print(customer.email)
    #return redirect(url_for('thanks'))


    if charge.paid :

        print(customer.email)
        session = dbConn().get_session(dbConn().get_engine())


        s = str(customer.email)


        curUser = session.query(models.User).filter(models.User.email == s).first()
        print(customer.email)


        if(curUser is None):
            return redirect(url_for('failure'))

        else:
            curUser.balance = curUser.balance + charge.amount
            session.commit()
            return redirect(url_for('thanks'))

    else:
        return redirect(url_for('failure'))



if __name__ == '__main__':
    app.run(debug=True)
