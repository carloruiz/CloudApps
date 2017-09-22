from flask import Flask
from sqlalchemy import *
from sqlalchemy import exc
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response


# URI for connecting to postgres
DATABASEURI = 'mysql+pymysql://user1:2cloud4grp@northwind.cpqu2popccu7.us-east-2.rds.amazonaws.com:3306/northwind'

# Creates a database engine that connects to the URI.
engine = create_engine(DATABASEURI)

#Use SQLAlchemy methods to reflect tables in database.
meta = MetaData()
meta.reflect(bind=engine)
app = Flask(__name__)
 
@app.route("/")
def hello():
    return "Welcome to Python Flask App!"


# Example query. Makes an array out of last_name field in northwind db. 
  cursor = g.conn.execute("SELECT last_name FROM employees")
  last_names = []
  for result in cursor:
    last_names.append(result['last_name'])
  cursor.close()

'''This runs before every web request'''
@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

'''tears down db connection. details are in sqlalcemy documentation'''
@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass
    
if __name__ == "__main__":
    app.run()
