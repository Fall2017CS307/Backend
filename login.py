from flask import Flask, request
import MySQLdb

app = Flask(__name__)

# DATABASE CONNECT... CALL IT DB

cur = table_name.cursor()

# route for handling the login page logic
@app.route('/login', methods=[POST'])
def login():

    error = "Invalid credentials"

    if request.method == 'POST':

        username = request.form.get['username']
        password = request.form.get['password']

        if(cur.execute(SELECT EXISTS(SELECT * FROM table_name WHERE username=username)):


            cur.execute(SELECT password FROM table_name WHERE username=username LIMIT 1);

            pwd = cursor.fetchone()

            if(pwd == password)
                return redirect(url_for('home'))
                #SUCCESS

        else:


            return render_template('login.html')




if __name__ == '__main__':
    app.run(debug=true)
