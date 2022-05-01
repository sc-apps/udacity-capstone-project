

################################################
Motivation for the project
################################################

Unfortunately, some people struggle to survive and don't have sufficient funds to buy a gift for their children. The Secret Santa web app makes the dreams of these children come true by gathering together people who want to be a Secret Santa with those who are in need.


################################################
Base URL
################################################

You can test the app at Heroku: https://myapp-5566.herokuapp.com/ or locally http:127.0.0.1:5000/


################################################
Instructions
################################################

To test locally:
1. Create a virtual environment

2. Set up environment variables
	Run in Terminal in activated virtual environment:
	chmod +x setup.sh
	source setup.sh

3. Install dependencies from requirements.txt file in the activated virtual environment
	- pip install -r requirements.txt

4. Add data into .env file
	- Update all variables where information is missing and add provided tokens

5. Setup database
	- Create appdb
	  Command in Terminal: createdb appdb

	- Copy db from appdb.psql to your appdb to have the db with a few records created
	  Command in Terminal: psql appdb < appdb.psql

6. To run the development server, run these commands in Terminal in the activated virtual environment:
	- export FLASK_APP=app.py
	- export FLASK_ENV=development
	- flask run

7. Use the provided accounts to log in and test the app
	- A user with name Patt has Admin role assigned
	- A user with name Ted has Recipient role assigned
	- A user with name Kelly who doesn't have any role assigned
	- You can also register a new user, that user won't have any role. The functionality will be similar to Kelly

8. To run tests:
	- Update tokens in .env file
	- Create test_appdb DB (createdb test_appdb) and copy data from appdb to test_appdb (psql test_appdb < appdb.psql)
	- Then run tests: python3 test_app.py

----------------------------------------------------

To deploy and test in Heroku:
1. Create .git folder
	- Run command: git init

2. Create an app in Heroku
	- Run command: heroku create [some unique app name] --buildpack heroku/python

3. Add PostgreSQL database
	- Run command: heroku adding:create heroku-postgresql:hobby-dev --app [name of the app created above]

4. Configure app in Heroku
	- Get database_path by running this command:
	heroku config -app [app name]
	- Copy the output DB path, i.e. postgres://....
	- Make change in models.py by uncommenting and commenting a few lines
	- Export database_path by running the command with copied db path:
	export database_path="postgresql://...." (postgres:// might not be recognized, because of that export postgresql://)
	- Add other variables from setup.sh to heroku app by navigating to Heroku dashboard >> Particular App >> Settings >> Reveal Config Vars

5. Deploy code
	- Add the code to git
	git add -A or git add .
	git commit -m "First commit"
	git push heroku master

6. Migrate the database
	Run command: heroku run python manage.py db upgrade --app [app name]

################################################
Endpoints:
################################################

GET '/'

Description: either asks the user to authenticate or shows available requests.

Auth requirements:
1. If user is not authenticated, a simple welcome page is shown asking the user to authenticate
2. If the user is authenticated, the user can view available requests raised by different users

----------------------------------------------------------------------------------------------

GET, POST '/requests/add'

Description: loads the AddForm which which a user can fill out to submit a new request.

Auth requirements:
1. The user has to be authenticated and provide a valid token to perform both API calls
2. The user must have either Admin or Recipient role (verified in the payload of the provided token)

----------------------------------------------------------------------------------------------

GET, POST '/events/add'

Description: loads the AddEvent form which a user can fill out to submit a new event.

Auth requirements:
1. The user has to be authenticated and provide a valid token to perform both API calls
2. The user must have the Admin role (verified in the payload of the provided token)

----------------------------------------------------------------------------------------------

GET '/requests'

Description: shows available requests by clicking on which a user can modify certain requests. The user cannot modify requests that were already taken by Secret Santa users.

Auth requirements:
1. The user has to be authenticated and provide a valid token to perform both API calls
2. The user must have either Admin or Recipient role (verified in the payload of the provided token)
	- The user with Admin role can view and access all requests
	- The user with Recipient role can view only own requests and can access only those that weren't taken (request.taken = False)

----------------------------------------------------------------------------------------------

GET, POST '/requests/<int:request_id>'

Description: shows a request with provided id and allows the user to modify data and patch the available record in the database.

Auth requirements:
1. The user has to be authenticated and provide a valid token to perform both API calls
2. The user must have either Admin or Recipient role (verified in the payload of the provided token)
	- The user with Admin role can view and modify all data in any request (event the one which was taken)
	- The user with Recipient role can view and modify only own requests that weren't taken. Child Name and Child Age cannot be updated the by user with this role, only Admin has this right

----------------------------------------------------------------------------------------------

POST '/requests/<int:request_id>/delete'

Description: deletes the record with provided id.

Auth requirements:
1. The user has to be authenticated and provide a valid token to perform both API calls
2. The user must have either Admin or Recipient role (verified in the payload of the provided token)
	- The user with Admin role can delete any request
	- The user with Recipient role can delete only own requests that weren't taken


################################################
Error handling
################################################

Errors are returned as JSON objects in the following format:

{
  "success": False,
  "error": 404,
  "message": "resource not found"
}

The API will return six error types when requests fail:
400: Invalid header
401: Token expired
403: Access forbidden
404: Resource Not Found
405: Method Not Allowed
422: Unprocessable










