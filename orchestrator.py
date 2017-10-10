from flask import Flask, request, Response, jsonify
import json
import requests
import urlparse, parse_qs

application = Flask(__name__)


@application.route('/')
def render_home():
    #render home page template
    pass

@application.route('/person-search')
def person_search():
    

@application.route('/person', methods=['GET', 'POST'])
def get_post_person():
    code = 400
    if request.method == 'GET':
        parsed = urlparse(request.url)
        url_query = parse_qs(parsed.query)
        if 'offset' in url_query:
            
        offset = 0 if 'offset' not in url_query` \
            else int(url_query['offset'][0])
         
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

