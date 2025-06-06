# Generated by Django 5.2 on 2025-05-03 20:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('telefone', models.CharField(max_length=20)),
                ('cpf', models.CharField(max_length=14, unique=True)),
                ('data_nascimento', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField()),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Profissional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefone', models.CharField(max_length=20)),
                ('cpf', models.CharField(max_length=14, unique=True)),
                ('data_nascimento', models.DateField()),
                ('especialidade', models.CharField(max_length=100)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profissional', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfissionalServico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_inicio', models.DateField()),
                ('data_fim', models.DateField(blank=True, null=True)),
                ('taxa', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.BooleanField(default=True)),
                ('profissional', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fisiofacil.profissional')),
                ('servico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fisiofacil.servico')),
            ],
        ),
        migrations.CreateModel(
            name='Agendamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField()),
                ('hora', models.TimeField()),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fisiofacil.cliente')),
                ('profissional_servico', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fisiofacil.profissionalservico')),
            ],
        ),
        migrations.CreateModel(
            name='Prontuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observacoes', models.TextField()),
                ('consulta_emergencial', models.BooleanField(default=False)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('agendamento', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='fisiofacil.agendamento')),
            ],
        ),
    ]
