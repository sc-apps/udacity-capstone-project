

################################################
Motivation for the project
################################################

Unfortunately, some people struggle to survive and don't have sufficient funds to buy a gift for their children. The Secret Santa web app makes the dreams of these children come true by gathering together people who want to be a Secret Santa with those who are in need.


################################################
Base URL
################################################

At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, http:127.0.0.1:5000/, which is set as a proxy in the frontend configuration.


################################################
Instructions
################################################
To test locally:
1. Create a virtual environment

2. Install dependencies from requirements.txt file in the activated virtual environment
	- pip install -r requirements.txt

3. Setup database
	- Create appdb
	  Command in Terminal: createdb appdb

	- Copy db from appdb.psql to your appdb to have the db with a few records created
	  Command in Terminal: psql appdb < appdb.psql

4. To run the development server, run these commands in Terminal in the activated virtual environment:
	- export FLASK_APP=app.py
	- export FLASK_ENV=development
	- flask run

5. Use the provided accounts to log in and test the app
	- A user with name Patt has Admin role assigned
	- A user with name Ted has Recipient role assigned
	- A user with name Kelly who doesn't have any role assigned
	- You can also register a new user, that user won't have any role. The functionality will be similar to Kelly

6. To run tests:
	- Update tokens in .env file
	- Create test_appdb DB (createdb test_appdb) and copy data from appdb to test_appdb (psql test_appdb < appdb.psql)
	- Then run tests: python3 test_app.py


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










