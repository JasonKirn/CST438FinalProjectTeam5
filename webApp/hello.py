#!/usr/bin/python
import os
import pprint
import pymongo
from flask import Flask, render_template, url_for, request, session, redirect, make_response, send_from_directory, jsonify
from pymongo import MongoClient
from flask_pymongo import PyMongo
from flask_login import LoginManager, login_user
import bcrypt
from key import key
import requests

app = Flask(__name__)
app.secret_key = '6ab7d1f456ee6d2630c670b1a025ed2fbd86fdfb31d89a7d'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.config['MONGO_DBNAME'] = 'beammeupscotty'
app.config['MONGO_URI'] = 'mongodb://Jason:password123@ds213229.mlab.com:13229/beammeupscotty'
app.config['SECRET_KEY'] = '6ab7d1f456ee6d2630c670b1a025ed2fbd86fdfb31d89a7d'

search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
details_url = "https://maps.googleapis.com/maps/api/place/details/json"

mongo = PyMongo(app)

#login_manager = LoginManager()

# Host home.html as the home directory webpage (at '/').
@app.route('/')
def hello():
    #check if a user is logged in and send them to login page if they're not
    #but currently just logs out for faster testing, changing later
    #if it doesn't redirect to logout, the login state will be persistent
    if 'username' in session:
        return redirect(url_for('home'))
        
    return render_template('login.html')

@app.route("/testGoogle", methods=["GET"])
def retrieve():
    return render_template('googleApiLayout.html')

@app.route("/googleApi")
def googleApi():
    
    return render_template('googleApi.html')

@app.route("/sendRequest/<string:query>")
def results(query):
	search_payload = {"key":key, "query":query}
	search_req = requests.get(search_url, params=search_payload)
	search_json = search_req.json()

	place_id = search_json["results"][0]["place_id"]

	details_payload = {"key":key, "placeid":place_id}
	details_resp = requests.get(details_url, params=details_payload)
	details_json = details_resp.json()

	#url = details_json["result"]["url"]
	url = "https://www.google.com"
	return jsonify({'result' : url})

@app.route('/friendlist')
def friendlist():
    users = mongo.db.siteUsers
    user = users.find_one({'name' : session['username']})

    return render_template('friendList.html', user=user);

@app.route('/acceptrequest/<notification>')
def acceptrequest(notification):
    users = mongo.db.siteUsers
    user = users.find_one({'name' : session['username']})
    
    notificationString = user[notification]
    otherUserName = notificationString[20:len(notificationString)]
    
    otherUser = users.find_one({'name' : otherUserName})

    otherUserFullFriendList = False
    otherUserFriendSlot = ""
    
    for x in range(1, 11):
        friendString = 'friend' + str(x)
        
        if user[friendString] == '':
            otherUserFullFriendList = False
            otherUserFriendSlot = friendString
            break
        else:
            otherUserFullFriendList = True
            
    if otherUserFullFriendList == True:
        return "Cannot add friend." + otherUserName + "'s friend list is full."
        
    userFullFriendList = False
    userFriendSlot = ""
        
    for y in range(1, 11):
        friendString = 'friend' + str(y)
        
        if otherUser[friendString] == '':
            userFullFriendList = False
            userFriendSlot = friendString
            break
        else:
            userFullFriendList = True
    
    if userFullFriendList == True:
        return "Cannot add friend. Your friend list is full."
        
    users.update(
        { 'name' : session['username'] },
        { '$set' : {
            notification : "",
            userFriendSlot : otherUserName } }
    )    
    
    users.update(
        { 'name' : otherUserName },
        { '$set' : { otherUserFriendSlot : session['username'] } }
    )
    
    return redirect(url_for('notifications'))

@app.route('/declinerequest/<notification>')
def declinerequest(notification):
    users = mongo.db.siteUsers

    users.update(
        { 'name' : session['username'] },
        { '$set' : { notification : "" } }
    )
    
    return redirect(url_for('notifications'))

#Deals with friend requests and status update notifications
@app.route('/notifications')
def notifications():
    users = mongo.db.siteUsers
    user = users.find_one({'name' : session['username']})

    return render_template('notifications.html', user=user);
    
#Currently making endpoint to test adding friends to a user
@app.route('/addfriend/<userToAdd>')
def addfriend(userToAdd):
    users = mongo.db.siteUsers
    user = users.find_one({'name' : session['username']})
    otherUser = users.find_one({'name' : userToAdd })

    fullUserFriendList = False
    fullOtherUserFriendList = False
    fullNotificationList = False
    
    #check session user friend slots
    for x in range(1, 11):
        friendString = 'friend' + str(x)
        
        if user[friendString] == '':
            fullUserFriendList = False
            break;
        else:
            fullUserFriendList = True
    
    if fullUserFriendList == True:
        return "Cannot send request to " + userToAdd + ". Your friend list is full."
    
    #checking if their friend list has open slots
    for x in range(1, 11):
        friendString = 'friend' + str(x)
        
        if otherUser[friendString] == '':
            fullOtherUserFriendList = False
            break;
        else:
            fullOtherUserFriendList = True
            
    if fullOtherUserFriendList == True:
        return "Cannot send request to " + userToAdd + ". Their friend list is full."
        
    for x in range(1, 11):
        notificationString = 'notification' + str(x)
        
        if otherUser[notificationString] == '':
            notificationMessage = "Friend request from " + session['username']
            users.update(
                { 'name' : userToAdd },
                { '$set' : { notificationString : notificationMessage } }
            )
            return "Friend request sent to " + userToAdd
        else:
            fullNotificationList = True
        
    return "There was an error in adding the other user"

