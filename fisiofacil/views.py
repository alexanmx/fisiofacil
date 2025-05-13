from rest_framework import viewsets, pagination, status
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
import requests
from django.shortcuts import render, redirect
from .models import Profissional, Servico, ProfissionalServico, Agendamento, Cliente, Prontuario
from .serializers import ProfissionalSerializer, ServicoSerializer, ServicoListSerializer, ProfissionalServicoSerializer, ProfissionalServicoDetalhadoSerializer, AgendamentoSerializer, ProntuarioSerializer, ClienteSerializer
from .forms import AgendamentoForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from .permissions import IsProfissionalOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsAuthenticatedAndNoDelete
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import logout

import os


class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.all()
    serializer_class = ProfissionalSerializer

class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoListSerializer

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


# Views para renderização de páginas HTML com dados da API
def index(request):
    api_url = f'{settings.API_BASE_URL}/api/profissional-servicos-ativos/?limit=3'
    response = requests.get(api_url)
    servicos_ativos = response.json() if response.status_code == 200 else []
    user = request.user if request.user.is_authenticated else None  # Obtém o usuário do Django, se autenticado
    return render(request, 'index.html', {'servicos_ativos': servicos_ativos, 'user': user})

def profissionais(request):
    api_url = f'{settings.API_BASE_URL}/api/profissionais/'
    response = requests.get(api_url)
    profissionais = response.json() if response.status_code == 200 else []
    return render(request, 'profissionais.html', {'profissionais': profissionais})

def servicos(request):
    api_url = f'{settings.API_BASE_URL}/api/profissional-servicos-ativos/'
    response = requests.get(api_url)
    servicos_ativos = response.json() if response.status_code == 200 else []
    return render(request, 'servicos.html', {'servicos_ativos': servicos_ativos})

def agendamentos(request):
    profissional_servicos = ProfissionalServico.objects.filter(status=True)
    return render(request, 'agendamentos.html', {'profissional_servicos': profissional_servicos})

def contato(request):
    return render(request, 'contato.html')

def agendar(request):
    profissional_servicos = ProfissionalServico.objects.filter(status=True)
    return render(request, 'agendar.html', {'profissional_servicos': profissional_servicos})

def obter_token_jwt(username, password):
    """Obtém o token JWT da API externa."""
    auth_url = f'{settings.API_BASE_URL}/api/token/'  # Defina isso em settings.py
    payload = {'username': username, 'password': password}  # Adapte conforme a API
    try:
        response = requests.post(auth_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get('access')  # Adapte conforme a resposta da API
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter token JWT: {e}")
        if hasattr(response, 'status_code'):
            print(f"Código de status da resposta: {response.status_code}")
        if hasattr(response, 'text'):
            print(f"Corpo da resposta: {response.text}")
        return None

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Autentica o usuário no Django
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token = obter_token_jwt(username, password)
            if token:
                request.session['jwt_token'] = token
                return JsonResponse({'status': 'success', 'redirect': reverse('profissionais')})
            else:
                return JsonResponse({'status': 'error', 'message': 'Erro ao obter token JWT.'}, status=400)
        else:
            return JsonResponse({'status': 'error', 'message': 'Usuário ou senha inválidos.'}, status=400)
    else:
        # Se não for POST, apenas renderiza o formulário de login
        return render(request, 'login.html')

def logout_view(request):
    logout(request)  # Limpa a sessão do Django (opcional, mas bom manter)
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('index')  # Redireciona para a página inicial   

def cadastrar(request):
    return render(request, 'cadastrar.html')

def meusAgendamentos(request):
    cpf = request.GET.get('cpf')
    api_url = f'{settings.API_BASE_URL}/api/agendamentos/?cpf={cpf}'
    response = requests.get(api_url)
    agendamentos = response.json() if response.status_code == 200 else []
    return render(request, 'meus_agendamentos.html', {'agendamentos': agendamentos})


# views administrativas
def indexAdm(request):
    if 'jwt_token' in request.session:
        return render(request, 'profissional_index.html')
    else:
        return HttpResponse("Acesso não autorizado", status=401)

def cadastrarUsuarioAdm(request):
    if 'jwt_token' in request.session:
        return render(request, 'profissional_cadastrarUsuario.html')
    else:
        return HttpResponse("Acesso não autorizado", status=401)

def listarUsuarioAdm(request):
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/profissionais/'
        response = requests.get(api_url)
        usuarios = response.json() if response.status_code == 200 else []
        return render(request, 'profissional_listarUsuario.html', {'usuarios': usuarios})
    else:
        return HttpResponse("Acesso não autorizado", status=401)

def editarUsuarioAdm(request, usuario_id):
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/profissionais/{usuario_id}/'
        response = requests.get(api_url)
        if response.status_code == 200:
            usuario = response.json()
            return render(request, 'profissional_editarUsuario.html', {'usuario': usuario})
        else:
            return HttpResponse("Usuário não encontrado", status=404)
    else:
        return HttpResponse("Acesso não autorizado", status=401)

def cadastrarServicoAdm(request):
    if 'jwt_token' in request.session:
        return render(request, 'profissional_cadastrarServico.html')
    else:
        return HttpResponse("Acesso não autorizado", status=401)
    
def listarServicoAdm(request):
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/servicos/'
        response = requests.get(api_url)
        servicos = response.json() if response.status_code == 200 else []
        return render(request, 'profissional_listarServico.html', {'servicos': servicos})
    else:
        return HttpResponse("Acesso não autorizado", status=401)
    
def editarServicoAdm(request, servico_id):
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/servicos/{servico_id}/'
        response = requests.get(api_url)
        if response.status_code == 200:
            servico = response.json()
            return render(request, 'profissional_editarServico.html', {'servico': servico})
        else:
            return HttpResponse("Serviço não encontrado", status=404)
    else:
        return HttpResponse("Acesso não autorizado", status=401)

def atribuirProfissionalAdm(request):
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/servicos/'
        response = requests.get(api_url)
        servicos = response.json() if response.status_code == 200 else []

        # lista profissionais
        api_url = f'{settings.API_BASE_URL}/api/profissionais/'
        response = requests.get(api_url)
        profissionais = response.json() if response.status_code == 200 else []

        return render(request, 'profissional_atribuirProfissional.html', {'servicos': servicos, 'profissionais': profissionais})
    else:
        return HttpResponse("Acesso não autorizado", status=401)

def servicosProfissionalAdm(request):
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/profissional-servicos-ativos/'
        response = requests.get(api_url)
        servicos = response.json() if response.status_code == 200 else []
        return render(request, 'profissional_listarServicosProfissionais.html', {'servicos': servicos})
    else:
        return HttpResponse("Acesso não autorizado", status=401)

def cadastrarAgendamentoAdm(request):
    if 'jwt_token' in request.session:
        profissional_servicos = ProfissionalServico.objects.filter(status=True)
        return render(request, 'profissional_cadastrarAgendamento.html', {'profissional_servicos': profissional_servicos})
    else:
        return HttpResponse("Acesso não autorizado", status=401)

def listarAgendamentoAdm(request):
    if 'jwt_token' in request.session:
        jwt_token = request.session['jwt_token']
        headers = {'Authorization': f'Bearer {jwt_token}'}
        api_url = f'{settings.API_BASE_URL}/api/agendamentos/'
        response = requests.get(api_url, headers=headers)
        agendamentos = response.json() if response.status_code == 200 else []
        return render(request, 'profissional_listarAgendamento.html', {'agendamentos': agendamentos})