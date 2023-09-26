from unittest import TestCase

from app import app
from models import db, Users, connect_db

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

app.config['TESTING'] = True


class BloglyTestCase(TestCase):

    def setUp(self):
        """stuff to do on mount"""
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_redirect_to_users(self):
        """Test Redirect to Users"""
        with app.test_client() as client:
            resp = client.get('/')
            self.assertEqual(resp.status_code, 302)
            self.assertIn(resp.location, 'http://localhost/users')

    def test_users(self):
        """Test Render Users"""
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<title>Users</title>', html)

    def test_users_new_form(self):
        """Test Users New Form"""
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<title>Create User</title>', html)

    def test_error(self):
        """Test Error Page"""
        with app.test_client() as client:
            resp = client.get('/users/999999')
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<title>Uh oh</title>', html)




