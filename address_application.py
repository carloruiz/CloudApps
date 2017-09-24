from flask import Flask, request, Response, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from address_constants import *
import json

engine = create_engine(DATABASEURI)
Base = automap_base()
Base.prepare(engine, reflect=True)
Addresses = Base.classes.addresses
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


#############Address routes####################

@application.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@application.route('/address', methods=['GET', 'POST'])
def get_post_address():
    code = 400
    if request.method == 'GET':
        offset = 0 if 'Pagination-Offset' not in request.headers \
            else int(request.headers.get('Pagination-Offset'))
         
        query = session.query(Addresses).order_by(Addresses.a_id)[offset:offset+10]
        #check 'query' is valid 
        response = []
        for row in query:
            response.append({ 'address': row.address, 'city': row.city, 'state': row.state, 'zip': row.zip, 'country': row.country })
        response = json.dumps(response)
        code = 200
    else:
        if any(x not in request.form for x in ['address', 'city', 'state', 'zip', 'country']):
            raise InvalidUsage('Address supplied is incomplete or incorrectly supplied.')
        address = Addresses(address=request.form['address'], city=request.form['city'], state=request.form['state'], zip=request.form['zip'], country=request.form['country'])
        session.add(address)
        session.commit()
        response = Response('')
        response.headers['Person-URL'] = request.base_url + '/%s' % address.a_id
        code = 201
    return response, code 

@application.route('/address/<a_id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_del_address_id(a_id):
    code = 400
    #query db
    response = []
    query = session.query(Addresses).filter_by(a_id=a_id).all()
    for row in query:
        response.append({ 'address': row.address, 'city': row.city, 'state': row.state, 'zip': row.zip, 'country': row.country })
    if not response:
        raise InvalidUsage('a_id not found', status_code=404)
    
    if request.method == 'GET':
        response = json.dumps(response)
        code = 200
    elif request.method == 'PUT':
        #only perform PUT on db fields that are in the request from
        if 'address' not in request.form:
            new_address = response[0]['address']
        else:
            new_address = request.form['address']
        if 'city' not in request.form:
            new_city = response[0]['city']
        else:
            new_city = request.form['city']
        if 'state' not in request.form:
            new_state = response[0]['state']
        else:
            new_state = request.form['state']
        if 'zip' not in request.form:
            new_zip = response[0]['zip']
        else:
            new_zip = request.form['zip']
        if 'country' not in request.form:
            new_country = response[0]['country']
        else:
            new_country = request.form['country']
        session.query(Addresses).filter_by(a_id=a_id).update({'address': new_address, 'city': new_city, 'state': new_state, 'zip': new_zip, 'country': new_country })
        session.commit()
        response = ''
        code = 204
    elif request.method == 'DELETE':
        session.query(Addresses).filter_by(a_id=a_id).delete()
        response = ''
        session.commit()
        code = 204

    return response, code
    
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


