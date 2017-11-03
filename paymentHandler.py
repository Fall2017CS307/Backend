from flask import Flask, render_template, request, redirect, url_for
import stripe

app = Flask(__name__)

pub_key = 'pk_test_fOAnrRLEB5cDZMCipafCb71E'
secret_key = 'sk_test_I54z4p3XASvKZAfuwhmDPvlN'

stripe.api_key = secret_key

@app.route('/')
def index():
    return render_template('index.html', pub_key=pub_key)

@app.route('/thanks')
def thanks():
    return render_template('thanks.html')

@app.route('/pay', methods=['POST'])
def pay():

    customer = stripe.Customer.create(email=request.form['stripeEmail'], source=request.form['stripeToken'])

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=99,
        currency='usd',
        description='The Product'
        token=source
    )

    if(charge.paid)
        session = dbConn().get_session(dbConn().get_engine())
        curUser = session.query(models.User).filter(models.User.email == email).first()
        curUser.balance = curUser.balance + amount
        session.commit()
        return redirect(url_for('thanks'))

    else
        return redirect(url_for('failure'))


if __name__ == '__main__':
    app.run(debug=True)
