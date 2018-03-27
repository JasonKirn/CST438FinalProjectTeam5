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




#mongoDB test
#set mongo URI

#TODO: connection isn't right and it's causing authentication error.
#how to get port number needed for mlab?
#connection = pymongo.MongoClient('mongodb://jasonkirn:password123@ds221258.mlab.com:21258/beammeupscotty')
#db = connection['beammeupscotty']
#db.authenticate('jasonkirn', 'password123')

#client = MongoClient("mongodb://jasonkirn:password123@ds221258.mlab.com:21258/beammeupscotty")
#db = client['prod-db']
#mydb = client['test-database']



#result = mydb.users.find()
#for document in result:
#    print document


#client = MongoClient('mongodb://jasonkirn:password123@ds221258.mlab.com:21258/beammeupscotty')

#create database mongo client instance
#db = client.test_database

#get collection from database instance
#collection = db.test_collection
#db.siteUsers.find_one()
#pprint.pprint(collection.find_one())

# Host home.html as the home directory webpage (at '/').
@app.route('/')
def hello():
    #return db.siteUsers.find_one()
    return render_template('home.html')
    
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
