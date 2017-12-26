#!/usr/bin/env python
CLIENT_ID = "----------------------------------------------.apps.googleusercontent.com"
CLIENT_SECRET = "------------------------"
GOOGLE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
#REDIRECT_URL = "https://localhost:8080/redirect"
REDIRECT_URL = "https://final-project-186875.appspot.com/redirect"

# [START imports]
import os
import httplib, urllib
from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
#import oauth2client.client as client
#import oauth2client.crypt as crypt

from oauth2client import client, crypt
import webapp2
import json
import string
import random
import logging
# [END imports]


# [START auth]
#====== Utils =========
def new_secure_state(length=18):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))
    #https://stackoverflow.com/a/23728630/2213647 (cryptographically random string-- "SystemRandom()")
def getParentKey(c, user_id):
    if user_id is not None:
        if c == 'dog':
            parent_key = ndb.Key(Dog, repr(user_id))
            logging.debug("returning Dog parent key")
            return parent_key
        if c == 'people':
            parent_key = ndb.Key(Person, repr(user_id))
            logging.debug("returning Person parent key")
            return parent_key
    else:
		return None

def parseToken(token):
    if token is not None:
        try:
            idinfo = client.verify_id_token(token, None)
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise crypt.AppIdentityError("wrong issuer")
            if idinfo['aud'] not in [CLIENT_ID]:
                raise crypt.AppIdentityError("Unrecognized client")
            userid = idinfo['sub']
            return userid
        except crypt.AppIdentityError:
            logging.debug("Expired User ID Token")
            return None
    else:
        return None

#===== Classes =======
class State(ndb.Model):
    value = ndb.StringProperty(required=True)

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
        id_token = res['id_token']

        template_values = {
            'auth_token': auth_token,
			'id_token': id_token
        }

        path = os.path.join(os.path.dirname(__file__), 'redirect.html')
        self.response.out.write(template.render(path, template_values))
# [END auth]


# [START Entities]
#for entity attribute info see "entity property reference" under  NDB Client Library Reference
class Person(ndb.Model):
    id = ndb.StringProperty()
    id_token = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    age = ndb.IntegerProperty()
    city = ndb.StringProperty()
    dogs = ndb.JsonProperty(repeated=True)
    recurring_client = ndb.BooleanProperty()

class Sport(ndb.Model):
    id = ndb.StringProperty()
    id_token = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True) #cardio, strength, wellness etc
    participants = ndb.JsonProperty() #recurring == NULL
    day = ndb.StringProperty()
    time = ndb.StringProperty()

class Dog(ndb.Model):
    id = ndb.StringProperty()
    id_token = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    owner = ndb.StringProperty(required=True)
    age = ndb.IntegerProperty()
    breed = ndb.StringProperty()
    gender = ndb.StringProperty()
    appointment = ndb.StringProperty()
# [END Entities]


