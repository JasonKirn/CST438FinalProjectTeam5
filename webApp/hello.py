#!/usr/bin/python
import os
import pprint
import pymongo
from flask import Flask, flash, render_template, url_for, request, session, redirect, make_response, send_from_directory
from flask import Flask, render_template, url_for, request, session, redirect, make_response, send_from_directory, jsonify
from pymongo import MongoClient
from flask_pymongo import PyMongo
import bcrypt
import tweepy
from tweepy import Stream
from tweepy.streaming import StreamListener
from key import key
import requests


app = Flask(__name__)
app.secret_key = '6ab7d1f456ee6d2630c670b1a025ed2fbd86fdfb31d89a7d'

consumer_key = 'oQrr2yblVu55dnV1svNPvqU1m'
consumer_secret = 'ChVz3zgUWm5TGtHALl0LjPrCbI9Cxq6w3hrZTFReFyhnfZOuwx'
#NOTE: WILL PROBABLY NEED TO CHANGE WHEN DEPLOYED TO A HEROKU LINK
#callback = 'http://cst438finalproject-jasonkirn.c9users.io:8080/callback'
callback = 'https://https://cst438finalprojectteam5.herokuapp.com/callback'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.config['MONGO_DBNAME'] = 'beammeupscotty'
app.config['MONGO_URI'] = 'mongodb://Jason:password123@ds213229.mlab.com:13229/beammeupscotty'
app.config['SECRET_KEY'] = '6ab7d1f456ee6d2630c670b1a025ed2fbd86fdfb31d89a7d'

search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
details_url = "https://maps.googleapis.com/maps/api/place/details/json"

mongo = PyMongo(app)

INTERESTS =[ 
    'interest1', 'interest2', 'interest3', 'interest4', 
    'interest5', 'interest6', 'interest7', 'interest8', 
    'interest9', 'interest10', 'interest11', 'interest12', 
    'interest13', 'interest14', 'interest15', 'interest16', 
    'interest17', 'interest18' 
]

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
    
    #FIXUP May want different functionality here for no source user.
    if(otherUser is None):
        return redirect(url_for('notifications'))    
    
    for x in range(1, 11):
        friendString = 'friend' + str(x)
        
        if user[friendString] == '':
            otherUserFullFriendList = False
            otherUserFriendSlot = friendString
            break
        else:
            otherUserFullFriendList = True
            
    if otherUserFullFriendList == True:
        flash("Cannot add friend. " + otherUserName + "'s friend list is full.")
        return redirect(url_for('notifications'))
        
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
        flash("Cannot add friend. Your friend list is full.")
        return redirect(url_for('notifications'))
        
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
        flash("Cannot send request to " + userToAdd + ". Your friend list is full.")
        return redirect(url_for('user', siteUser=userToAdd))
    
    #checking if their friend list has open slots
    for x in range(1, 11):
        friendString = 'friend' + str(x)
        
        if otherUser[friendString] == '':
            fullOtherUserFriendList = False
            break;
        else:
            fullOtherUserFriendList = True
            
    if fullOtherUserFriendList == True:
        flash("Cannot send request to " + userToAdd + ". Their friend list is full.")
        return redirect(url_for('user', siteUser=userToAdd))
        
    for x in range(1, 11):
        notificationString = 'notification' + str(x)
        
        if otherUser[notificationString] == '':
            notificationMessage = "Friend request from " + session['username']
            updateEntry(userToAdd, notificationString, notificationMessage)
            flash("Friend request sent to " + userToAdd)
            return redirect(url_for('user', siteUser=userToAdd))
        else:
            fullNotificationList = True
    
    flash("Error in adding " + userToAdd)
    return redirect(url_for('user', siteUser=userToAdd))

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
    if(user is None):
        return render_template('login.html')
    else:
        return render_template('home.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('hello'))
    
def error():
    return "Something went wrong."

#endpoint for userprofile, siteUser must be a user in the db for it to work.
@app.route('/users/<siteUser>')
def user(siteUser):
    if siteUser is None:
        return error()
    #check if a user is logged in, if not they can't view a profile and are sent to login
    if 'username' not in session:
        return render_template('login.html')
    
    sessionUserName = session['username']
    selectedUser = getUser(siteUser)
    print(selectedUser)
    print(siteUser)
    if((selectedUser is not None)):
        if('twitterUser' not in selectedUser):
            twitterUser = None
            twitterUserLink = None
        else:
            twitterUser = selectedUser['twitterUser']
            if('twitterUserLink' not in selectedUser):
                twitterUserLink = None
            else:
                twitterUserLink = selectedUser['twitterUserLink']

    if selectedUser is not None:
        
        #FIXUP Remove posts for styling.
        posts = [
            {'author' : siteUser, 'body': 'Test post #1'}    
        ]
        print(twitterUser)
        print(twitterUserLink)
        if siteUser == sessionUserName:
            return render_template('sessionUser.html', user=selectedUser, posts=posts, twitterUser = twitterUser,twitterUserLink = twitterUserLink)
        else:
            return render_template('user.html', user=selectedUser, posts=posts, twitterUser = twitterUser,twitterUserLink = twitterUserLink)

    return "Uh oh. The user page you're looking for doesn't seem to exist."

@app.route('/testPost', methods=['POST', 'GET'])
def testPost():
    if request.method == 'POST':
        return request.form['value']
        
    return "You shouldn't be here :eyes:"
    
#Used for testing purposes only, edit it if you'd like for further testing
#@app.route('/test')
#def test():
#    if 'username' in session:
#        user = getUser(session['username'])
#        for userCursor in users.find():
#            return userCursor['name']
#        return "Hello " + session['username'] + " here is your profile description.  If it loads here correctly, that means it was an asynchronous call: " + "\n" + user['profileDescription']
    
@app.route('/login', methods=['POST'])
def login():
    loginUser = getUser(request.form['username'])
    
    if loginUser is not None:
        if (loginUser['password'] is None):
            return error()
        isSamePassword = bcrypt.hashpw(request.form['pass'].encode('utf-8'), loginUser['password'].encode('utf-8')) == loginUser['password'].encode('utf-8')

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

@app.route('/updatelocation', methods=['POST'])
def updatelocation():
    
    location = json.loads(request.data)
    
    users = mongo.db.siteUsers
    user = users.find_one({'name' : session['username']})
    users.update(
        { 'name': session['username'] },
        {'$set': {'location': '{{"lat": {}, "lng": {}}}'.format(location['lat'], location['lng']) }
        })
        
    return 'OK'

@app.route('/editprofile', methods=['POST', 'GET'])
def editprofile():
    sessionUser = getUser(session['username'])
    if(sessionUser is None):
        return error()
    if request.method == 'POST':
        #Notes:
        #1. request.form.get is needed for optional form fields
        #2. If a field isn't filled out, it will be 'something' : null in DB
        #3. can also maybe use find_one_and_update with pymongo 2.9 or above
        userName = session['username']
        for i in range(1,19):
            setInterest(userName, i, request.form.get('interest'+str(i)))
        updateEntry(userName, 'profileDescription', request.form.get('profileDescription'))
        updateEntry(userName, 'avatarImage', request.form.get('profileCharacter'))
        return render_template('home.html', user=sessionUser)
        #return redirect(url_for('home')
        #4/21 FIX
    #request.method is GET
    return render_template('editProfile.html', sessionUser=sessionUser)

#Code for getting matches between users
@app.route('/matches')
def matches():
    matchScores = []
    users = mongo.db.siteUsers
    user = getUser(session['username'])
    if((users is None) or (user is None)):
        return error()
    for iterUser in users.find():
        if iterUser == user: continue
        score = sum([iterUser[i] == user[i] for i in INTERESTS if i in iterUser and i in user])
        if score > 3:
            matchScores.append((score, iterUser['name'], iterUser))
    ranked_matches = sorted(matchScores, reverse=True)
    matched_users = [x[2] for x in ranked_matches[:5]]
    return render_template('matches.html', user=user, matched_users=matched_users)

@app.route('/updateStatus', methods=['POST'])
def btnTest():
    if request.method == 'POST':
	    sessionUser = getUser(session['username'])
	    if 'username' in session:
		    myStatus = request.form['statusTextField']
		    updateEntry(sessionUser, 'profileStatus', request.form.get('statusTextField'))
	    return render_template('home.html', user=sessionUser)
    return "Null; bad return."

@app.route('/twitterauth')
def twitterauth():
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret,callback)
    url = auth.get_authorization_url()
    session['request_token'] = auth.request_token
    return redirect(url)
	
