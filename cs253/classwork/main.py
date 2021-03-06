import re
from string import letters
import webapp2
from google.appengine.ext import db
import hmac

import redditups
import basehandler
import asciichan

SECRET = 'imsosecret'

def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))
    
def check_secure_val(h):
    val = h.split('|')[0]
    if h == make_secure_val(val):
        return val

class TableOfContents(basehandler.BaseHandler):
    def get(self):
        self.render('table-of-contents.html')
        
class Play(basehandler.BaseHandler):
    def get(self):
        self.render('/play.html')
        
class Rot13(basehandler.BaseHandler):
    def get(self):
        self.render('/rot13-form.html')
        
    def post(self):
        rot13 = ''
        text = self.request.get('text')
        if text:
            rot13 = text.encode('rot13')
        
        self.render('/rot13-form.html', text = rot13)
        
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)
    
class Signup(basehandler.BaseHandler):

    def get(self):
        self.render("signup-form.html")
    
    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
            
        params = dict(username = username, 
                      email = email)
        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True
    
        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True
    
        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True
    
        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.redirect('/unit2/welcome?username=' + username)

class Welcome(basehandler.BaseHandler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('/welcome.html', username = username)
        else:
            self.redirect('/unit2/signup')

class Cookies(basehandler.BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = 0
        visit_cookie_str = self.request.cookies.get('visits', '0')
        if visit_cookie_str:
            cookie_val = check_secure_val(visit_cookie_str)
            if cookie_val:
                visits = int(cookie_val)
                
        visits += 1
        
        new_cookie_val = make_secure_val(str(visits))

        self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)
        
        if visits > 100:
            self.write("You are the best ever!")
        else:
            self.write("You've been here %s times!" % visits)
            
app = webapp2.WSGIApplication([('/', TableOfContents),
                               ('/unit1/play', Play),
                               ('/unit2/rot13', Rot13),
                               ('/unit2/signup', Signup),
                               ('/unit2/welcome', Welcome),
                               ('/unit3/asciichan', asciichan.AsciiChan),
                               ('/unit4/cookies', Cookies),
                               ('/unit5/redditups', redditups.RedditUps)],
                               debug=True)