#!/usr/bin/python
import os
import pprint
import pymongo
from flask import Flask, render_template, url_for, request, session, redirect, make_response, send_from_directory
from pymongo import MongoClient
from flask_pymongo import PyMongo
import bcrypt
session
app = Flask(__name__)
app.secret_key = '6ab7d1f456ee6d2630c670b1a025ed2fbd86fdfb31d89a7d'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.config['MONGO_DBNAME'] = 'beammeupscotty'
app.config['MONGO_URI'] = 'mongodb://Jason:password123@ds213229.mlab.com:13229/beammeupscotty'
app.config['SECRET_KEY'] = '6ab7d1f456ee6d2630c670b1a025ed2fbd86fdfb31d89a7d'

mongo = PyMongo(app)

def getUser(name):
    users = mongo.db.siteUsers
    user = users.find_one({'name' : name})
    return user

def updateEntry(userName, key, value):
    users = mongo.db.siteUsers
    users.update(
        { 'name' : userName },
        { '$set' : { key : value } }
    )
def newUser(name, hashedPass):
    users = mongo.db.siteUsers
    users.insert({'name' : name, 'password' : hashedPass})

def setFriend(userName, index, friendName):
    friendString = 'friend' + str(index)
    updateEntry(userName, friendString, friendName)

def setNotification(userName, index, message):
    notificationString = 'notification' + str(index)
    updateEntry(userName, notificationString, message)
    
def setInterest(userName, index, interest):
    interestString='interest' + str(index)
    updateEntry(userName, interestString, interest)
    
# Host home.html as the home directory webpage (at '/').
@app.route('/')
def hello():
    #check if a user is logged in and send them to login page if they're not
    #but currently just logs out for faster testing, changing later
    #if it doesn't redirect to logout, the login state will be persistent
    if 'username' in session:
        return redirect(url_for('home'))
        
    return render_template('login.html')

#DELETE
@app.route('/testUser')
def testUser():
    thisUser = getUser(session['username'])
    return thisUser['name']
    
@app.route('/friendlist')
def friendlist():
    return render_template('friendList.html', user=getUser(session['username']));

@app.route('/acceptrequest/<notification>')
def acceptrequest(notification):
    user = getUser(session['username'])
    notificationString = user[notification]
    otherUserName = notificationString[20:len(notificationString)]
    
    otherUser = getUser(otherUserName)

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
        
    updateEntry(session['username'], notification, "")
    updateEntry(session['username'], userFriendSlot, otherUserName)
    updateEntry(otherUserName, otherUserFriendSlot, session['username'])
    return redirect(url_for('notifications'))

@app.route('/declinerequest/<notification>')
def declinerequest(notification):
    users = mongo.db.siteUsers
    updateEntry(session['username'], notification, "")
    return redirect(url_for('notifications'))

#Deals with friend requests and status update notifications
@app.route('/notifications')
def notifications():
    return render_template('notifications.html', user=getUser(session['username']));
    
#Currently making endpoint to test adding friends to a user
@app.route('/addfriend/<userToAdd>')
def addfriend(userToAdd):
    user = getUser(session['username'])
    otherUser = getUser(userToAdd)

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
            updateEntry(userToAdd, notificationString, notificationMessage)
            return "Friend request sent to " + userToAdd
        else:
            fullNotificationList = True
        
    return "There was an error in adding the other user"

#@app.route('/statusNotifyFriends')
#def statusUpdate():
#    users = mongo.db.siteUsers
#    user = users.find_one({'name' : session['username']})
#    for x in range(1, 11):
##        friendString = 'friend' + str(x)
 #       if user[friendString] != '':
 #           selectedFriend = users.find_one({'name'} : friendString)
            
                        
@app.route('/home')
def home():
    user = getUser(session['username'])
    if(user['profileStatus'] is None):
        return render_template('home.html')
    else:
        return render_template('home.html', statusPageText=user['profileStatus'])
    
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
    
    user = getUser(siteUser)
    sessionUser = getUser(session['username'])
    
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
        user = getUser(session['username'])
        return "Hello " + session['username'] + " here is your profile description.  If it loads here correctly, that means it was an asynchronous call: " + "\n" + user['profileDescription']
        
#Accessed by adding on /add to url.  It will insert a sample user into mlab db
@app.route('/add')
def addSiteUser():
    users = mongo.db.siteUsers
    users.insert({'name' : 'testUserName'})
    return 'Added User!'
    
@app.route('/login', methods=['POST'])
def login():
    loginUser = getUser(request.form['username'])
    
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
        existingUser = getUser(request.form['username'])
        
        if existingUser is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            newUser(request.form['username'], hashpass)
            #create session for newly registered user
            session['username'] = request.form['username']
            userName = session['username']
            updateEntry(userName, 'profileStatus', '')
            
            setFriend(userName,1,'dog')
            setFriend(userName,2,'fish')
            setFriend(userName,3,'duck')
            for i in range(4,11):
                setFriend(userName,i,'')

            setNotification(userName,1,'I am notification 1')
            setNotification(userName,2,'I am notification 2')
            for i in range(3,11):
                setNotification(userName,i,'')

            return redirect(url_for('editprofile'))
            
        return 'Username already exists'
        
    #request.method is GET
    return render_template('register.html')

@app.route('/editprofile', methods=['POST', 'GET'])
def editprofile():
    
    if request.method == 'POST':
        sessionUser = getUser(session['username'])
        #Notes:
        #1. request.form.get is needed for optional form fields
        #2. If a field isn't filled out, it will be 'something' : null in DB
        #3. can also maybe use find_one_and_update with pymongo 2.9 or above
        userName = session['username']
        for i in range(1,5):
            setInterest(userName, i, request.form.get('interest'+str(i)))
        
        updateEntry(userName, 'profileDescription', request.form.get('profileDescription'))

        return redirect(url_for('home'))

    #request.method is GET
    return render_template('editProfile.html')

@app.route('/updateStatus', methods=['POST'])
def btnTest():
    if request.method == 'POST':
        if 'username' in session:
            sessionUser = getUser(session['username'])
            myStatus = request.form['statusTextField']
            updateEntry(sessionUser, 'profileStatus', request.form.get('statusTextField'))
        return render_template('home.html', statusPageText=myStatus)
        #return welcome+""+statusText+"\n"+dbStatus
    return "Null; bad return."


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