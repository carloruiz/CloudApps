from flask import Flask, request, Response, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from person_constants import *
import json
import requests
from requests.exceptions import MissingSchema, RequestException
from urlparse import urlparse, parse_qs
from flask_cors import CORS

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
CORS(application)


@application.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@application.route('/person', methods=['GET', 'POST'])
def get_post_person():
    code = 400
    if request.method == 'GET':
        offset = 0 if 'offset' not in request.args \
            else int(request.args['offset'])
        print(offset)
        args = {}
        for x in ['last_name', 'first_name', 'address_url']:
            if x in request.args:
                args[x] = request.args[x]
        query = session.query(Persons).filter_by(**args).order_by(Persons.p_id)[offset:offset+10]
        
        response = []
        for row in query:
            response.append({ 'p_id':row.p_id, 'last_name': row.last_name, 'first_name': row.first_name, 'address_url': row.address_url })
        response = json.dumps(response)
        code = 200

    else:
        payload = json.loads(request.data)
        if any(x not in payload for x in ['last_name', 'first_name']):
            raise InvalidUsage('first name and last name must both be specified')
        args = {}
        for x in ['last_name', 'first_name', 'address_url']:
            args[x] = payload[x]

        person = Persons(**args)
        session.add(person)
        session.commit()
        #Place person_url in addresses with PUT call
        query = session.query(Persons).filter_by(**args).all()
        person_url = persons_endpoint + '/' + str(query[-1].p_id)
        response = {'Person-URL':person_url}

        try:
            payload = {'person_url':person_url}
            r = requests.put(query[0].address_url, data=json.dumps(payload))
            response['PUT response'] = r.text.encode("ascii")
     
        except RequestException:
            raise InvalidUsage('PUT on addresses failed at' + query[0].address_url, status_code=400)
                    
        response = json.dumps(response)
        code = 201
    return response, code 

@application.route('/person/<p_id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_del_person_id(p_id):
    response = ''
    query = session.query(Persons).filter_by(p_id=p_id).all()
    person = { 'last_name': query[0].last_name, 'first_name': query[0].first_name, 'address_url': query[0].address_url} if query else None
    if not person:
        raise InvalidUsage('p_id not found', status_code=404)
    
    if request.method == 'GET':
        response = json.dumps(person)
        code = 200
    
    elif request.method == 'PUT':
        person.update(json.loads(request.data))
        session.query(Persons).filter_by(p_id=p_id).update(person)
        session.commit()
        code = 204
    
    elif request.method == 'DELETE':
        session.query(Persons).filter_by(p_id=p_id).delete()
        session.commit()
        code = 204

    return response, code
    
@application.route('/person/<p_id>/address')
def get_person_address(p_id):
    response = ''
    query = session.query(Persons).filter_by(p_id=p_id).all()
    if not query:
        raise InvalidUsage('p_id not found', status_code=404)

    address_url = query[0].address_url
    if not address_url:
        return response, 204
    
    try:
        r = requests.get(address_url)
    except MissingSchema:
        raise InvalidUsage('Invalid Url', status_code=404)
   
    return r.text, r.status_code


if __name__ == "__main__":
    application.debug = True
    application.run()

