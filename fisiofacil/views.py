import os
import requests

from rest_framework import viewsets, pagination, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from .models import Profissional, Servico, ProfissionalServico, Agendamento, Cliente, Prontuario, Pagamento
from .serializers import ProfissionalSerializer, ServicoSerializer, ProfissionalServicoSerializer, ProfissionalServicoDetalhadoSerializer, AgendamentoSerializer, ProntuarioSerializer, ClienteSerializer, PagamentoSerializer
from .forms import AgendamentoForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib import messages
from .permissions import IsProfissionalOrAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsAuthenticatedAndNoDelete, IsSuperUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q



class ProfissionalViewSet(viewsets.ModelViewSet):
    queryset = Profissional.objects.select_related('usuario').all()
    serializer_class = ProfissionalSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'nome', 'usuario__email', 'telefone','especialidade', 'usuario__username']



class ServicoViewSet(viewsets.ModelViewSet):
    queryset = Servico.objects.all()
    serializer_class = ServicoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome','descricao', 'valor']
   


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
    filter_backends = [filters.SearchFilter]
    search_fields = ['data', 'status', 'cliente__nome']

    def get_permissions(self):
        if self.action in ['create', 'list']:
            return [AllowAny()]
        return [IsProfissionalOrAdmin()]

    def create(self, request, *args, **kwargs):
            if not request.user.is_authenticated:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return super().create(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        agendamento = self.get_object()

        if 'tratamento' in request.data:
            if request.user != agendamento.profissional_servico.profissional.usuario:
                # raise PermissionDenied("Você não tem permissão para atualizar o campo 'tratamento' deste agendamento.")
                return Response({"detail": "Você não tem permissão para atualizar o campo 'tratamento' deste agendamento."}, status=status.HTTP_400_BAD_REQUEST)

        return super().partial_update(request, *args, **kwargs)

    
    def list(self, request, *args, **kwargs):
        
        if not request.user.is_authenticated:
            cpf = request.query_params.get('cpf')
            search_query = request.query_params.get('search')
            
            if not cpf:
                return Response({"detail": "CPF é necessário para consulta."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                cliente = Cliente.objects.get(cpf=cpf)
            except Cliente.DoesNotExist:
                return Response({"detail": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)
            queryset = Agendamento.objects.filter(cliente=cliente)

            if search_query:
                queryset = queryset.filter(
                    Q(data__icontains=search_query) |
                    Q(status__icontains=search_query) |
                    Q(profissional_servico__profissional__nome__icontains=search_query)
                )
        elif request.user.is_superuser:
            queryset = self.queryset
            search_query = request.GET.get('search', '')
            if search_query:
                queryset = queryset.filter(
                    Q(data__icontains=search_query) |
                    Q(status__icontains=search_query) |
                    Q(cliente__nome__icontains=search_query)
                )
        else:
            # try:
            #     profissional = Profissional.objects.get(usuario=request.user)
            # except Profissional.DoesNotExist:
            #     return Response({"detail": "Profissional não encontrado."}, status=status.HTTP_404_NOT_FOUND)
            # queryset = Agendamento.objects.filter(profissional_servico__profissional=profissional)
            # print("cai no else")
            queryset = self.queryset
            search_query = request.GET.get('search', '')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'nome', 'email', 'telefone', 'cpf', 'data_nascimento']  



class ProntuarioViewSet(viewsets.ModelViewSet):
    queryset = Prontuario.objects.all()
    serializer_class = ProntuarioSerializer
    permission_classes = [IsAuthenticatedAndNoDelete]



class DeletarAgendamentoView(APIView):
    
    def delete(self, request):
        cpf = request.data.get("cpf")
        idAgendamento = request.data.get("agendamento_id")

        try:
            cliente = Cliente.objects.get(cpf=cpf)
        except Cliente.DoesNotExist:
            return Response({"detail": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        try:
            agendamento = Agendamento.objects.get(cliente=cliente, id=idAgendamento, status='agendado')
        except Agendamento.DoesNotExist:
            return Response({"detail": "Agendamento não permite cancelamento."}, status=status.HTTP_404_NOT_FOUND)
        
        agendamento.status = 'cancelado_pelo_cliente'
        agendamento.save()
        return Response({"detail": "Agendamento cancelado com sucesso."}, status=status.HTTP_204_NO_CONTENT)    


class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['id', 'valor', 'status']



class TratamentosPorCPFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cpf = request.GET.get('cpf')
        if not cpf:
            return Response({'detail': 'CPF é obrigatório.'}, status=400)

        try:
            cliente = Cliente.objects.get(cpf=cpf)
        except Cliente.DoesNotExist:
            return Response({'detail': 'Cliente não encontrado.'}, status=404)

        try:
            profissional = Profissional.objects.get(usuario=request.user)
        except Profissional.DoesNotExist:
            return Response({'detail': 'Profissional não encontrado.'}, status=404)

        agendamentos = Agendamento.objects.filter(
            cliente=cliente,
            profissional_servico__profissional=profissional
        ).exclude(tratamento__isnull=True).exclude(tratamento__exact='')

        tratamentos = [
            {
                'data': agendamento.data,
                'hora': agendamento.hora,
                'tratamento': agendamento.tratamento,
                'status': agendamento.status,
            }
            for agendamento in agendamentos
        ]
        return Response(tratamentos)



def index(request):
    api_url = f'{settings.API_BASE_URL}/api/profissional-servicos-ativos/?limit=3'
    response = requests.get(api_url)
    servicos_ativos = response.json() if response.status_code == 200 else []
    user = request.user if request.user.is_authenticated else None
    return render(request, 'public/index.html', {'servicos_ativos': servicos_ativos, 'user': user})



def profissionais(request):
    api_url = f'{settings.API_BASE_URL}/api/profissionais/'
    response = requests.get(api_url)
    profissionais = response.json() if response.status_code == 200 else []
    return render(request, 'public/profissionais.html', {'profissionais': profissionais})



def servicos(request):
    api_url = f'{settings.API_BASE_URL}/api/profissional-servicos-ativos/'
    response = requests.get(api_url)
    servicos_ativos = response.json() if response.status_code == 200 else []
    return render(request, 'public/servicos.html', {'servicos_ativos': servicos_ativos})



def agendamentos(request):
    profissional_servicos = ProfissionalServico.objects.filter(status=True)
    return render(request, 'public/agendamentos.html', {'profissional_servicos': profissional_servicos})



def contato(request):
    return render(request, 'public/contato.html')



def agendar(request):
    profissional_servicos = ProfissionalServico.objects.filter(status=True)
    return render(request, 'public/agendar.html', {'profissional_servicos': profissional_servicos})



def obter_token_jwt(username, password):
    """Obtém o token JWT da API externa."""
    auth_url = f'{settings.API_BASE_URL}/api/token/'
    payload = {'username': username, 'password': password}
    try:
        response = requests.post(auth_url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get('access')
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
        return render(request, 'public/login.html')



def logout_view(request):
    logout(request)
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('index')  



def cadastrar(request):
    return render(request, 'public/cadastrar.html')



def meusAgendamentos(request):
    cpf = request.GET.get('cpf')
    search = request.GET.get('search', '')
    api_url = f'{settings.API_BASE_URL}/api/agendamentos/?cpf={cpf}'
    if search:
        api_url += f'&search={search}'
    response = requests.get(api_url)
    agendamentos = response.json() if response.status_code == 200 else []
    return render(request, 'public/meus_agendamentos.html', {'agendamentos': agendamentos})



# views administrativas #
def indexAdm(request):
    if 'jwt_token' in request.session:
        return render(request, 'administracao/profissional_index.html')
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



@login_required
def cadastrarUsuarioAdm(request):
    if not request.user.is_superuser:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})
    if 'jwt_token' in request.session:
        return render(request, 'administracao/profissional_cadastrarUsuario.html', {'jwt_token': request.session['jwt_token']})
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



@login_required
def listarUsuarioAdm(request):
    if not request.user.is_superuser:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})
    if 'jwt_token' in request.session:
        jwt_token = request.session['jwt_token']
        
        search_query= request.GET.get('search', '')
        if search_query:
            api_url = f'{settings.API_BASE_URL}/api/profissionais/?search={search_query}'
        else:
            api_url = f'{settings.API_BASE_URL}/api/profissionais/'

        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(api_url, headers=headers)
        usuarios = response.json() if response.status_code == 200 else []
        return render(request, 'administracao/profissional_listarUsuario.html', {'usuarios': usuarios})
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def editarUsuarioAdm(request, usuario_id):
    if not request.user.is_superuser:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/profissionais/{usuario_id}/'
        response = requests.get(api_url)
        if response.status_code == 200:
            usuario = response.json()
            return render(request, 'administracao/profissional_editarUsuario.html', {'usuario': usuario})
        else:
            return HttpResponse("Usuário não encontrado", status=404)
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def cadastrarServicoAdm(request):
    if 'jwt_token' in request.session:
        return render(request, 'administracao/profissional_cadastrarServico.html')
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def listarServicoAdm(request):
    if 'jwt_token' in request.session:

        search_query= request.GET.get('search', '')
        if search_query:
            api_url = f'{settings.API_BASE_URL}/api/servicos/?search={search_query}'
        else:
            api_url = f'{settings.API_BASE_URL}/api/servicos/'

        response = requests.get(api_url)
        servicos = response.json() if response.status_code == 200 else []
        return render(request, 'administracao/profissional_listarServico.html', {'servicos': servicos})
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def editarServicoAdm(request, servico_id):
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/servicos/{servico_id}/'
        response = requests.get(api_url)
        if response.status_code == 200:
            servico = response.json()
            duracao = servico.get('duracao')

            if duracao:
                servico['duracao_str'] = duracao[:5]
            else:
                servico['duracao_str'] = ''
            
            return render(request, 'administracao/profissional_editarServico.html', {'servico': servico})
        else:
            return HttpResponse("Serviço não encontrado", status=404)
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def atribuirProfissionalAdm(request):
    if not request.user.is_superuser:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/servicos/'
        response = requests.get(api_url)
        servicos = response.json() if response.status_code == 200 else []
        api_url = f'{settings.API_BASE_URL}/api/profissionais/'
        jwt_token = request.session['jwt_token']
        headers = {'Authorization': f'Bearer {jwt_token}'}
        response = requests.get(api_url, headers=headers)
        profissionais = response.json() if response.status_code == 200 else []

        return render(request, 'administracao/profissional_atribuirProfissional.html', {'servicos': servicos, 'profissionais': profissionais})
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def servicosProfissionalAdm(request):
    if not request.user.is_superuser:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})
    if 'jwt_token' in request.session:
        api_url = f'{settings.API_BASE_URL}/api/profissional-servicos-ativos/'
        response = requests.get(api_url)
        servicos = response.json() if response.status_code == 200 else []
        return render(request, 'administracao/profissional_listarServicosProfissionais.html', {'servicos': servicos})
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def cadastrarAgendamentoAdm(request):
    if 'jwt_token' in request.session:
        profissional_servicos = ProfissionalServico.objects.filter(status=True)
        return render(request, 'administracao/profissional_cadastrarAgendamento.html', {'profissional_servicos': profissional_servicos})
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def verAgendamentoAdm(request, agendamento_id):
    if 'jwt_token' in request.session:
        jwt_token = request.session['jwt_token']
        headers = {'Authorization': f'Bearer {jwt_token}'}
        api_url = f'{settings.API_BASE_URL}/api/agendamentos/{agendamento_id}/'
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            agendamento = response.json()
            return render(request, 'administracao/profissional_verAgendamento.html', {'agendamento': agendamento, 'jwt_token': request.session['jwt_token']})
        else:
            return HttpResponse("Agendamento não encontrado", status=404)
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def listarAgendamentoAdm(request):
    if 'jwt_token' in request.session:
        jwt_token = request.session['jwt_token']
        headers = {'Authorization': f'Bearer {jwt_token}'}

        search_query= request.GET.get('search', '')
        if search_query:
            api_url = f'{settings.API_BASE_URL}/api/agendamentos/?search={search_query}'
        else:
            api_url = f'{settings.API_BASE_URL}/api/agendamentos/'

        response = requests.get(api_url, headers=headers)
        agendamentos = response.json() if response.status_code == 200 else []
        return render(request, 'administracao/profissional_listarAgendamento.html', {'agendamentos': agendamentos})   



