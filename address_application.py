from flask import Flask, request, Response, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from address_constants import *
import json
from urllib.parse import urlparse, parse_qs

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


@application.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@application.route('/address', methods=['GET', 'POST'])
def get_post_address():
    code = 400
    if request.method == 'GET':
    offset = 0 if 'offset' not in request.args \
        else int(request.args['offset'][0])

    args = {}
    for x in ['address', 'city', 'state', 'zip', 'country']:
        if x in request.args:
            args[x] = request.args[x]
         
        query = session.query(Addresses).filter_by(**args).order_by(Addresses.a_id)[offset:offset+10]

        #check 'query' is valid 
        response = []
        for row in query:
            response.append({ 'address': row.address, 'city': row.city, 'state': row.state, 'zip': row.zip, 'country': row.country })
        response = json.dumps(response)
        code = 200
    else:
    payload = jason.loads(request.data)
        if any(x not in payload for x in ['address', 'city', 'state', 'zip', 'country']):
            raise InvalidUsage('Address supplied is incomplete')

        address = Addresses(address=payload['address'], city=payload['city'], \
            state=payload['state'], zip=payload['zip'], country=payload['country'])

        session.add(address)
        session.commit()
        response = Response('')
        response.headers['Address-URL'] = request.base_url + '/%s' % address.a_id
        code = 201

    return response, code 

@application.route('/address/<a_id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_del_address_id(a_id):

    code = 400
    response = ''
    query = session.query(Addresses).filter_by(a_id=a_id).all()
    address = { 'address': query[0].address, 'city': query[0].city, 'state': query[0].state, 'zip': query[0].zip, 'country': query[0].country } if query else None

    if not address:
        raise InvalidUsage('a_id not found', status_code=404)
    
    if request.method == 'GET':
        response = json.dumps(address)
        code = 200

    elif request.method == 'PUT':
        address.update(json.loads(request.data))
        session.query(Addresses).filter_by(a_id=a_id).update(address)
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

if __name__ == "__main__":
    application.debug = True
    application.run()