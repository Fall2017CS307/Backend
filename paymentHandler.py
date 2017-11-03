from flask import Flask, render_template, request, redirect, url_for
import stripe
from userHandler import userHandler
from utils.dbConn import dbConn
import MySQLdb
from jsonReturn import apiDecorate
import json
import models
import os

class paymentHandler():

    @staticmethod
    def pay():

        customer = stripe.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=99,
            currency='usd',
            description='The Product'

        )

        if charge.paid :

            print(customer.email)
            session = dbConn().get_session(dbConn().get_engine())


            s = str(customer.email)


            curUser = session.query(models.User).filter(models.User.email == s).first()
            print(customer.email)


            if(curUser is None):
                return "FAILURE"

            else:
                curUser.balance = curUser.balance + amount
                session.commit()
                return "SUCCESS. THANKS FOR THE PAYMENT"

        else:
            return "FAILURE"
