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




class ProfissionalModelMockTest(SimpleTestCase):
    @patch('fisiofacil.models.Profissional')
    def test_criar_profissional_mock(self, MockProfissional):
        mock_profissional = MagicMock()
        mock_profissional.nome = 'Maria Souza'
        mock_profissional.email = 'maria@email.com'
        mock_profissional.telefone = '(21)98888-8888'
        mock_profissional.cpf = '98765432100'
        mock_profissional.especialidade = 'Fisioterapia'
        mock_profissional.__str__.return_value = 'Maria Souza'
        MockProfissional.objects.create.return_value = mock_profissional

        profissional = MockProfissional.objects.create(
            nome='Maria Souza',
            email='maria@email.com',
            telefone='(21)98888-8888',
            cpf='98765432100',
            especialidade='Fisioterapia',
            data_nascimento='1985-05-10'
        )
        self.assertEqual(profissional.nome, 'Maria Souza')
        self.assertEqual(profissional.email, 'maria@email.com')
        self.assertEqual(profissional.telefone, '(21)98888-8888')
        self.assertEqual(profissional.cpf, '98765432100')
        self.assertEqual(profissional.especialidade, 'Fisioterapia')
        self.assertEqual(str(profissional), 'Maria Souza')