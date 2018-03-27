import os
import pprint
import pymongo
from flask import Flask, render_template
from pymongo import MongoClient
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'beammeupscotty'
app.config['MONGO_URI'] = 'mongodb://Jason:password123@ds213229.mlab.com:13229/beammeupscotty'

mongo = PyMongo(app)

# Host home.html as the home directory webpage (at '/').
@app.route('/')
def hello():
    return render_template('home.html')

#Accessed by adding on /add to url.  It will insert a sample user into mlab db
@app.route('/add')
def addSiteUser():
    user = mongo.db.siteUsers
    user.insert({'name' : 'testUserName'})
    return 'Added User!'
    
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
