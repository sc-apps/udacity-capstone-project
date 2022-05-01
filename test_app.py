import os
from os import environ
#from dotenv import find_dotenv, load_dotenv
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import db, setup_db, Event, Request


class TestCase(unittest.TestCase):

    def setUp(self):
        #ENV_FILE = find_dotenv()
        #if ENV_FILE:
        #    load_dotenv(ENV_FILE)
        database_name = os.environ.get("database_name_test")
        admin_token = os.environ.get("admin_token")

        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = "postgresql://{}/{}".format('localhost:5432', database_name)
        setup_db(self.app, self.database_path)

        #includes token with Admin role
        self.headers = {"Authorization": "Bearer {}".format(admin_token),
                        "Content-Type": "application/x-www-form-urlencoded"}
        
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()
    
    
    def tearDown(self):
        pass


    def test_get_home(self):
        res = self.client().get('/')

        self.assertEqual(res.status_code, 200)


    def test_405_get_home(self):
        res = self.client().patch('/')
        self.assertEqual(res.status_code, 405)
    
    # testing this endpoint with Recipient role who has permissions to access this page (Ted)
    def test_get_AddForm(self):
        #ENV_FILE = find_dotenv()
        #if ENV_FILE:
        #    load_dotenv(ENV_FILE)
        recipient_token = os.environ.get("recipient_token")
        res = self.client().get('/requests/add', headers={"Authorization":"Bearer {}".format(recipient_token)})
        self.assertEqual(res.status_code, 200)
    
    #testing with a wrong token
    def test_401_get_AddForm(self):
        res = self.client().get('/requests/add', headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"})
        self.assertEqual(res.status_code, 401)

    # testing this endpoint with a user who has Admin role (Patt)
    def test_get_AddEvent(self):
        res = self.client().get('/events/add', headers=self.headers)
        self.assertEqual(res.status_code, 200)

    # testing this endpoint with Recipient role who doesn't have permissions to access this page (Ted)
    def test_403_get_AddEvent(self):
        #ENV_FILE = find_dotenv()
        #if ENV_FILE:
        #    load_dotenv(ENV_FILE)
        recipient_token = os.environ.get("recipient_token")
        res = self.client().get('/events/add', headers={"Authorization":"Bearer {}".format(recipient_token)})
        self.assertEqual(res.status_code, 403)

    # testing this endpoint with a user who has Admin role (Patt)
    def test_get_all_requests(self):
        res = self.client().get('/requests', headers=self.headers)
        self.assertEqual(res.status_code, 200)

    # testing this endpoint with a user who doesn't have Admin or Recipient role to access this page (Kelly)
    def test_403_get_all_requests(self):
        #ENV_FILE = find_dotenv()
        #if ENV_FILE:
        #    load_dotenv(ENV_FILE)
        without_role_token = os.environ.get("without_role_token")
        res = self.client().get('/requests', headers={"Authorization":"Bearer {}".format(without_role_token)})
        self.assertEqual(res.status_code, 403)

    def test_get_specific_requests(self):
        res = self.client().get('/requests/3', headers=self.headers)
        self.assertEqual(res.status_code, 200)

    def test_404_get_specific_requests(self):
        res = self.client().get('/requests/100', headers=self.headers)
        self.assertEqual(res.status_code, 404)

    def test_delete_specific_request(self):
        res = self.client().post('/requests/4/delete', headers=self.headers)
        self.assertEqual(res.status_code, 200)

    def test_404_delete_specific_request(self):
        res = self.client().post('/requests/100/delete', headers=self.headers)
        self.assertEqual(res.status_code, 404)

if __name__ == "__main__":
    unittest.main()
