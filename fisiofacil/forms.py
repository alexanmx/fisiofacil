from django import forms
from .models import Agendamento

class AgendamentoForm(forms.ModelForm):
    class Meta:
        model = Agendamento
        fields = ['profissional_servico', 'cliente', 'data', 'hora', 'observacoes']
