from flask import Flask, request, Response, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from address_constants import *
import json
from urlparse import urlparse, parse_qs
from flask_cors import CORS
from pymysql.err import IntegrityError
import requests

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
CORS(application)


@application.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@application.route('/address', methods=['GET', 'POST'])
def get_post_address():
    if request.method == 'GET':
        offset = 0 if 'offset' not in request.args else int(request.args['offset'])
        args = {}
        for x in ['address', 'city', 'state', 'zip', 'country']:
            if x in request.args:
                args[x] = request.args[x]
        try:         
            query = session.query(Addresses).filter_by(**args).order_by(Addresses.a_id)[offset:offset+10]
        except sqlalchemy.exc.InvalidRequestError:
            session.rollback()
            raise InvalidUsage('database error', satus_code=500)

        response = []
        for row in query:
            response.append({ 'a_id': row.a_id, 'address': row.address, 'city': row.city, 'state': row.state, 'zip': row.zip, 'country': row.country })
        response = json.dumps(response)
        code = 200

    else:
        payload = json.loads(request.data)
        if any(x not in payload for x in ['address', 'city', 'state', 'zip', 'country']):
            raise InvalidUsage('Address supplied is incomplete')

        args = {}
        for x in ['address', 'city', 'state']:
            args[x] = payload[x]
       
        try:
            query = session.query(Addresses).filter_by(**args).all()
            if query:
                address = query[0]
            else:
                address = Addresses(**args)
                session.add(address)
                session.commit()
        except sqlalchemy.exc.InvalidRequestError:
            session.rollback()
            raise InvalidUsage('database error', status_code=500)

        response = Response('')
            
        response.headers['Address-URL'] = request.base_url + '/%s' % address.a_id
        code = 201

    return response, code 

@application.route('/address/<a_id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_del_address_id(a_id):

    code = 400
    response = ''
    try:
        query = session.query(Addresses).filter_by(a_id=a_id).all()
    except sqlalchemy.exc.InvalidRequestError:
        session.rollback()
        raise InvalidUsage("database error", status_code=500)

    address = { 'a_id': a_id, 'address': query[0].address, 'city': query[0].city, 'state': query[0].state, 'zip': query[0].zip, 'country': query[0].country } if query else None

    if not address:
        raise InvalidUsage('a_id not found', status_code=404)
    
    if request.method == 'GET':
        response = json.dumps(address)
        code = 200

    elif request.method == 'PUT':
        payload = json.loads(request.data)
        args = {}
        for x in ['address', 'city', 'state', 'zip', 'country']:
            if x in payload:
                args[x] = payload[x]

        address.update(args)
        session.query(Addresses).filter_by(a_id=a_id).update(address)
        session.commit()
        code = 204

    elif request.method == 'DELETE':
        session.query(Addresses).filter_by(a_id=a_id).delete()
        session.commit()
        code = 204

    return response, code
    
@application.route('/address/<a_id>/persons', methods=['GET'])
def get_address_persons(a_id):
    code = 400
    address_url = request.base_url[0:request.base_url.rfind('/')]
    r = requests.get(persons_endpoint , params={"address_url": address_url})
    return r.text, r.status_code

if __name__ == "__main__":
    application.debug = True
    application.run(port=5001)
