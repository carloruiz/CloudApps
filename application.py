from flask import Flask, request, Response, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from constants import *
import json

engine = create_engine(DATABASEURI)
Base = automap_base()
Base.prepare(engine, reflect=True)
Persons = Base.classes.persons
session = Session(engine)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

# EB looked for an 'application' callable by default
application = Flask(__name__)


#############PERSON routes####################

@application.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@application.route('/person', methods=['GET', 'POST'])
def get_post_person():
    if request.method == 'GET':
        offset = 0 if 'Pagination-Offset' not in request.headers \
            else int(request.headers.get('Pagination-Offset'))
	            
        query = session.query(Persons).order_by(Persons.p_id)[offset:offset+10]
        #check 'query' is valid 
        response = []
        for row in query:
            response.append({ 'last_name': row.last_name, 'first_name': row.first_name })
	response = json.dumps(response)
    else:
        if any(x not in request.form for x in ['last_name', 'first_name']):
            raise InvalidUsage('first name and last name must both be specified')
        person = Persons(last_name=request.form['last_name'], first_name=request.form['first_name'])
	session.add(person)
        session.commit()
        response = Response('')
	response.headers['Person-URL'] = request.base_url + '/%s' % person.p_id

   return response 

@application.route('/person/<p_id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_del_person_id(p_id):
        #query db here??
    if request.method == 'GET':
        #query db. If result is empty. return 404,
        #else 200 with entity in payload
        pass
    elif request.method == 'PUT':
        #modify entry in db if it exists. Return 4** code otherwise
        pass
    else:
        #delete entry in db if it exists. Return 4** code otherwise
        pass

    return 'called person/%s' %p_id

@application.route('/person/<p_id>/addresses')
def get_person_address():
    # check if a_id is valid. If so, return their address. Else 404
    return 'called person/$s/address' % p_id


#############ADDRESS routes####################

@application.route('/addresses', methods=['GET', 'POST'])
def get_post_address():
    if request.method == 'GET':
        #return paginated list of addresses in db
        pass
    else:
        #check db if address  already exists
        #if exists return error code for  already exists
        #else return 200
        pass
    
    return 'called /address'

@application.route('/addresses/<a_id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_del_address_id():
        #query db here??
    if request.method == 'GET':
        #query db. If result is empty. return 404,
        #else 200 with entity in payload
        pass
    elif request.method == 'PUT':
        #modify entry in db if it exists. Return 4** code otherwise
        pass
    else:
        #delete entry in db if it exists. Return 4** code otherwise
        pass

    return 'called address/%s' %a_id


@application.route('/addresses/<a_id>/persons')
def get_address_persons():
    # check if a_id is valid. If so, return their address. Else 404
    return 'called person/$s/address' % p_id


#application.add_url_rule('/', 'index', (lambda: header_text + say_hello() + instructions + footer_text))

#application.add_url_rule('/<username>', 'hello', (lambda username: header_text + say_hello(username) + home_link + footer_text))

if __name__ == "__main__":
    application.debug = True
    application.run()

def say_hello(username="World"):
    return '<p>Hello %s!<\p>' % username

header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''

home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'


