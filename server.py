from flask import Flask, request, redirect, render_template, session, flash
from flask import Flask
import datetime
import re
from flask.ext.bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key='secret'
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
from mysqlconnection import MySQLConnector
mysql= MySQLConnector('howdy')

#this is mainpage without user input registered
@app.route('/', methods =['GET'])
def index():

	return render_template('index.html')

@app.route('/create_user', methods=['POST'])
def create_user():

	email = request.form['email']
	first_name = request.form['first_name']
	last_name = request.form['last_name']
	password = request.form['password']

	if len(request.form['first_name']) > 2 and len(request.form['last_name']) > 2 and (request.form['first_name']).isalpha() and (request.form['first_name']).isalpha() and EMAIL_REGEX.match(request.form['email']) and len(request.form['password']) > 8 and request.form['password']== request.form['cpassword']:
			 # run validations and if they are successful we can create the password hash with bcrypt
		session['user_id'] = user[0]['id']
		flash("You have been logged, locked and recorded!")
		password = bcrypt.generate_password_hash(request.form['password'])
		query = "INSERT into users(first_name, last_name, email, password, created_at, updated_at) VALUES('{}','{}','{}','{}', NOW(), NOW())".format(request.form['first_name'], request.form['last_name'], request.form['email'], password)
		mysql.run_mysql_query(query)
		 # now we insert the new user into the database

		  # redirect to success page
	else:
		flash("Incorrect Inputs! Try again....but harder.")
	
	return redirect('/')

@app.route('/login', methods=['POST'])
def login():

	email = request.form['email']
	password = request.form['password']
	query = "SELECT * from users where email = '{}'".format(request.form['email']);
	existing_user = mysql.fetch(query)
	session['user']={'first_name':existing_user[0]['first_name'], 'last_name':existing_user[0]['last_name']}
	user_query = "SELECT * FROM users WHERE email = '{}' LIMIT 1".format(email)
	user = mysql.fetch(user_query) # user will be returned in an array

	if bcrypt.check_password_hash(user[0]['password'], password):
		flash("You are logged in!")
		session['user_id'] = user[0]['id']
		return render_template('memberlogin.html')

	else:
		flash("Access denied, NERD. Make sure you're typing in the correct password. Not a registered member?? Sign up further below!!!")
		return redirect('/')
	# set flash error message and redirect to login page
	return redirect('/')

@app.route('/commentspage', methods=['POST'])
def comments():

	messages = mysql.fetch("SELECT message FROM messages")
	messages = mysql.fetch("SELECT messages.message, messages.created_at, users.first_name, messages.id FROM messages left join users on messages.user_id=users.id")
	comments = mysql.fetch("SELECT comments.comment, comments.created_at, users.first_name, comments.message_id FROM comments left join users on comments.user_id=users.id")

	return render_template('thewall.html', messages=messages, comments=comments)

@app.route('/postmessage', methods=['POST'])
def postthis():

	if len(request.form['submitmessage']) > 3:
		messagesfunction = "INSERT into messages(message, user_id, created_at) VALUES('{}','{}', NOW())".format(request.form['submitmessage'], session['user_id'])
		mysql.run_mysql_query(messagesfunction)
		return redirect('/')

	else:
		flash("No message is significant enough to post with so little characters.")
	return render_template('thewall.html')

@app.route('/postcomment', methods=['POST'])
def postthat():

	if len(request.form['submitcomment']) > 3:
		commentsfunction = "INSERT into comments(comment, user_id, message_id, created_at) VALUES('{}','{}','{}', NOW())".format(request.form['submitcomment'], session['user_id'], request.form['message_id'])
		mysql.run_mysql_query(commentsfunction)

		return redirect('/')

	else:
		flash("No message is significant enough to post with so little characters.")
		return render_template('thewall.html')

# @app.route('/delete')
# def delete():
# 	query = "DELETE FROM messages WHERE conditions 


@app.route('/reset')
def reset():
	session.pop('user')
	return redirect('/')


app.run(debug=True)


