from rest_framework import viewsets, pagination,status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import date,datetime, timedelta
from .models import Agendamento
import requests
from django.shortcuts import render, redirect
from .models import Profissional, Servico, ProfissionalServico, Agendamento,Cliente, Prontuario
from .serializers import ProfissionalSerializer, ServicoSerializer, ProfissionalServicoSerializer, ProfissionalServicoDetalhadoSerializer, AgendamentoSerializer, ProntuarioSerializer, ClienteSerializer
from .forms import AgendamentoForm
from .permissions import IsProfissionalOrAdmin
from rest_framework.permissions import AllowAny
from .permissions import IsAuthenticatedAndNoDelete

class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer

class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer

class ProfissionalServicoViewSet(viewsets.ModelViewSet):
    queryset = ProfissionalServico.objects.all()
    serializer_class = ProfissionalServicoSerializer

class ProfissionalServicoDetalhadoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProfissionalServico.objects.all()
    serializer_class = ProfissionalServicoDetalhadoSerializer

class ProfissionalServicoAtivoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProfissionalServico.objects.filter(status=True)
    serializer_class = ProfissionalServicoSerializer
    pagination_class = pagination.LimitOffsetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit')
        if limit:
            self.pagination_class.default_limit = limit
        else:
            self.pagination_class.default_limit = 10
        return queryset
