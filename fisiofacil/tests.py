from django.test import SimpleTestCase

class TemplateRenderTest(SimpleTestCase):
    def test_index_template_used(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'index.html')
        self.assertEqual(response.status_code, 200)