from flask import Flask, request, Response, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from person_constants import *
import json
from urllib.parse import urlparse, parse_qs
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
            else int(request.args['offset'][0])
        
        args = {}
        for x in ['last_name', 'first_name']:
            if x in request.args:
                args[x] = request.args[x]
    
        query = session.query(Persons).filter_by(**args).order_by(Persons.p_id)[offset:offset+10]
        
        response = []
        for row in query:
            response.append({ 'last_name': row.last_name, 'first_name': row.first_name })
        response = json.dumps(response)
        code = 206
    else:
        payload = json.loads(request.data)
        if any(x not in payload for x in ['last_name', 'first_name']):
            raise InvalidUsage('first name and last name must both be specified')
        person = Persons(last_name=payload['last_name'], first_name=payload['first_name'])
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
        person.update(json.loads(request.data))
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
    response = ''
    query = session.query(Persons).filter_by(p_id=p_id).all()
    if not query:
        raise InvalidUsage('p_id not found', status_code=404)
    address_url = query[0].address_url
    person = { 'last_name': query[0].last_name, 'first_name': query[0].first_name } if query else None
    
    return 'called person/$s/address' % p_id


if __name__ == "__main__":
    application.debug = True
    application.run()

