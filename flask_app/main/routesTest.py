import unittest
from flask import Flask
from flask_app import create_app
from flask_app.main.routes import main

class RoutesTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.client.testing = True

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Home - Speckle Invoice", response.get_data(as_text=True))

    def test_signup_route(self):
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sign Up - Speckle Invoice", response.get_data(as_text=True))

    def test_signin_route(self):
        response = self.client.get('/signin')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sign In - Speckle Invoice", response.get_data(as_text=True))

    def test_dashboard_route(self):
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Dashboard - Speckle Invoice", response.get_data(as_text=True))

    def test_forgot_route(self):
        response = self.client.get('/forgot')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Forgot Password - Speckle Invoice", response.get_data(as_text=True))

    def test_sitemap_route(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "application/xml")

    def test_robots_txt_route(self):
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/plain")

    def test_home_page_title_in_meta(self):
        response = self.client.get('/')
        self.assertIn('<title>Home - Speckle Invoice</title>', response.get_data(as_text=True))

    def test_signup_page_title_in_meta(self):
        response = self.client.get('/signup')
        self.assertIn('<title>Sign Up - Speckle Invoice</title>', response.get_data(as_text=True))

    def test_dashboard_page_title_in_meta(self):
        response = self.client.get('/dashboard')
        self.assertIn('<title>Dashboard - Speckle Invoice</title>', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()