def cadastrarClienteAdm(request):
    if 'jwt_token' in request.session:
        return render(request, 'administracao/profissional_cadastrarCliente.html')
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def listarClienteAdm(request):
    if 'jwt_token' in request.session:

        search_query= request.GET.get('search', '')
        if search_query:
            api_url = f'{settings.API_BASE_URL}/api/clientes/?search={search_query}'
        else:
            api_url = f'{settings.API_BASE_URL}/api/clientes/'
        
        response = requests.get(api_url)
        clientes = response.json() if response.status_code == 200 else []
        return render(request, 'administracao/profissional_listarCliente.html', {'clientes': clientes})
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def listarPagamentoAdm(request):
    if 'jwt_token' in request.session:
        jwt_token = request.session['jwt_token']
        headers = {'Authorization': f'Bearer {jwt_token}'}
        
        search_query = request.GET.get('search', '')
        if search_query:
            api_url = f'{settings.API_BASE_URL}/api/pagamentos/?search={search_query}'
        else:
            api_url = f'{settings.API_BASE_URL}/api/pagamentos/'

        response = requests.get(api_url, headers=headers)
        pagamentos = response.json() if response.status_code == 200 else []
        return render(request, 'administracao/profissional_listarPagamentos.html', {'pagamentos': pagamentos})
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})



def verProntuarioAdm(request):
    if 'jwt_token' in request.session:
        jwt_token = request.session['jwt_token']
        headers = {'Authorization': f'Bearer {jwt_token}'}
        api_url = f'{settings.API_BASE_URL}/api/prontuarios/'
        response = requests.get(api_url, headers=headers)
        prontuarios = response.json() if response.status_code == 200 else []
        return render(request, 'administracao/profissional_verProntuario.html', {'prontuarios': prontuarios, 'jwt_token': request.session['jwt_token']})
    else:
        return render(request, 'administracao/profissional_index.html', {'error': 'Acesso não autorizado'})

