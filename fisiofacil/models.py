from django.db import models
import datetime
from django.contrib.auth.models import User

class Profissional(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profissional')
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    especialidade = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)


    def __str__(self):
        return self.nome

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    duracao = models.DurationField()

    def __str__(self):
        return self.nome

class ProfissionalServico(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    # campos removidos
    
    # Remova o campo taxa, pois ele deve ser derivado de Servico.valor
    @property
    def taxa(self):
        return self.servico.valor
    
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.profissional.nome} - {self.servico.nome} - {self.status}"
    
class Cliente(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()

    def __str__(self):
        return f"{self.nome} - {self.cpf}"

class Agendamento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    profissional_servico = models.ForeignKey(ProfissionalServico, on_delete=models.CASCADE)
    data = models.DateField()
    hora = models.TimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    tratamento = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    tratamento = models.TextField(blank=True, null=True)


    def __str__(self):
       return f"{self.cliente.nome} - {self.data} {self.hora} - {self.profissional_servico}"

class Prontuario(models.Model):
    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE)
    observacoes = models.TextField()
    consulta_emergencial = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prontuário de {self.agendamento.cliente.nome} em {self.agendamento.data}"


class Pagamento(models.Model):
    agendamento = models.OneToOneField(Agendamento, on_delete=models.CASCADE, related_name='pagamento')
    data_criacao = models.DateTimeField(auto_now_add=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, default='pendente')

    def __str__(self):
        return f"Pagamento para Agendamento #{self.agendamento.id} - Status: {self.status}"
