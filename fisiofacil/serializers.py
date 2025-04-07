from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Profissional, Servico, ProfissionalServico, Agendamento

class ProfissionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profissional
        fields = '__all__'

class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = '__all__'

class ProfissionalServicoSerializer(serializers.ModelSerializer):
    profissional_nome = serializers.SerializerMethodField()
    servico_nome = serializers.SerializerMethodField()
    servico_desc = serializers.SerializerMethodField()

    class Meta:
        model = ProfissionalServico
        fields = '__all__'

    def get_profissional_nome(self, obj):
        return obj.profissional.nome
    
    def get_servico_nome(self, obj):
        return obj.servico.nome
    
    def get_servico_desc(self, obj):
        return obj.servico.descricao
    
class ProfissionalServicoDetalhadoSerializer(serializers.ModelSerializer):
    profissional_nome = serializers.CharField(source='profissional.nome', read_only=True)
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    servico_desc = serializers.CharField(source='servico.descricao', read_only=True)
    servico_valor = serializers.DecimalField(source='servico.valor', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProfissionalServico
        fields = ['id', 'profissional_nome', 'servico_nome', 'servico_desc', 'servico_valor', 'data_inicio', 'data_fim', 'taxa', 'status']

class AgendamentoSerializer(serializers.ModelSerializer):
    profissional_servico = serializers.PrimaryKeyRelatedField(
        queryset=ProfissionalServico.objects.filter(status=True)
    )
    
    def validate(self, data):
        hora = data['hora']
        profissional_servico = data['profissional_servico']
        data_agendamento = data['data']

        if hora.minute != 0:
            raise ValidationError("Os horários de agendamento devem ser horas inteiras.")

        conflitos = Agendamento.objects.filter(
            profissional_servico=profissional_servico,
            data=data_agendamento,
            hora=hora
        ).exists()

        if conflitos:
            raise ValidationError("O profissional já tem um agendamento neste horário.")

        return data

    class Meta:
        model = Agendamento
        fields = '__all__'