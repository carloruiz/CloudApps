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

if __name__ == "__main__":
    app.run()
