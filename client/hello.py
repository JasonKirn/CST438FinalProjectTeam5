import os
import pprint
import pymongo
from flask import Flask, render_template, url_for, request, session, redirect
from pymongo import MongoClient
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt

app = Flask(__name__)

#Put app in Bcrypt wrapper so that we can hash passwords for security
bcrypt = Bcrypt(app)

app.config['MONGO_DBNAME'] = 'beammeupscotty'
app.config['MONGO_URI'] = 'mongodb://Jason:password123@ds213229.mlab.com:13229/beammeupscotty'

mongo = PyMongo(app)

# Host home.html as the home directory webpage (at '/').
@app.route('/')
def hello():
    #check if user is logged in and send them to login page if they're not
    if 'username' in session:
        return render_template('home.html')
        
    return render_template('login.html')
        
#Accessed by adding on /add to url.  It will insert a sample user into mlab db
@app.route('/add')
def addSiteUser():
    user = mongo.db.siteUsers
    user.insert({'name' : 'testUserName'})
    return 'Added User!'
    
@app.route('/login')
def login():
    return render_template('login.html')
    
#methods makes sure it accepts POST and GET request methods
@app.route('/register', methods=['POST', 'GET'])
def register():
    #check if username already exists
    if request.method == 'POST':
        users = mongo.db.siteUsers
        existingUser = users.find_one({'name' : request.form['username']})
        
        if existingUser is None:
            #based off most recent version, seems to generate salt automatically with value of 12?
            hashpass = bcrypt.generate_password_hash(request.form['pass'])
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            #create session for newly registered user
            session['username'] = request.form['username']
            return redirect(url_for('home.html'))
            
        return 'Username already exists'
        
    #request.method is GET
    return render_template('register.html')
    
if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)
    
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