# [START Handlers]
class PersonHandler(webapp2.RequestHandler):
    def post(self):
        if 'id_token' in self.request.headers:
            token = self.request.headers['id_token']
            header_data = parseToken(token)
            logging.debug("header data:")
            logging.debug(header_data)
        else:
            self.response.set_status(403)
            self.response.write("Forbidden!\nmust provide \'id_token\'")
            return
        person_data = json.loads(self.request.body)
        logging.debug("person data:")
        logging.debug(person_data)
        if header_data and 'name' in person_data:
            if person_data['name']:
                new_person = Person(parent=getParentKey(c = 'person', user_id = header_data),
                                    id_token=header_data,
                                    name=person_data['name'],
                                    age=None,
                                    city=None,
                                    dogs = [],
                                    recurring_client=False)
                if 'age' in person_data:
                    new_person.age = person_data['age']
                if 'city' in person_data:
                    new_person.city = person_data['city']
                if 'recurring_client' in person_data:
                    new_person.recurring_client = person_data['recurring_client']
                new_person.put()
                new_person.id = new_person.key.urlsafe() # here
                new_person.put()
                person_dict = new_person.to_dict()
                person_dict['self'] = "/clients/" + new_person.id
                self.response.set_status(200)
                self.response.write(json.dumps(person_dict))
            else:
                self.response.set_status(400)
                self.response.write("Bad Request: must provide \'name\'")
                return
        else:
            self.response.set_status(400)
            self.response.write("Bad Request: Error processing Request")
            return

    def get(self, id=None):
        if 'id_token' in self.request.headers:
            header_data = parseToken(self.request.headers['id_token'])
        else:
            self.response.set_status(400)
            self.response.write("Bad Request: must provide \'id_token\'")
            return
        if header_data:
            if id:
                person = ndb.Key(urlsafe=id).get()
                if person:
                    if person.id_token == header_data:
                        person_dict = person.to_dict()
                        person_dict['dogs'] = person.dogs
                        person_dict['self'] = "/clients/" + person.id
                        self.response.set_status(200)
                        self.response.write(json.dumps(person_dict))
                    else:
                        self.response.set_status(403)
                        self.response.write("Forbidden!")
                else:
                    self.response.set_status(404)
                    self.response.write("failed to locate client")
            else:
                parent_key = getParentKey(c = 'person', user_id = header_data)
                persons = Person.query(ancestor=parent_key).fetch()
                if persons:
                    client_list = []
                    for person in persons:
                        cur = {}
                        cur['id'] = person.id
                        cur['name'] = person.name
                        cur['age'] = person.age
                        cur['city'] = person.city
                        cur['recurring_client'] = person.recurring_client
                        client_list.append(cur)
                    self.response.set_status(200)
                    self.response.write(json.dumps(client_list))
                else:
                    self.response.set_status(404)
                    self.response.write("failed to locate resource")
        else:
            self.response.set_status(400)
            self.response.write("Bad Request Dawgg")

    def delete(self, id=None):
        if id:
            if 'id_token' in self.request.headers:
                header_data = parseToken(self.request.headers['id_token'])
            else:
                self.response.set_status(400)
                self.response.write("Bad Request")
                return
            person = ndb.Key(urlsafe=id).get()
            if person:
                if person.id_token == header_data:
                    dog_query = Dog.query(Dog.owner == id).fetch()
                    if dog_query:
                        for dog in dog_query:
                            dog.key.delete()
                    person.key.delete()
                    self.response.set_status(204)
                else:
                    self.response.set_status(403)
                    self.response.write("Unauthorized")
            else:
                self.response.set_status(404)
                self.response.write("Failed To Locate Client")
                return
        else:
            self.response.set_status(400)
            self.response.write("Bad Request")
            return

    def patch(self, id=None):
        if id:
            if 'id_token' in self.request.headers:
                header_data = parseToken(self.request.headers['id_token'])
                logging.debug("header data:")
                logging.debug(header_data)
            else:
                self.response.set_status(400)
                self.response.write("Bad Request")
                return
            data = json.loads(self.request.body)
            person = ndb.Key(urlsafe=id).get()
            if person:
                if person.id_token == header_data:
                    if 'name' in data:
                        person.name = data['name']
                    if 'age' in data:
                        person.age = data['age']
                    if 'city' in data:
                        person.city = data['city']
                    if 'recurring_client' in data:
                        person.recurring_client = data['recurring_client']
                    if 'dog' in data:
                        person.dogs.append(data['dog'])
                    person.put()
                    person_dict = person.to_dict()
                    person_dict['self'] = "/clients/" + person.id
                    self.response.set_status(204)
                    self.response.write(json.dumps(person_dict))
                else:
                    self.response.set_status(403)
                    self.response.write("Unauthorized")
                    return
            else:
                self.response.set_status(404)
                self.response.write("Failed To Locate Client")
                return
        else:
            self.response.set_status(400)
            self.response.write("Bad Request")
            return

    def put(self, id=None):
        if id:
            if 'id_token' in self.request.headers:
                header_data = parseToken(self.request.headers['id_token'])
                logging.debug("header data:")
                logging.debug(header_data)
            else:
                self.response.set_status(400)
                self.response.write("Bad Request")
                return
            data = json.loads(self.request.body)
            person = ndb.Key(urlsafe=id).get()
            if person:
                if person.id_token == header_data:
                    if 'recurring_client' in data:
                        person.recurring_client = data['recurring_client']
                    person.put()
                    person_dict = person.to_dict()
                    person_dict['self'] = "/clients/" + person.id
                    self.response.set_status(204)
                else:
                    self.response.set_status(403)
                    self.response.write("Unauthorized")
                    return
            else:
                self.response.set_status(404)
                self.response.write("Failed To Locate Client")
                return
        else:
            self.response.set_status(400)
            self.response.write("Bad Request")
            return


