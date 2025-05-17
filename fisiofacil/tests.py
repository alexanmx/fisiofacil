from django.test import TestCase, Client
from django.contrib.auth.models import User

class SimpleViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username='admin', password='admin123', email='admin@test.com')
        self.client.login(username='admin', password='admin123')

    def test_index_adm_status_code(self):
        response = self.client.get('/adm/')
        self.assertEqual(response.status_code, 200)
