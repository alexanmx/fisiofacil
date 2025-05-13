from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Profissional, Servico, ProfissionalServico, Agendamento, Cliente, Prontuario
from django.contrib.auth.models import User
from django.utils.formats import localize

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'email', 'telefone', 'cpf', 'data_nascimento']
        read_only_fields = ['id']

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        # use create_user para garantir hashing da senha
        return User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

class ProfissionalSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Profissional
        fields = ['id', 'nome', 'email', 'telefone',
                  'cpf', 'data_nascimento', 'especialidade', 'usuario']

    def create(self, validated_data):
        # retira os dados de usuário para criar primeiro o User
        usuario_data = validated_data.pop('usuario')
        user = UsuarioSerializer().create(usuario_data)

        # agora cria o Profissional referenciando o user
        profissional = Profissional.objects.create(usuario=user, **validated_data)
        return profissional

class ServicoSerializer(serializers.ModelSerializer):
    valor_formatado = serializers.SerializerMethodField(read_only=True)
    valor = serializers.DecimalField(max_digits=10, decimal_places=2)

    def get_valor_formatado(self, obj):
        return f"R$ {localize(obj.valor)}"

    class Meta:
        model = Servico
        fields = '__all__'
        # Se você não quiser o 'valor_formatado' durante a criação/edição,
        # pode explicitamente definir os campos que podem ser escritos:
        # fields = ('id', 'nome', 'descricao', 'valor')

class ProfissionalServicoSerializer(serializers.ModelSerializer):
    profissional_nome = serializers.SerializerMethodField()
    servico_nome = serializers.SerializerMethodField()
    servico_desc = serializers.SerializerMethodField()

    taxa = serializers.DecimalField(max_digits=10, decimal_places=2)
    taxa_formatada = serializers.SerializerMethodField(read_only=True)

    data_inicio = serializers.DateField(format="%d/%m/%Y")
    data_fim = serializers.DateField(format="%d/%m/%Y")

    def get_taxa_formatada(self, obj):
        return f"R$ {localize(obj.valor)}"

    def get_taxa(self, obj):
        # Formata o taxa da taxa como moeda brasileira
        return f"R$ {localize(obj.taxa)}"

    def get_profissional_nome(self, obj):
        return obj.profissional.nome
    
    def get_servico_nome(self, obj):
        return obj.servico.nome
    
    def get_servico_desc(self, obj):
        return obj.servico.descricao

    class Meta:
        model = ProfissionalServico
        fields = '__all__'
    
class ProfissionalServicoDetalhadoSerializer(serializers.ModelSerializer):
    profissional_nome = serializers.CharField(source='profissional.nome', read_only=True)
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    servico_desc = serializers.CharField(source='servico.descricao', read_only=True)
    servico_valor = serializers.DecimalField(source='servico.valor', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProfissionalServico
        fields = ['id', 'profissional_nome', 'servico_nome', 'servico_desc', 'servico_valor', 'data_inicio', 'data_fim', 'taxa', 'status']

class ProfissionalServicoBasicoSerializer(serializers.ModelSerializer):
    profissional_nome = serializers.CharField(source='profissional.nome', read_only=True)
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    servico_valor = serializers.DecimalField(source='servico.valor', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ProfissionalServico
        fields = ['id', 'profissional_nome', 'servico_nome', 'servico_valor', 'taxa']
        read_only_fields = ['id', 'profissional_nome', 'servico_nome', 'servico_valor', 'taxa']

class AgendamentoSerializer(serializers.ModelSerializer):
    profissional_servico = ProfissionalServicoBasicoSerializer(read_only=True)
    cliente = ClienteSerializer(read_only=True)
    cpf = serializers.CharField(write_only=True, required=False)
    data = serializers.DateField(format="%d/%m/%Y")
    hora = serializers.TimeField(format="%H:%M")
    taxa_formatada = serializers.SerializerMethodField()

    def get_taxa_formatada(self, obj):
        # Formata o valor da taxa como moeda brasileira
        return f"R$ {localize(obj.profissional_servico.taxa)}"
    
    # Recebe o CPF para associar ao cliente
    cpf = serializers.CharField(write_only=True)

    def validate(self, data):
        hora = data['hora']
        profissional_servico = data['profissional_servico']
        data_agendamento = data['data']

        if hora.minute != 0:
            raise ValidationError("Os horários de agendamento devem ser horas inteiras.")

        # Verifica se há conflitos de horário
        conflitos = Agendamento.objects.filter(
            profissional_servico=profissional_servico,
            data=data_agendamento,
            hora=hora
        ).exists()

        if conflitos:
            raise ValidationError("O profissional já tem um agendamento neste horário.")

        return data

    def create(self, validated_data):
        # Obtemos o CPF do cliente que vem na requisição
        cpf = validated_data.pop('cpf')

        # Verificamos se o cliente já existe no sistema
        try:
            cliente = Cliente.objects.get(cpf=cpf)
        except Cliente.DoesNotExist:
            raise ValidationError("Cliente não encontrado com o CPF fornecido.")

        # Agora associamos o cliente ao agendamento
        agendamento = Agendamento.objects.create(cliente=cliente, **validated_data)
        return agendamento

    class Meta:
        model = Agendamento
        fields = ['id', 'cliente', 'cpf', 'profissional_servico', 'data', 'hora', 'criado_em', 'taxa_formatada']
        read_only_fields = ['id', 'criado_em', 'cliente', 'profissional_servico', 'data', 'taxa_formatada'] # Tornar nested read-only
        write_only_fields = ['cpf']

class ProntuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prontuario
        fields = '__all__'
