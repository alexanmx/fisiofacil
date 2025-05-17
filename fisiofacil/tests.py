from django.test import TestCase
from .models import Cliente

class ClienteModelTest(TestCase):
    def test_criar_cliente(self):
        cliente = Cliente.objects.create(
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