import os
import pprint
import pymongo
from flask import Flask, render_template, url_for, request, session, redirect
from pymongo import MongoClient
from flask_pymongo import PyMongo
import bcrypt
#from flask_bcrypt import bcrypt
#Note: Do not use flask_bcrypt anymore, overwrites some of bcrypt's functions and does not allow us
#to compare passwords on login

app = Flask(__name__)
app.secret_key = 'mysecret'

app.config['MONGO_DBNAME'] = 'beammeupscotty'
app.config['MONGO_URI'] = 'mongodb://Jason:password123@ds213229.mlab.com:13229/beammeupscotty'
app.config['SECRET_KEY'] = 'mysecret'

mongo = PyMongo(app)

# Host home.html as the home directory webpage (at '/').
@app.route('/')
def hello():
    #check if user is logged in and send them to login page if they're not
    if 'username' in session:
        return redirect(url_for('test'))
        
    return render_template('login.html')

#Used for testing purposes only
@app.route('/test')
def test():
    if 'username' in session:
        return "Hello " + session['username']
        
#Accessed by adding on /add to url.  It will insert a sample user into mlab db
@app.route('/add')
def addSiteUser():
    user = mongo.db.siteUsers
    user.insert({'name' : 'testUserName'})
    return 'Added User!'
    
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.siteUsers
    loginUser = users.find_one({'name' : request.form['username']})
    
    if loginUser is not None:
        isSamePassword = bcrypt.hashpw(request.form['pass'].encode('utf-8'), loginUser['password'].encode('utf-8'))

        if isSamePassword:
            #once logged in, work with session cookie to have the experience of a user being logged in
            return 'You are now logged in as ' + session['username']
        
    return 'username or password incorrect'
    
#methods makes sure it accepts POST and GET request methods
@app.route('/register', methods=['POST', 'GET'])
def register():
    #check if username already exists
    if request.method == 'POST':
        users = mongo.db.siteUsers
        existingUser = users.find_one({'name' : request.form['username']})
        
        if existingUser is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            #create session for newly registered user
            session['username'] = request.form['username']
            
            #TODO: redirect into pages where the user fills out information about them for profile
            return redirect(url_for('test'))
            
        return 'Username already exists'
        
    #request.method is GET
    return render_template('register.html')
    
    
#Heroku note: app.secret_key may need to be moved outside of if since heroku doesn't reach this if
if __name__ == '__main__':
    app.run(debug=True)
    app.run()
    
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))

#TODO: Kill session variable when app is closed or put logout feature to kill it