class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [AllowAny()]  # Cliente pode criar e listar sem login
        return [IsProfissionalOrAdmin()]  # Outras ações precisam de login

    def create(self, request, *args, **kwargs):
        # Se for cliente (sem autenticação), usa o fluxo de CPF
        if not request.user.is_authenticated:
            cpf = request.data.get('cpf')
            data_agendamento = request.data.get('data')
            hora_agendamento = request.data.get('hora')

            if not cpf or not data_agendamento or not hora_agendamento:
                return Response({"detail": "CPF, data e hora são necessários."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                cliente = Cliente.objects.get(cpf=cpf)
            except Cliente.DoesNotExist:
                return Response({"detail": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

            if Agendamento.objects.filter(cliente=cliente, data=data_agendamento, hora=hora_agendamento).exists():
                return Response({"detail": "Já existe um agendamento para essa data e hora."}, status=status.HTTP_400_BAD_REQUEST)

            profissional_servico_id = request.data.get('profissional_servico')
            try:
                profissional_servico = ProfissionalServico.objects.get(id=profissional_servico_id)
            except ProfissionalServico.DoesNotExist:
                return Response({"detail": "Profissional e serviço não encontrados."}, status=status.HTTP_404_NOT_FOUND)

            agendamento = Agendamento(cliente=cliente, profissional_servico=profissional_servico, data=data_agendamento, hora=hora_agendamento)
            agendamento.save()

            return Response({"detail": "Agendamento criado com sucesso!"}, status=status.HTTP_201_CREATED)
        
        # Se for profissional logado, usa o comportamento normal
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            cpf = request.query_params.get('cpf')

            if not cpf:
                return Response({"detail": "CPF é necessário para consulta."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                cliente = Cliente.objects.get(cpf=cpf)
            except Cliente.DoesNotExist:
                return Response({"detail": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

            queryset = Agendamento.objects.filter(cliente=cliente)
        else:
            # Profissional logado ou admin pode ver todos
            queryset = self.queryset

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# Views para renderização de páginas HTML com dados da API
def index(request):
    api_url = 'http://127.0.0.1:8000/api/profissional-servicos-ativos/?limit=3'
    response = requests.get(api_url)
    servicos_ativos = response.json() if response.status_code == 200 else []
    return render(request, 'index.html', {'servicos_ativos': servicos_ativos})


def profissionais(request):
    api_url = 'http://127.0.0.1:8000/api/profissionais/'
    response = requests.get(api_url)
    profissionais = response.json() if response.status_code == 200 else []
    return render(request, 'profissionais.html', {'profissionais': profissionais})


def servicos(request):
    api_url = 'http://127.0.0.1:8000/api/profissional-servicos-ativos/'
    response = requests.get(api_url)
    servicos_ativos = response.json() if response.status_code == 200 else []
    return render(request, 'servicos.html', {'servicos_ativos': servicos_ativos})


def agendamentos(request):
    profissional_servicos = ProfissionalServico.objects.filter(status=True)
    return render(request, 'agendamentos.html', {'profissional_servicos': profissional_servicos})


def contato(request):
    api_url = 'http://127.0.0.1:8000/api/profissional-servicos-ativos/'
    response = requests.get(api_url)
    servicos_ativos = response.json() if response.status_code == 200 else []
    return render(request, 'contato.html', {'servicos_ativos': servicos_ativos})

def profissionais(request):
    api_url = 'http://127.0.0.1:8000/api/profissionais/'
    response = requests.get(api_url)

    if response.status_code == 200:
        profissionais = response.json()
    else:
        profissionais = []

    context = {
        'profissionais': profissionais,
    }
    return render(request, 'profissionais.html', context)


def servicos(request):
    api_url = 'http://127.0.0.1:8000/api/profissional-servicos-ativos/'
    response = requests.get(api_url)

    if response.status_code == 200:
        servicos_ativos = response.json()
    else:
        servicos_ativos = []

    context = {
        'servicos_ativos': servicos_ativos,
    }

    return render(request, 'servicos.html', context)


def agendamentos(request):
    profissional_servicos = ProfissionalServico.objects.filter(status=True)
    return render(request, 'agendamentos.html', {'profissional_servicos': profissional_servicos})

def contato(request):
    api_url = 'http://127.0.0.1:8000/api/profissional-servicos-ativos/'
    response = requests.get(api_url)

    if response.status_code == 200:
        servicos_ativos = response.json()
    else:
        servicos_ativos = []

    context = {
        'servicos_ativos': servicos_ativos,
    }

    return render(request, 'contato.html', context)


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ProntuarioViewSet(viewsets.ModelViewSet):
    queryset = Prontuario.objects.all()
    serializer_class = ProntuarioSerializer
    permission_classes = [IsAuthenticatedAndNoDelete]

class DeletarAgendamentoView(APIView):
    def delete(self, request):
        cpf = request.data.get("cpf")
        data_str = request.data.get("data")

        try:
            data_agendamento = datetime.strptime(data_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "Formato de data inválido. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Busca o cliente pelo CPF
        try:
            cliente = Cliente.objects.get(cpf=cpf)
        except Cliente.DoesNotExist:
            return Response({"detail": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Busca o agendamento com esse cliente e data
        try:
            agendamento = Agendamento.objects.get(cliente=cliente, data=data_agendamento)
        except Agendamento.DoesNotExist:
            return Response({"detail": "Agendamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Verifica se está no prazo permitido para deletar
        hoje = datetime.now().date()
        if data_agendamento <= hoje + timedelta(days=1):
            return Response({"detail": "Cancelamento só é permitido com mais de 1 dia de antecedência."}, status=status.HTTP_403_FORBIDDEN)

        agendamento.delete()
        return Response({"detail": "Agendamento cancelado com sucesso."}, status=status.HTTP_204_NO_CONTENT)


from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib import messages

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            login_data = data.get('login')
            password = data.get('password')

            if not login_data or not password:
                return JsonResponse({'error': 'Por favor, forneça login e senha.'}, status=400)

            user = authenticate(request, username=login_data, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({'success': 'Login efetuado com sucesso.'})
            else:
                return JsonResponse({'error': 'Credenciais inválidas.'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Dados inválidos no corpo da requisição.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Ocorreu um erro: {str(e)}'}, status=500)
    else:
        return render(request, 'login.html')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('index')

def cadastrar(request):
    return render(request, 'cadastrar.html')
