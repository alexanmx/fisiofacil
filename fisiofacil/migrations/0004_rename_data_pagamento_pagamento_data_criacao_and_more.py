# Generated by Django 5.2 on 2025-05-17 16:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fisiofacil', '0003_agendamento_status_agendamento_tratamento_pagamento'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pagamento',
            old_name='data_pagamento',
            new_name='data_criacao',
        ),
        migrations.RenameField(
            model_name='pagamento',
            old_name='valor_pago',
            new_name='valor',
        ),
        migrations.RemoveField(
            model_name='pagamento',
            name='forma_pagamento',
        ),
        migrations.RemoveField(
            model_name='pagamento',
            name='observacoes',
        ),
        migrations.AddField(
            model_name='pagamento',
            name='metodo_pagamento',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='pagamento',
            name='agendamento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagamento', to='fisiofacil.agendamento'),
        ),
        migrations.AlterField(
            model_name='pagamento',
            name='status',
            field=models.CharField(default='pendente', max_length=20),
        ),
    ]
