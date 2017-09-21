from flask import Flask

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

# EB looked for an 'application' callable by default
application = Flask(__name__)

@application.route('/person', methods=['GET', 'POST'])
def get_post_person():
    if request.method == 'GET':
        #return paginated list of persons in db
        pass
    else:
        #check db if person already exists
        #if exists return person already exists
        #else return 200
        pass
    
    return 'called /person'

@application.route('/person/<id>', methods=['GET', 'PUT', 'DELETE'])
def get_put_del_person_id():
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

    return 'called person/<id>'

@application.route('/person/<p_id>/<a_id>')
def get_person_address():
    return 'Hello, Wor

@application.route('/person')
def hello_world():
    return 'Hello, World!'

@application.route('/person')
def hello_world():
    return 'Hello, World!'

#application.add_url_rule('/', 'index', (lambda: header_text + say_hello() + instructions + footer_text))

#application.add_url_rule('/<username>', 'hello', (lambda username: header_text + say_hello(username) + home_link + footer_text))

if __name__ == "__main__":
    application.debug = True
    application.run()


