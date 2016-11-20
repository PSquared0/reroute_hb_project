from unittest import TestCase
from server import app
from model import Stop, Bus, Rating, User, Bus_filter, Filter, connect_to_db, db
from reroute import get_bus_list

class FlaskTest(TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def get_bus_list(self):

        buses = db.session.query(Bus.bus_name).all()
        self.assertIsNotNone(buses)


if __name__ == "__main__":
    import unittest

    unittest.main()
