import unittest
from app import create_app
import json

class TestChatbot(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def ask(self, message):
        response = self.client.post('/chatbot/ask', 
                                    data=json.dumps({'message': message}),
                                    content_type='application/json')
        return response

    def test_greeting(self):
        response = self.ask('Hello')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('University AI Assistant', data['response'])

    def test_enrollment(self):
        response = self.ask('How do I register?')
        data = json.loads(response.data)
        self.assertIn('Register', data['response'])

    def test_fees(self):
        response = self.ask('What is the fee?')
        data = json.loads(response.data)
        self.assertIn('payment', data['response'])

    def test_unknown(self):
        response = self.ask('blablabla')
        data = json.loads(response.data)
        self.assertIn('understand', data['response'])

if __name__ == '__main__':
    unittest.main()
