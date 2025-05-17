from django.test import SimpleTestCase

class IndexViewTest(SimpleTestCase):
    def test_index_page_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_template_used(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'index.html')