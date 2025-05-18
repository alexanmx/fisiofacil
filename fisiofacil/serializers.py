from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Pagamento, Profissional, Servico, ProfissionalServico, Agendamento, Cliente, Prontuario
from django.contrib.auth.models import User
from django.utils.formats import localize

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nome', 'email', 'telefone', 'cpf', 'data_nascimento']
        read_only_fields = ['id']

class UsuarioSerializer(serializers.ModelSerializer):
    is_superuser = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True}
        }

    def create(self, validated_data):
        is_superuser = validated_data.pop('is_superuser', False)
        # Converte string para booleano se necessário
        if isinstance(is_superuser, str):
            is_superuser = is_superuser.lower() == 'true'
        if is_superuser:
            user = User.objects.create_superuser(
                username=validated_data['username'],
                password=validated_data['password']
            )
        else:
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password']
            )
        return user

class ProfissionalSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer()

    class Meta:
        model = Profissional
        fields = ['id', 'nome', 'email', 'telefone',
                  'cpf', 'data_nascimento', 'especialidade', 'usuario','ativo']

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

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = '__all__'
        read_only_fields = ['id', 'data_criacao', 'agendamento'] # 'agendamento' será definido no create

class AgendamentoSerializer(serializers.ModelSerializer):
    profissional_servico_info = ProfissionalServicoBasicoSerializer(read_only=True, source='profissional_servico')
    profissional_servico = serializers.PrimaryKeyRelatedField(queryset=ProfissionalServico.objects.all(), write_only=True)
    cliente_info = ClienteSerializer(read_only=True, source='cliente')
    cpf = serializers.CharField(write_only=True, required=False)
    data = serializers.DateField(format="%d/%m/%Y")
    hora = serializers.TimeField(format="%H:%M")
    taxa_formatada = serializers.SerializerMethodField()
    tratamento = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False, allow_blank=True)
    pagamento = PagamentoSerializer(read_only=True)

    def get_taxa_formatada(self, obj):
        # Formata o valor da taxa como moeda brasileira
        return f"R$ {localize(obj.profissional_servico.taxa)}"
    
    # Recebe o CPF para associar ao cliente
    cpf = serializers.CharField(write_only=True)

    def validate(self, data):
        # --- INÍCIO: se for PATCH/PUT (atualização), pula toda a validação abaixo ---
        if self.instance:
            return data
        # --- FIM: validações apenas para criação (POST) ---
        
         # Criação exige profissional_servico
        if 'profissional_servico' not in data:
            raise ValidationError({"profissional_servico": "Este campo é obrigatório na criação."})


        profissional_servico_id = data['profissional_servico']
        if isinstance(profissional_servico_id, str) and profissional_servico_id.isdigit():
            try:
                profissional_servico = ProfissionalServico.objects.get(pk=int(profissional_servico_id))
                data['profissional_servico'] = profissional_servico # Substitui o ID pelo objeto para uso posterior
            except ProfissionalServico.DoesNotExist:
                raise ValidationError("Profissional e serviço não encontrados.")
        elif isinstance(profissional_servico_id, ProfissionalServico):
            profissional_servico = profissional_servico_id
        else:
            raise ValidationError("Valor inválido para profissional_servico.")

        if 'hora' not in data:
            raise ValidationError("O campo hora é obrigatório.")
        hora = data['hora']

        if 'data' not in data:
            raise ValidationError("O campo data é obrigatório.")
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

        # Extrai o profissional_servico do validated_data
        profissional_servico = validated_data.get('profissional_servico')

        # Verificamos se o cliente já existe no sistema
        try:
            cliente = Cliente.objects.get(cpf=cpf)
        except Cliente.DoesNotExist:
            raise ValidationError("Cliente não encontrado com o CPF fornecido.")

        # Agora associamos o cliente ao agendamento
        agendamento = Agendamento.objects.create(cliente=cliente, **validated_data)

        # Cria o pagamento associado
        Pagamento.objects.create(agendamento=agendamento, valor=profissional_servico.taxa)

        return agendamento

    class Meta:
        model = Agendamento
        fields = ['id', 'cliente_info', 'cpf', 'profissional_servico', 'profissional_servico_info', 'data', 'hora', 'criado_em', 'taxa_formatada', 'status', 'tratamento', 'pagamento']
        read_only_fields = ['id', 'criado_em', 'cliente_info', 'profissional_servico_info', 'data', 'taxa_formatada', 'pagamento']
        write_only_fields = ['cpf', 'profissional_servico'] # 'profissional_servico' agora é write_only

class ProntuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prontuario
        fields = '__all__'