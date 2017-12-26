CLIENT_ID = "1032379959199-68d98qngcqprtdnuq1dqjsl7ouagsvt3.apps.googleusercontent.com"
CLIENT_SECRET = "4Pc4NXqoyWR4P9MdPMoG9iBO"
GOOGLE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
REDIRECT_URL = "https://oauth2-demo-183302.appspot.com/redirect"

import os
import httplib, urllib
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
#from google.appengine.api import users
from google.appengine.ext import ndb
import webapp2
import json
import string
import random
import logging





class State(ndb.Model):
    value = ndb.StringProperty(required=True)

def new_secure_state(length=18):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
    #https://stackoverflow.com/a/23728630/2213647 (cryptographically random string-- "SystemRandom()")

class redirectHandler(webapp2.RequestHandler):
    def get(self,):

        # [process server auth response]
        server_state = self.request.get('state')
        code = self.request.get('code')

        query = State.query(State.value == server_state)
        client_state = query.get()

        if server_state != client_state.value:
            path = os.path.join(os.path.dirname(__file__), 'fail.html')
            self.response.set_status(401)
            self.response.out.write(template.render(path, template_values))
            return
        client_state.key.delete()

        # [POST response to server]
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'grant_type': 'authorization_code',
		           'code': code,
		           'client_id': CLIENT_ID,
		           'client_secret': CLIENT_SECRET,
	               'redirect_uri': REDIRECT_URL
        }
        result = urlfetch.fetch(url='https://www.googleapis.com/oauth2/v4/token',
                                headers=headers,
                                payload=urllib.urlencode(payload),
                                method=urlfetch.POST)
        res = json.loads(result.content)
        logging.debug("POST Result:")
        logging.debug(res)

        # [authorization!]
        auth_token = "Bearer " + res['access_token']

        # [GET user info with token]
        headers = {'Authorization': auth_token }
        response = urlfetch.fetch(url='https://www.googleapis.com/plus/v1/people/me',
                                  headers=headers,
                                  method=urlfetch.GET)
        res = json.loads(response.content)
        logging.debug("GET Response:")
        logging.debug(res)

        # [fill in template info]
        user_name = res['name']
        template_values = {
			'displayName': res['displayName'],
			'familyName': user_name['familyName'],
			'givenName': user_name['givenName'],
			'url': res['url'],
			'state': server_state
		}

        path = os.path.join(os.path.dirname(__file__), 'redirect.html')
        self.response.out.write(template.render(path, template_values))

class MainPage(webapp2.RequestHandler):
    def get(self):
        # [create a state string]
        state = new_secure_state()
        ndb_state = State(value=state)
        ndb_state.put()

        # [link the button to Google's OAuth]
        url = GOOGLE_URL + "?response_type=code&client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URL + "&scope=email&state=" + state
        template_values = { 'url': url }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
	('/', MainPage),
	('/redirect', redirectHandler)
], debug=True)
