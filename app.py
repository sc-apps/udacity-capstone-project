#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
from os import environ as env
import json
from flask import Flask, render_template, make_response, request, Response, flash, redirect, url_for, jsonify, abort, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import Form
from flask_cors import CORS
from auth import AuthError, requires_auth, get_token_auth_header, verify_decode_jwt, check_permissions
from forms import AddForm, UpdateForm, AddEvent
from models import db, Request, Event, setup_db

from urllib.parse import quote_plus, urlencode
from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

#----------------------------------------------------------------------------#
# App Config
#----------------------------------------------------------------------------#

def create_app(test_config=None):	

	ENV_FILE = find_dotenv()
	if ENV_FILE:
	    load_dotenv(ENV_FILE)	

	app = Flask(__name__)
	setup_db(app)	

	Migrate(app, db)
	CORS(app)	
	

#----------------------------------------------------------------------------#
# Auth Config
#----------------------------------------------------------------------------#	

	oauth = OAuth(app)	
	

	oauth.register(
	    "auth0",
	    client_id=env.get("AUTH0_CLIENT_ID"),
	    client_secret=env.get("AUTH0_CLIENT_SECRET"),
	    client_kwargs={"scope": "openid profile email"},
	    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
	)	
	

#----------------------------------------------------------------------------#
# Controllers
#----------------------------------------------------------------------------#	

	@app.route("/login")
	def login():
		return oauth.auth0.authorize_redirect(redirect_uri=url_for("callback", _external=True))	

	@app.route("/callback", methods=["GET", "POST"])
	def callback():
	    token = oauth.auth0.authorize_access_token()
	    session["user"] = token
	    return redirect("/")	
	

	@app.route("/logout")
	def logout():
	    session.clear()
	    return redirect(
	        "https://" + env.get("AUTH0_DOMAIN")
	        + "/v2/logout?"
	        + urlencode(
	            {
	                "returnTo": url_for("home", _external=True),
	                "client_id": env.get("AUTH0_CLIENT_ID"),
	            },
	            quote_via=quote_plus,
	        )
	    )	


	
	@app.route("/", methods=['GET','POST'])
	def home():	
		# when a user is authenticated, the user will be able to see the table with available requests
		if session:
			token = session['user']['id_token']
			payload = verify_decode_jwt(token)
			admin_check = check_permissions('Admin', payload)
			recipient_check = check_permissions('Recipient', payload)	

			page = request.args.get('page', 1, type=int)
			requests = Request.query.filter_by(taken=False).paginate(page, per_page=10)	

			# if a user decides to take a request, the user ticks the checkbox and clicks Submit, it will mark the request as taken in the DB and remove it from the view
			if request.method == 'POST':
				if request.form['submit-button'] == "Submit":
					for checkbox in request.form.getlist('check'):
						record = Request.query.filter_by(id=checkbox).first()
						record.taken = True
						db.session.commit()
					return redirect(url_for('home'))
			return render_template("home.html", requests=requests, admin_check=admin_check, recipient_check=recipient_check)
		# if not authenticated, a welcome page is shown asking the user to log in
		else:
			headers = {'Content-Type': 'text/html'}
			return make_response(render_template("home.html"), 200, headers)
			
	
	# an endpoint to add a new request for a gift. The user has to be authenticated and to have either Admin or Recipient role to see this endpoint 
	@app.route('/requests/add', methods=['GET', 'POST'])
	def add_request():
		# if authenticated via Auth0 in a web browser, we take the token from the user session
		if session:
			user = session.get('user')
			token = session['user']['id_token']
		# otherwise, the token should be provided in the API call
		else:
			token = get_token_auth_header()
			
		payload = verify_decode_jwt(token)
		admin_check = check_permissions('Admin', payload)
		recipient_check = check_permissions('Recipient', payload)
		
		if admin_check or recipient_check:
			form = AddForm()
			form.event_id.choices = [(event.id, event.name) for event in Event.query.all()]	

			if form.validate_on_submit():
				event_id = form.event_id.data
				event = Event.query.get(event_id)
				event_name = event.name
				new_request = Request(
		        	child_name = form.child_name.data,
		        	child_age = form.child_age.data,
		        	gift_name = form.gift_name.data,
		        	gift_link = form.gift_link.data,
		        	price = form.price.data,
		        	shipping_address = form.shipping_address.data,
		        	phone = form.phone.data,
		        	recipient_email = user['userinfo']['email'],
		        	taken = False,
		        	event_id = event_id,
		        	event_name = event_name
		        	)
				db.session.add(new_request)
				db.session.commit()	
				return redirect(url_for("user_requests"))
			return render_template('add.html',form=form, admin_check=admin_check, recipient_check=recipient_check)
		else:
			abort(403)	


	# the endpoint to add a new event that the user will be able to select in a new request form. Only accessible by the user with Admin role
	@app.route('/events/add', methods=['GET','POST'])
	def add_event():
		if session:
			user = session.get('user')
			token = session['user']['id_token']
		else:
			token = get_token_auth_header()

		payload = verify_decode_jwt(token)
		admin_check = check_permissions('Admin', payload)
		recipient_check = check_permissions('Recipient', payload)	
		if admin_check:
			form = AddEvent()
			if form.validate_on_submit():
				new_event = Event(
			        name = form.name.data,
			        date = form.date.data
			        )
				db.session.add(new_event)
				db.session.commit()
				return redirect(url_for("user_requests"))
			return render_template('add_event.html',form=form, admin_check=admin_check, recipient_check=recipient_check)	
		else:
			abort(403)


	# the endpiont to view raised requests. The user has to be authenticated and have either Admin or Recipient role
	@app.route('/requests')
	def user_requests():
		if session:
			user = session.get('user')
			email = str(user['userinfo']['email'])
			token = session['user']['id_token']
		else:
			token = get_token_auth_header()
		payload = verify_decode_jwt(token)
		admin_check = check_permissions('Admin', payload)
		recipient_check = check_permissions('Recipient', payload)	

		# the user with Admin role can see all requests created by various users with Recipient role
		if admin_check:
			requests = Request.query.all()
		# the users with Recipient role can see only own tickets
		elif recipient_check: 
			requests = Request.query.filter_by(recipient_email=email).all()
		else:
			abort(403)
		return render_template('profile.html',requests=requests, admin_check=admin_check, recipient_check=recipient_check) 
			
	
	# the endpoint to view and modify specific request. The user has to be authenticated and has either Recipient or Admin role
	@app.route('/requests/<int:request_id>', methods=['GET', 'POST'])
	def update_request(request_id):
		req = Request.query.get_or_404(request_id)
		if session:
			user = session.get('user')
			email = str(user['userinfo']['email'])
			token = session['user']['id_token']
		else:
			token = get_token_auth_header()
		payload = verify_decode_jwt(token)
		admin_check = check_permissions('Admin', payload)
		recipient_check = check_permissions('Recipient', payload)	

		# admin user will be able to see and modify all tickets. Other users with Recipient role can access and modify only own tickets
		if admin_check:
			pass
		elif req.recipient_email != email: 
			abort(403)	

		form = UpdateForm()
		# admin can modify the whole form, including child_name and child_age
		if admin_check:
			form.child_name.render_kw = {}
			form.child_age.render_kw = {}
		if request.method == 'POST':
			if admin_check:
				req.child_name = form.child_name.data
				req.child_age = form.child_age.data
			req.gift_name = form.gift_name.data
			req.gift_link = form.gift_link.data
			req.price = form.price.data
			req.shipping_address = form.shipping_address.data
			req.phone = form.phone.data
			db.session.commit()
			return redirect(url_for("user_requests"))	

		elif request.method == 'GET':
			form.child_name.data = req.child_name
			form.child_age.data = req.child_age
			form.gift_name.data = req.gift_name
			form.gift_link.data = req.gift_link
			form.price.data = req.price
			form.shipping_address.data = req.shipping_address
			form.phone.data = req.phone	

		return render_template('update.html',form=form, req=req,admin_check=admin_check, recipient_check=recipient_check)	
	

	# endpoint to delete a record. Admin can delete any record, A user with the Recipient role can delete only own ticket.
	@app.route('/requests/<int:request_id>/delete', methods=['POST'])
	def delete_request(request_id):
		req = Request.query.get_or_404(request_id)
		if session:
			user = session.get('user')
			email = str(user['userinfo']['email'])
			token = session['user']['id_token']
		else:
			token = get_token_auth_header()
		payload = verify_decode_jwt(token)
		admin_check = check_permissions('Admin', payload)	

		if admin_check:
			pass
		elif req.recipient_email != email: 
			abort(403)	

		db.session.delete(req)
		db.session.commit()
		return make_response(redirect(url_for("user_requests")),200)


#----------------------------------------------------------------------------#
# Error handlers
#----------------------------------------------------------------------------#
	@app.errorhandler(AuthError)
	def auth_error(e):
		return jsonify({"success": False, "error": e.status_code, "message": e.error['description']}), e.status_code

	@app.errorhandler(405)
	def method_not_allowed(error):
		return jsonify({
	          'success': False,
	          'error': 405,
	          'message': 'method not allowed'
	          }), 405

	@app.errorhandler(404)
	def not_found(error):
		return jsonify({
          'success': False,
          'error': 404,
          'message': 'resource not found'
          }), 404

	@app.errorhandler(403)
	def forbidden(error):
		return jsonify({
          'success': False,
          'error': 403,
          'message': 'Access forbidden'
          }), 403

	@app.errorhandler(422)
	def unprocessable(error):
		return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
        }), 422

	return app

app = create_app()

	







