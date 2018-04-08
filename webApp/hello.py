import os
import pprint
import pymongo
from flask import Flask, render_template, url_for, request, session, redirect, make_response, send_from_directory
from pymongo import MongoClient
from flask_pymongo import PyMongo
import bcrypt
#from flask_bcrypt import bcrypt
#Note: Do not use flask_bcrypt anymore, overwrites some of bcrypt's functions and does not allow us
#to compare passwords on login

app = Flask(__name__)
app.secret_key = '6ab7d1f456ee6d2630c670b1a025ed2fbd86fdfb31d89a7d'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app.config['MONGO_DBNAME'] = 'beammeupscotty'
app.config['MONGO_URI'] = 'mongodb://Jason:password123@ds213229.mlab.com:13229/beammeupscotty'
app.config['SECRET_KEY'] = '6ab7d1f456ee6d2630c670b1a025ed2fbd86fdfb31d89a7d'

mongo = PyMongo(app)

# Host home.html as the home directory webpage (at '/').
@app.route('/')
def hello():
    #check if a user is logged in and send them to login page if they're not
    #but currently just logs out for faster testing, changing later
    #if it doesn't redirect to logout, the login state will be persistent
    if 'username' in session:
        return redirect(url_for('home'))
        
    return render_template('login.html')

# Admin login will be used for going to admin page for checking logs.
@app.route('/adminLogin')
def admin():
    if 'username' in session:
        return redirect(url_for('home'))
    admin = mongo.db.siteAdmin
    
@app.route('/friendrequests')
def friendrequest():
    return ""
    
#Currently making endpoint to test adding friends to a user
@app.route('/addfriend/<userToAdd>')
def addfriend(userToAdd):
    users = mongo.db.siteUsers
    user = users.find_one({'name' : session['username']})
    
    #if userToAdd is not None:
    #    return "This is the username: " + userToAdd
    
    for x in range(1, 11):
        friendString = 'friend' + str(x)
        #friend(x) slot is found, keep looking for new friend slot
        #Note: This syntax must be used to check over nonexistant dict's, otherwise keyError
        if friendString in user:
            continue
        #friend(x) is not found, add new friend(x)
        else:
            users.update(
                {'name' : session['username'] },
                { '$set' : { friendString : userToAdd } }
            )
            return "New friend " + userToAdd + " added, you (" + session['username'] + ") currently have " + str(x) + " friends" 
    
    return "10 friends already added"
    

@app.route('/home')
def home():
    return render_template('home.html')
    
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
        #TODO: Figure out why user variable won't show up on user.html even though it's passed
        #and used in the same way it is used in the tutorial.
        #return siteUser + "   " + sessionUser
        if siteUser == sessionUser:
            return render_template('sessionUser.html', user=user, siteUser=siteUser, posts=posts)
        else:
            return render_template('user.html', sessionUser=sessionUser, user=user, posts=posts )
        #return statement works, return a template now
        #return "This is the userpage of " + siteUser

    return "Uh oh. The user page you're looking for doesn't seem to exist."

#Used for testing purposes only, edit it if you'd like for further testing
@app.route('/test')
def test():
    if 'username' in session:
        users = mongo.db.siteUsers
        user = users.find_one({'name' : session['username']})
        return "Hello " + session['username'] + " here is your profile description.  If it loads here correctly, that means it was an asynchronous call: " + "\n" + user['profileDescription']
        
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
            
            #set the user's 10 friendslots to null once their account is created
            #users.update(
            #    { 'name': session['username'] },
            #    { '$push': { 'friends' : {
            #        'friend1' : '',
            #        'friend2' : '',
            #        'friend3' : '',
            #        'friend4' : '',
            #        'friend5' : '',
            #        'friend6' : '',
            #        'friend7' : '',
            #        'friend8' : '',
            #        'friend9' : '',
            #        'friend10' : ''}}}
            #)
            users.update(
                { 'name': session['username'] },
                { '$set' : { 'friend1' : 'dog', 'friend2' : 'fish', 'friend3' : 'duck' } }
            )
            #users.update(
            #    { 'name': session['username'] },
            #    { '$push': { 'friends' : { '$each': ['testFriend1', '', '', '', '', '', '', '', '', ''] }}}
            #)
            
            
            #users.update(
            #   { 'name': session['username'] },
            #   { '$push': { 'scores': { '$each': [ 90, 92, 85 ] } } }
            #)
            
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
            { '$set': { 'colorInterests' : {
                'interest1' : request.form.get('interest1'),
                'interest2' : request.form.get('interest2'),
                'interest3' : request.form.get('interest3'),
                'interest4' : request.form.get('interest4')}}}#,
            #{ '$push': {'profileDescription' : request.form.get('profileDescription')}}
        )
        
        users.update(
            { 'name': session['username'] },
            { '$set': { 'profileDescription' : request.form.get('profileDescription')}}
        )
        
        
        
        #if request.form.get('interest1') is None:
        #    return "interest1 was not checked"
    
        #this will return red like the request.form.get('interest1'),
        #but both produce errors when the optional field isn't filled
        return redirect(url_for('home'))
        #return request.form.get('profileDescription') + " " + sessionUser['name'] + sessionUser['profileDescription']
    
    #request.method is GET
    return render_template('editProfile.html')

'''
@app.route('/register/<filename>')
def send_image(filename):
    return send_from_directory("tempIMG", filename)

#Code for displaying images in createProfile.html
@app.route('/images')
def images():
    image_names = os.listdir('./tempIMG')
    return render_template("createProfile.html", image_names=image_names)
'''
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
    app.run(debug=True)
    app.run()
    
app.run(host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))