from rest_framework import viewsets, pagination
import requests
from django.shortcuts import render, redirect
from .models import Profissional, Servico, ProfissionalServico, Agendamento,Cliente, Prontuario
from .serializers import ProfissionalSerializer, ServicoSerializer, ProfissionalServicoSerializer, ProfissionalServicoDetalhadoSerializer, AgendamentoSerializer, ProntuarioSerializer, ClienteSerializer
from .forms import AgendamentoForm
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib import messages

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

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ProntuarioViewSet(viewsets.ModelViewSet):
    queryset = Prontuario.objects.all()
    serializer_class = ProntuarioSerializer


# views públicas
def index(request):
    api_url = 'http://127.0.0.1:8000/api/profissional-servicos-ativos/?limit=3'
    response = requests.get(api_url)

    if response.status_code == 200:
        servicos_ativos = response.json()
    else:
        servicos_ativos = []

    context = {
        'servicos_ativos': servicos_ativos,
    }

    return render(request, 'index.html', context)


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


def contato(request):
    return render(request, 'contato.html')


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
    

def agendar(request):
    profissional_servicos = ProfissionalServico.objects.filter(status=True)
    return render(request, 'agendar.html', {'profissional_servicos': profissional_servicos})


# views administrativas
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# @login_required
def indexAdm(request):
    return render(request, 'profissional_index.html')

def agendamentosAdm(request):
    return render(request, 'profissional_agendamentos.html')