twitter = oauth.remote_app('twitter', 
base_url ='https://api.twitter.com/oauth2/token', 
request_token_url = 'https://api.twitter.com/oauth/request_token',
access_token_url = 'https://api.twitter.com/oauth/access_token',
authorize_url = 'https://api.twitter.com/oauth/authenticate',
consumer_key = 'oQrr2yblVu55dnV1svNPvqU1m',
consumer_secret = 'ChVz3zgUWm5TGtHALl0LjPrCbI9Cxq6w3hrZTFReFyhnfZOuwx')

#api = twitter.Api( consumer)


@twitter.tokengetter
def get_twitter_token():
    return session.get('twitter_token')

@app.route('/twitter')
def twitter_index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect((url_for('twitterlogin')))
    access_token = access_token[0]
    
    return render_template('editProfile.html')
    
@app.route('/twitterlogin')
def twitterlogin():
    return twitter.authorize(callback=url_for('oauth_authorized',
        next = request.args.get('next') or request.referrer or None))
 
 
@app.route('/twitterlogout')
def twitterlogout():
    session.pop('screen_name', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))
    
@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('twitter')
    if resp is None:
        return redirect(next_url)
    access_token = resp['oauth_token']
    session['access_token'] = access_token
    
    session['twitter_token'] = (
        resp['oauth_token'],
        resp['oauth_token_secret']
        )
    return redirect(url_for('editprofile'))