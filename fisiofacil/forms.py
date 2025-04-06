from django import forms
from .models import Agendamento

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['profissional_servico', 'data', 'hora', 'cliente_nome', 'cliente_telefone', 'cliente_email', 'observacoes']