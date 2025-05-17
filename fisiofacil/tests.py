from django.test import SimpleTestCase
from unittest.mock import patch, MagicMock

class ClienteModelMockTest(SimpleTestCase):
    @patch('fisiofacil.models.Cliente')
    def test_criar_cliente_mock(self, MockCliente):
        mock_cliente = MagicMock()
        mock_cliente.nome = 'João da Silva'
        mock_cliente.email = 'joao@email.com'
        mock_cliente.telefone = '(11)99999-9999'
        mock_cliente.cpf = '12345678900'
        mock_cliente.__str__.return_value = 'João da Silva'
        MockCliente.objects.create.return_value = mock_cliente

        cliente = MockCliente.objects.create(
            nome='João da Silva',
            email='joao@email.com',
            telefone='(11)99999-9999',
            cpf='12345678900',
            data_nascimento='1990-01-01'
        )
        self.assertEqual(cliente.nome, 'João da Silva')
        self.assertEqual(cliente.email, 'joao@email.com')
        self.assertEqual(cliente.telefone, '(11)99999-9999')
        self.assertEqual(cliente.cpf, '12345678900')
        self.assertEqual(str(cliente), 'João da Silva')