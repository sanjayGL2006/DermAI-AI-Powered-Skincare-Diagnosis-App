import unittest
import json
import os
import time
from datetime import datetime, timedelta
from app import app, init_db, get_db, auto_purge_expired_images_and_data, AUTO_PURGE_SECONDS

class DermAITestSuite(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        self.client = app.test_client()
        with app.app_context():
            init_db()

    def test_01_database_initialization(self):
        """Test SQLite database schema initialization and tables existence."""
        with app.app_context():
            db = get_db()
            users = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';").fetchone()
            analyses = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='analyses';").fetchone()
            chats = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chats';").fetchone()
            self.assertIsNotNone(users)
            self.assertIsNotNone(analyses)
            self.assertIsNotNone(chats)

    def test_02_index_route(self):
        """Test home index route accessibility."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DermAI', response.data)
        self.assertIn(b'sanjay_logo.png', response.data)

    def test_03_privacy_route_and_branding(self):
        """Test Privacy & Security route, Sanjay GL logo branding, creation date 18 August 2026, and 5-hour auto-purge notice."""
        response = self.client.get('/privacy')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sanjay GL', response.data)
        self.assertIn(b'18 August 2026', response.data)
        self.assertIn(b'5-Hour 1-Minute', response.data)
        self.assertIn('nosniff', response.headers.get('X-Content-Type-Options', ''))
        self.assertIn('SAMEORIGIN', response.headers.get('X-Frame-Options', ''))

    def test_04_guest_login_and_analyze_page(self):
        """Test guest login route and access to /analyze."""
        response = self.client.get('/auth/guest', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Analyze', response.data)

    def test_05_api_analyze_endpoint(self):
        """Test skin analysis API endpoint with base64 image data."""
        # First authenticate guest session
        self.client.get('/auth/guest')
        
        # Sample minimal 1x1 pixel JPEG base64
        sample_b64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
        
        payload = {
            "image": sample_b64,
            "skin_type": "Combination",
            "answers": {"feel": "Oily T-Zone", "concern": "Acne"}
        }
        response = self.client.post('/api/analyze', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))
        self.assertIn('analysis_id', data)
        self.assertIn('analysis', data)

    def test_06_auto_purge_mechanism(self):
        """Test 5-Hour 1-Minute Auto-Purge logic for temporary image assets."""
        temp_dir = os.path.join('static', 'temp_scans')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create a test temp file with older timestamp
        test_file = os.path.join(temp_dir, 'test_expired_img.jpg')
        with open(test_file, 'w') as f:
            f.write('fake image data')
            
        # Modify mtime to 6 hours ago (21,600 seconds ago)
        old_time = time.time() - 21600
        os.utime(test_file, (old_time, old_time))
        
        # Run auto purge
        auto_purge_expired_images_and_data()
        
        # Assert file was automatically deleted
        self.assertFalse(os.path.exists(test_file))

    def test_07_static_logo_asset(self):
        """Test existence of Sanjay GL logo image asset."""
        logo_path = os.path.join('static', 'images', 'sanjay_logo.png')
        self.assertTrue(os.path.exists(logo_path))
        self.assertGreater(os.path.getsize(logo_path), 1000)

if __name__ == '__main__':
    unittest.main()