@app.route('/home')
def home():
    users = mongo.db.siteUsers
    user = users.find_one({'name' : session['username']})
    return render_template('home.html', user=user)
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello'))

#endpoint for userprofile, siteUser must be a user in the db for it to work.
@app.route('/users/<siteUser>')
def user(siteUser):
    #check if a user is logged in, if not they can't view a profile and are sent to login
    if 'username' not in session:
        return render_template('login.html')
    
    users = mongo.db.siteUsers
    user = users.find_one({'name' : siteUser})
    sessionUser = session['username']
    
    if user is not None:
        posts = [
            {'author' : siteUser, 'body': 'Test post #1'}    
        ]

        if siteUser == sessionUser:
            return render_template('sessionUser.html', user=user, siteUser=siteUser, posts=posts)
        else:
            return render_template('user.html', sessionUser=sessionUser, user=user, posts=posts )

    return "Uh oh. The user page you're looking for doesn't seem to exist."

@app.route('/testPost', methods=['POST', 'GET'])
def testPost():
    if request.method == 'POST':
        return request.form['value']
        
    return "You shouldn't be here :eyes:"
    
#Used for testing purposes only, edit it if you'd like for further testing
@app.route('/test')
def test():
    if 'username' in session:
        users = mongo.db.siteUsers
        user = users.find_one({'name' : session['username']})
        
        return "Hello " + session['username']
    
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.siteUsers
    loginUser = users.find_one({'name' : request.form['username']})
    
    if loginUser is not None:
        isSamePassword = bcrypt.hashpw(request.form['pass'].encode('utf-8'), loginUser['password'].encode('utf-8'))
        
        if isSamePassword:
            session['username'] = request.form['username']
            return redirect(url_for('home'))
        
    return 'username or password incorrect'
    
#methods makes sure it accepts POST and GET request methods
@app.route('/register', methods=['POST', 'GET'])
def register():
    
    if request.method == 'POST':
        users = mongo.db.siteUsers
        #check if username already exists
        existingUser = users.find_one({'name' : request.form['username']})
        
        if existingUser is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass})
            #create session for newly registered user
            session['username'] = request.form['username']
            
            users.update(
                { 'name': session['username'] },
                { '$set' : { 
                    'friend1' : 'dog', 
                    'friend2' : 'fish',
                    'friend3' : 'duck',
                    'friend4' : '',
                    'friend5' : '',
                    'friend6' : '',
                    'friend7' : '',
                    'friend8' : '',
                    'friend9' : '',
                    'friend10' : '' } }
            )
            
            users.update(
                { 'name' : session['username'] },
                { '$set' : { 
                    'notification1' : 'I am notification 1',
                    'notification2' : 'I am notification 2',
                    'notification3' : '',
                    'notification4' : '',
                    'notification5' : '',
                    'notification6' : '',
                    'notification7' : '',
                    'notification8' : '',
                    'notification9' : '',
                    'notification10' : ''} }
            )
            
            return redirect(url_for('editprofile'))
            
        return 'Username already exists'
        
    #request.method is GET
    return render_template('register.html')

@app.route('/editprofile', methods=['POST', 'GET'])
def editprofile():
    
    if request.method == 'POST':
        users = mongo.db.siteUsers
        
        #find the current session user in the database
        sessionUser = users.find_one({'name' : session['username']})

        #Notes:
        #1. request.form.get is needed for optional form fields
        #2. If a field isn't filled out, it will be 'something' : null in DB
        #3. can also maybe use find_one_and_update with pymongo 2.9 or above
        
        users.update(
            { 'name': session['username'] },
            { '$set': {'interest1' : request.form.get('interest1'),
                'interest2' : request.form.get('interest2'),
                'interest3' : request.form.get('interest3'),
                'interest4' : request.form.get('interest4'),
                'interest5' : request.form.get('interest5'),
                'interest6' : request.form.get('interest6'),
                'interest7' : request.form.get('interest7'),
                'interest8' : request.form.get('interest8'),
                'interest9' : request.form.get('interest9'),
                'interest10' : request.form.get('interest10'),
                'interest11' : request.form.get('interest11'),
                'interest12' : request.form.get('interest12'),
                'interest13' : request.form.get('interest13'),
                'interest14' : request.form.get('interest14'),
                'interest15' : request.form.get('interest15'),
                'interest16' : request.form.get('interest16'),
                'interest17' : request.form.get('interest17'),
                'interest18' : request.form.get('interest18')}}
        )
        
        users.update(
            { 'name': session['username'] },
            { '$set': { 'profileDescription' : request.form.get('profileDescription')}}
        )
        
        return redirect(url_for('home'))

    #request.method is GET
    return render_template('editProfile.html')

#Code for setting cookies
@app.route('/setcookie')
def setcookie():
    resp = make_response("SETCOOKIE abc, def")
    resp.set_cookie('abc', 'def')
    return resp 

#Code for getting cookies
@app.route('/getcookie')
def getcookie():
    cookieName = request.cookies.get('abc')
    return cookieName 

#Heroku note: app.secret_key may need to be moved outside of if since heroku doesn't reach this if
if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)), debug=True)