@app.route('/callback')
def twitter_callback():
    request_token = session['request_token']
    del session['request_token']

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret, callback)
    auth.request_token = request_token
    verifier = request.args.get('oauth_verifier')
    auth.get_access_token(verifier)
    '''
    Information to be stored in the database for the user 
    
    usersToken = auth.access_token
    usersSecret = auth.access_token_secret
    
    Then you run this
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(usersToken, usersSecret)
    api = tweepy.API(auth)
    
    user = api.me()
    
    #instead of session, twitterUserLink would be stored in the database
    session['twitterUserLink'] = "https://twitter.com/" + user.screen_name
    return redirect(url_for('editprofile'))
    
    
    This code should be able to run without redirecting to /twitterapp
    If not then 
    '''
    #should be irrelevant after implementing above code
    session['token'] = (auth.access_token, auth.access_token_secret)

    return redirect('/twitterapp')
    
@app.route('/twitterapp')
def request_twitter():
    token, token_secret = session['token']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret,callback)
    auth.set_access_token(token, token_secret)
    api = tweepy.API(auth)
    user = api.me()
    if(user is None):
        return error()
    if(user.screen_name is None):
        return error()
    
    updateEntry(session['username'], 'twitterUser', user.screen_name)
    #instead of session, twitterUserLink would be stored in the database
    updateEntry(session['username'], 'twitterUserLink', "https://twitter.com/" + user.screen_name)
    print(user.screen_name)
    usr = getUser(session['username'])
    print(usr['twitterUser'])
    print(usr['twitterUserLink'])
    #twitterUserName = user.screen_name
    
    #twitterFileName = "templates/" + twitterUserName + ".txt"
    
    #public_tweets = api.user_timeline()
    
    '''
    myTweetFile = open(twitterFileName,'w+')
    
    for i in range(0,10):
        myTweetFile.write(public_tweets[i].text.encode('utf-8'))
        myTweetFile.write("\n")
    
    myTweetFile.close()
    '''
    #session['twitterFirstTweet'] = public_tweets[1].text
    #session['twitterSecondTweet'] = public_tweets[2].text
    #for tweet in public_tweets:
       # allTweets += str(tweet.text)
    #return render_template('sessionUser.html', singleTweet = singleTweet)
    return redirect(url_for('editprofile'))


#Heroku note: app.secret_key may need to be moved outside of if since heroku doesn't reach this if
if __name__ == '__main__':
    app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)), debug=True)