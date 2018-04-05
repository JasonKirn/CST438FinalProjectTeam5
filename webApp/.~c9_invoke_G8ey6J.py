import os
import pprint
import pymongo
from flask import Flask, render_template, url_for, request, session, redirect
from pymongo import MongoClient
from flask_pymongo import PyMongo
import bcrypt
#from flask_bcrypt import bcrypt


#SESSION_TYPE = 'mongodb'

app = Flask(__name__)
app.secret_key = 'mysecret'

#import myapp.views
#sess = Session()

#Put app in Bcrypt wrapper so that we can hash passwords for security
#bcrypt = Bcrypt(app)

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
        #return render_template('home.html')
        
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
        #loginUser['password']
        
        #pwHash = bcrypt.generate_password_hash(request.form['pass']).decode('utf-8')
        
        ### DEBUG CODE ###
        isSamePassword = bcrypt.hashpw(request.form['pass'].encode('utf-8'), loginUser['password'].encode('utf-8'))
        #pwHash2 = bcrypt.generate_password_hash(request.form['pass']).decode('utf-8')
        #pwHash3 = bcrypt.generate_password_hash(request.form['pass']).decode('utf-8')
        #pwHash4 = bcrypt.generate_password_hash(request.form['pass']).decode('utf-8')
        #correctPass = bcrypt.check_password_hash(pwHash, 'a')#loginUser['password'])
        
        if isSamePassword:
            return ''
        
        #return request.form['pass'] + "<br />" +loginUser['password']+"<br />"+pwHash + " " + pwHash2 + " " + pwHash3 + " " + pwHash4 + " " + "<br />" + str(correctPass)
        ### END ####
        #if correctPass is True:
        #if bcrypt.generate_password_hash(request.form['pass'].encode('utf-8'), loginUser['password'].encode('utf-8')) == loginUser['password'].encode('utf-8'):
        #    session['username'] = request.form['username']
        #    return redirect(url_for('test'))
        #return 'Incorrect username/password combination'
    
    #once logged in, work with session cookie to have the experience of a user being logged in
    return 'username or password incorrect'
    #return render_template('login.html')
    
#methods makes sure it accepts POST and GET request methods
@app.route('/register', methods=['POST', 'GET'])
def register():
    #check if username already exists
    if request.method == 'POST':
        users = mongo.db.siteUsers
        existingUser = users.find_one({'name' : request.form['username']})
        
        if existingUser is None:
            #based off most recent version, seems to generate salt automatically with value of 12
            #hashpass = bcrypt.generate_password_hash(request.form['pass'])
            hashpass = bcrypt.hashpw(request.form['pass'], )
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            #create session for newly registered user
            session['username'] = request.form['username']
            return redirect(url_for('test'))
            
        return 'Username already exists'
        
    #request.method is GET
    return render_template('register.html')
    
    
#Heroku note: app.secret_key may need to be moved outside of if since heroku doesn't reach this if
if __name__ == '__main__':
#    app.secret_key = 'mysecret'
#    app.config['SESSION_TYPE'] = 'mongodb'
    
#    sess.init_app(app)
    
    app.run(debug=True)
    app.run()
    
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))

#TODO: Kill session variable when app is closed or put logout feature to kill it