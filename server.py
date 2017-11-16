#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
#url_for
#from flask_login import LoginManager,current_user,login_user,login_required
#from flask.ext.login import LoginManager

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://zw2423:1231@35.196.90.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#[]
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args



  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT distinct taste FROM cuisine")
  cuisine = []
  for result in cursor:
    cuisine.append(result[0])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = cuisine)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

@app.route('/findCuisine', methods=['POST'])
def findCuisine():
  #query = request.form['taste']
  cursor = g.conn.execute(
    """SELECT restaurant.name,avg(food_rating) 
    FROM cuisine,ratings,consumer,restaurant 
    WHERE consumer.restaurant_id=cuisine.restaurant_id and rating_id=user_id 
    and restaurant.place_id=cuisine.restaurant_id and taste = '"""+request.form['taste']+"'"
    +"group by restaurant.name order by avg(food_rating) desc"
    )
  rfind = []
  for result in cursor:
    # print result
    rfind.append(result[0]+"    "+str(result[1]))
  cursor.close()
  context_cuisine = dict(data_cuisine = rfind)
  return render_template("index.html",**context_cuisine)

@app.route('/getDrink', methods=['POST'])
def getDrink():
  cursor = g.conn.execute(
    """SELECT restaurant.name,avg(food_rating) 
    FROM service,ratings,consumer,restaurant 
    WHERE consumer.restaurant_id=service.restaurant_id and rating_id=user_id 
    and restaurant.place_id=service.restaurant_id and alcohol = '"""+request.form['alcohol']+"'"
    +"group by restaurant.name order by avg(food_rating) desc limit 5"
    )
  rget = []
  for result in cursor:
    rget.append(result[0]+"    "+str(result[1]))
  cursor.close()
  '''cursor=g.conn.execute(
    """SELECT restaurant.name 
    FROM service,restaurant 
    WHERE restaurant.place_id=service.restaurant_id and alcohol = '"""+request.form['alcohol']+"'"
    )
  rget = []
  for result in cursor:
    rget.append(result[0])
  cursor.close()'''
  context_alcohol = dict(data_alcohol = rget)
  return render_template("index.html",**context_alcohol)

@app.route('/addRating', methods=['GET'])
def addRating():
  cursor = g.conn.execute("SELECT place_id,name FROM restaurant")
  res = []
  for result in cursor:
    res.append(str(result[0])+"    "+result[1])
  cursor.close()
  context = dict(data_res = res)
  return render_template("addRating.html", **context)




@app.route('/add', methods=['POST'])
def add():
  userID = request.form['userID']
  password=request.form['password']
  resID = request.form['resID']
  drink_level = request.form['drink_level']
  taste_preference = request.form['taste_preference']
  dress_preference = request.form['dress_preference']
  foodRating=request.form['foodRating']

  g.conn.execute("INSERT INTO consumer VALUES ("+userID+",'"+password+"',"+resID+",'"+drink_level+"','"+taste_preference+"','"+dress_preference+"')")
  g.conn.execute("INSERT INTO ratings VALUES ("+userID+","+foodRating+")")

  cursor = g.conn.execute(
    """SELECT user_id,password,restaurant_id,food_rating, drink_level, taste_preference, dress_preference FROM consumer,ratings 
    WHERE rating_id=user_id and user_id = '"""+request.form['userID']+"'"
    )
  newconsumer = []
  #newconsumer.append(str(userID)+"    "+password+"    "+resID+"   "+foodRating+"    "+drink_level+"   "+taste_preference+"   "+dress_preference)
  for result in cursor:
    newconsumer.append(str(str(result[0])+"    "+str(result[1])+"    "+str(result[2])+"    "+str(result[3])+"   "+str(result[4])+"   "+str(result[5])+"   "+str(result[6])))
  cursor.close()
  context = dict(data_newconsumer = newconsumer)
  return render_template("addRating.html", **context)
  #return redirect('/')



# Example of adding new data to the database
'''@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')'''






username = []
password = []
@app.route('/login',methods=['POST'])
def login():
  goto = []
  context = {}
  username = request.form['username_data']
  input_password = request.form['password_data']
  cursor = g.conn.execute("""SELECT password From consumer where user_id='""" + username + "'")
  for result in cursor:
    password.append(result[0])
  cursor.close()
  #cursor = g.conn.execute("SELECT restaurant.name From restaurant,service,consumer,ratings where rating_id=user_id and consumer.restaurant_id=restaurant.place_id and restaurant.place_id = service.restaurant_id and alcohol='" + query + "'")
  if password[0] == input_password:
    profile_search = g.conn.execute("""SELECT * From consumer where user_id = '""" + username +"'")
    user_profile = []
    for profile_data in profile_search:
      user_profile.append(str(str(profile_data[0]))+"    "+str(profile_data[1])+"    "+str(profile_data[2])+"    "+profile_data[3]+"    "+profile_data[4]+"    "+profile_data[5])
    profile_search.close()
    context = dict(result = user_profile[0])
    goto = ["userprofile.html"]
  else:
    context = dict(result = 'Failed')
    goto = ["failed.html"]
    #goto = "index.html"
  return render_template(goto,**context)
'''
@app.route('/loginrating', methods=['POST'])
def loginrating():
  userID = request.form['userID']
  password=request.form['password']
  resID = request.form['resID']
  foodRating=request.form['foodRating']

  g.conn.execute("INSERT INTO consumer VALUES ("+userId+",'"+password+"',"+resID+")")
  g.conn.execute("INSERT INTO ratings VALUES ("+userId+","+foodRating+")")

  cursor = g.conn.execute(
    """SELECT user_id,password,restaurant_id,food_rating FROM consumer,ratings 
    WHERE rating_id=user_id and user_id = '"""+request.form['userID']+"'"
    )
  newrating = []
  for result in cursor:
    newrating.append(str(result[0])+"    "+result[1]+"    "+str(result[2])+"    "+str(result[3]))
  cursor.close()
  context = dict(data_newconsumer = newrating)
  return render_template("loginrating.html", **context)
'''
if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
