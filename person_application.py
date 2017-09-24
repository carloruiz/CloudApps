from flask import Flask, request, Response, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from person_constants import *
import json
from urlparse import urlparse, parse_qs


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


@application.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@application.route('/person', methods=['GET', 'POST'])
def get_post_person():
    code = 400
    if request.method == 'GET':
        parsed = urlparse(request.url)
        url_query = parse_qs(parsed.query)
        offset = 0 if 'offset' not in url_query \
            else int(url_query['offset'][0])
        '''
        offset = 0 if 'Pagination-Offset' not in request.headers \
            else int(request.headers.get('Pagination-Offset'))
        '''
         
        query = session.query(Persons).order_by(Persons.p_id)[offset:offset+10]
        response = []
        for row in query:
            response.append({ 'last_name': row.last_name, 'first_name': row.first_name })
        response = json.dumps(response)
        code = 206
    else:
        if any(x not in request.form for x in ['last_name', 'first_name']):
            raise InvalidUsage('first name and last name must both be specified')
        person = Persons(last_name=request.form['last_name'], first_name=request.form['first_name'])
        session.add(person)
        session.commit()
        response = Response('')
        response.headers['Person-URL'] = request.base_url + '/%s' % person.p_id
        code = 201
    return response, code 

@application.route('/person/<p_id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_del_person_id(p_id):
    response = ''
    query = session.query(Persons).filter_by(p_id=p_id).all()
    person = { 'last_name': query[0].last_name, 'first_name': query[0].first_name } if query else None
    if not person:
        raise InvalidUsage('p_id not found', status_code=404)
    
    if request.method == 'GET':
        response = json.dumps(person)
        code = 200
    
    elif request.method == 'PUT':
        person.update(request.form)
        session.query(Persons).filter_by(p_id=p_id).update(person)
        session.commit()
        code = 204
    
    elif request.method == 'DELETE':
        session.query(Persons).filter_by(p_id=p_id).delete()
        session.commit()
        code = 204

    return response, code
    
@application.route('/person/<p_id>/addresses')
def get_person_address():
    # check if a_id is valid. If so, return their address. Else 404
    response = ''
    query = session.query(Persons).filter_by(p_id=p_id).all()
    if not query:
        raise InvalidUsage('p_id not found', status_code=404)
    address_url = query[0].address_url
    

    person = { 'last_name': query[0].last_name, 'first_name': query[0].first_name } if query else None
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