class DogHandler(webapp2.RequestHandler):
    def post(self):
        if 'id_token' in self.request.headers:
            token = self.request.headers['id_token']
            header_data = parseToken(token)
        else:
            self.response.set_status(403)
            self.response.write("Forbidden!\nmust provide \'id_token\'")
            return
        dog_data = json.loads(self.request.body)
        if header_data and 'name' in dog_data:
            if dog_data['name'] and dog_data['owner']:
                new_dog = Dog(parent=getParentKey(c = 'dog', user_id = header_data),
                                id_token=header_data,
                                name=dog_data['name'],
                                owner=dog_data['owner'],
                                gender=None,
                                age=None,
                                breed=None,
                                appointment=None)
                if 'gender' in dog_data:
                    new_dog.gender = dog_data['gender']
                if 'age' in dog_data:
                    new_dog.age = dog_data['age']
                if 'breed' in dog_data:
                    new_dog.breed = dog_data['breed']
                if 'appointment' in dog_data:
                    new_dog.appointment = dog_data['appointment']
                new_dog.put()
                new_dog.id = new_dog.key.urlsafe() # here
                new_dog.put()
                dog_dict = new_dog.to_dict()
                #owner = ndb.Key(urlsafe=new_dog.owner).get()
                owner = Person.query(Person.id == new_dog.owner).get()
                owner.dogs.append(dog_dict)
                owner.put()
                dog_dict['self'] = "/dogs/" + new_dog.id
                self.response.set_status(200)
                self.response.write(json.dumps(dog_dict))
            else:
                self.response.set_status(400)
                self.response.write("Bad Request: must provide \'name\'")
                return
        else:
            self.response.set_status(400)
            self.response.write("Bad Request")
            return


    def get(self, id=None):
        if 'id_token' in self.request.headers:
            header_data = parseToken(self.request.headers['id_token'])
        else:
            self.response.set_status(400)
            self.response.write("Bad Request: must provide \'id_token\'")
            return
        if header_data:
            if id:
                dog = ndb.Key(urlsafe=id).get()
                if dog:
                    if dog.id_token == header_data:
                        dog_dict = dog.to_dict()
                        dog_dict['self'] = "/dogs/" + dog.id
                        self.response.set_status(200)
                        self.response.write(json.dumps(dog_dict))
                    else:
                        self.response.set_status(403)
                        self.response.write("Forbidden!")
                else:
                    self.response.set_status(404)
                    self.response.write("failed to locate dog! \nsend a search party and post fliers!")
            else:
                parent_key = getParentKey(c = 'dog', user_id = header_data)
                dogs = Dog.query(ancestor=parent_key).fetch()
                if dogs:
                    dawgs = []
                    for dog in dawgs:
                        cur = {}
                        cur['id'] = dog.id
                        cur['name'] = dog.name
                        cur['age'] = dog.age
                        cur['gender'] = dog.gender
                        cur['breed'] = dog.breed
                        owner_name = Person.querry(Person.id == dog.owner).get().name
                        cur['owner_id'] = dog.owner
                        cur['owner'] = owner_name
                        cur['appointment'] = dog.appointment
                        dawgs.append(cur)
                    self.response.set_status(200)
                    self.response.write(json.dumps(dawgs))
                else:
                    self.response.set_status(404)
                    self.response.write("failed to locate resource")
        else:
            self.response.set_status(400)
            self.response.write("Bad Request")

    def put(self, id=None):
        if id:
            if 'id_token' in self.request.headers:
                token = self.request.headers['id_token']
                header_data = parseToken(token)
            else:
                self.response.set_status(400)
                self.response.write("Bad Request")
                return
            dog_data = json.loads(self.request.body)
            dog = ndb.Key(urlsafe=id).get()
            if dog:
                if dog.id_token == header_data:
                    if dog_data['appointment']:
                        dog.appointment = dog_data['appointment']
                        dog.put()
                        self.response.set_status(204)
                    else:
                        self.response.set_status(400)
                        self.response.write("error: no appointment data")
                        return
                else:
                    self.response.set_status(403)
                    self.response.write("Forbidden!")
                    return
            else:
                self.response.set_status(400)
                self.response.write("Bad Request")
                return
        else:
            self.reponse.set_status(404)
            self.response.write("unable to locate dog")
            return

    def patch(self, id=None):
        if id:
            if 'id_token' in self.request.headers:
                header_data = parseToken(self.request.headers['id_token'])
            else:
                self.response.set_status(400)
                self.response.write("Bad Request")
                return
            data = json.loads(self.request.body)
            dog = ndb.Key(urlsafe=id).get()
            if dog:
                if dog.id_token == header_data:
                    if 'name' in data:
                        dog.name = data['name']
                    if 'owner' in data:
                        dog.owner = data['owner']
                    if 'age' in data:
                        dog.age = data['age']
                    if 'gender' in data:
                        dog.gender = data['gender']
                    if 'breed' in data:
                        dog.breed = data['breed']
                    if 'appointment' in data:
                        dog.appointment = data['appointment']
                    dog.put()
                    self.response.set_status(204)
                else:
                    self.response.set_status(403)
                    self.response.write("Unauthorized")
                    return
            else:
                self.response.set_status(404)
                self.response.write("Failed To Locate Dog")
                return
        else:
            self.response.set_status(400)
            self.response.write("Bad Request")
            return

    #replace (can modify current_boat)
    def putd(self, id=None):
        if id:
            s = ndb.Key(urlsafe=id).get()
            if s.id:
                s_d = json.loads(self.request.body)
                #make sure number is spec'd!
                if 'number' in s_d:
                    #filter bad req
                    if ('arrival_date' in s_d and not 'current_boat' in s_d) or (not 'arrival_date' in s_d and 'current_boat' in s_d):
                        self.reponse.set_status(400)
                        self.response.write("must specify both arrival date and boat id or neither")
                        return
                    else:
                        #set the docked boat to sea
						if s.current_boat:
							old_boat_key = s.current_boat
							old_boat = ndb.Key(urlsafe=old_boat_key).get()
							old_boat.at_sea = True
							old_boat.put()
                        #dock a new boat
						if 'arrival_date' in s_d and 'current_boat' in s_d:
							s.arrival_date = sd['arrival_date']
							s.current_boat = sd['current_boat']
                        #slip is empty
						s.arrival_date = None
						s.current_boat = None
                    #set rest of slip stuff & return 200
                    s.number = s_d['number']
                    s.departure_history = []
                    s.put()
                    sd = s.to_dict()
                    sd['self']= "/slips/" + id
                    self.response.set_status(204)
                    self.response.write(json.dumps(sd))
                else:
                    self.response.set_status(400)
                    self.response.write("must specify slip number")
                    return
            else:
                self.response.set_status(404)
                self.response.write("unable to locate specified slip")
                return
        else:
            self.response.set_status(400)


# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):
        # [create a state string]
        state = new_secure_state()
        ndb_state = State(value=state)
        ndb_state.put()

        # [link the button to Google's OAuth]
        welcome = "Welcome, this is a place to help manage your clients, their dogs, and upcoming appointments!"
        url = GOOGLE_URL + "?response_type=code&client_id=" + CLIENT_ID + "&redirect_uri=" + REDIRECT_URL + "&scope=email&state=" + state
        template_values = { 'url': url }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
# [END Handlers]



""" -{ the magic }- """
# [START app]
#allow PATCH (note: from stackexchange, not in webapp2 docs)
#https://stackoverflow.com/questions/16280496/patch-method-handler-on-google-appengine-webapp2
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/redirect', redirectHandler),
    ('/clients/(.*)', PersonHandler),
    ('/clients', PersonHandler),
    ('/dogs', DogHandler),
    ('/dogs/(.*)', DogHandler),
], debug=True)
# [END app]
