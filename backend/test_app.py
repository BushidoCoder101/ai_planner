import os
import unittest
import json
import tempfile

from ai_planner_app import create_app
from ai_planner_app.db import get_db, init_db

class BackendTestCase(unittest.TestCase):
    """Test suite for the Flask backend application."""

    def setUp(self):
        """Set up a test environment before each test."""
        self.db_fd, self.db_path = tempfile.mkstemp()

        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path,
        })

        self.client = self.app.test_client()

        with self.app.app_context():
            init_db()

    def tearDown(self):
        """Clean up the test environment after each test."""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_index_serves_html(self):
        """Test that the root URL serves the main HTML file."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Agent Command Center', response.data)

    def test_get_ideas_empty(self):
        """Test that GET /api/ideas returns an empty list when the DB is empty."""
        response = self.client.get('/api/ideas')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data), [])

    def test_save_and_get_ideas(self):
        """Test saving a new idea and then retrieving it."""
        test_goal = "Create a test suite"
        self.client.post('/api/execute', json={'goal': test_goal})

        response = self.client.get('/api/ideas')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['goal'], test_goal)

    def test_duplicate_ideas_are_ignored(self):
        """Test that saving a duplicate idea does not create a new entry."""
        test_goal = "Ensure database integrity"
        self.client.post('/api/execute', json={'goal': test_goal})
        self.client.post('/api/execute', json={'goal': test_goal}) # Post again

        response = self.client.get('/api/ideas')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1, "Duplicate idea should not be added.")

if __name__ == '__main__':
    unittest.main()