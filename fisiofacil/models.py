from django.db import models
import datetime

class Profissional(models.Model):
    nome = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    senha = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20)

    def __str__(self):
        return self.nome

class Servico(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome

class ProfissionalServico(models.Model):
    profissional = models.ForeignKey(Profissional, on_delete=models.CASCADE)
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_fim = models.DateField(null=True, blank=True)
    taxa = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.profissional.nome} - {self.servico.nome} - {self.status}"

class Agendamento(models.Model):
    profissional_servico = models.ForeignKey(ProfissionalServico, on_delete=models.CASCADE)
    data = models.DateField(default=datetime.date.today)
    hora = models.TimeField(default=datetime.time(0,0))
    cliente_nome = models.CharField(max_length=100)
    cliente_email = models.EmailField()
    cliente_telefone = models.CharField(max_length=20)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.profissional_servico} - {self.data} {self.hora}"