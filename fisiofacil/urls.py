from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('servicos/', views.servicos, name='servicos'),
    path('contato/', views.contato, name='contato'),
    path('profissionais/', views.profissionais, name='profissionais'),
    path('login/', views.login_view, name='login'),
    path('agendar/', views.agendar, name='agendar'),
    path('logout/', views.logout_view, name='logout'),
    path('cadastrar/', views.cadastrar, name='cadastrar'),
    path('meus-agendamentos/', views.meusAgendamentos, name='meusAgendamentos'),
    path('meus-agendamentos/?cpf=<str:cpf>', views.meusAgendamentos, name='meusAgendamentos'),
    
    path('adm/', views.indexAdm, name='indexAdm'),
    path('adm/cadastrar-usuario/', views.cadastrarUsuarioAdm, name='cadastrarUsuarioAdm'),
    path('adm/listar-usuario/', views.listarUsuarioAdm, name='listarUsuarioAdm'),
    path('adm/editar-usuario/<int:usuario_id>', views.editarUsuarioAdm, name='editarUsuarioAdm'),
    path('adm/cadastrar-servico/', views.cadastrarServicoAdm, name='cadastrarServicoAdm'),
    path('adm/listar-servico/', views.listarServicoAdm, name='listarServicoAdm'),
    path('adm/editar-servico/<int:servico_id>/', views.editarServicoAdm, name='editarServicoAdm'),
    path('adm/atribuir-profissional/', views.atribuirProfissionalAdm, name='atribuirProfissionalAdm'),
    path('adm/servicos-profissionais/', views.servicosProfissionalAdm, name='servicosProfissionalAdm'),
    path('adm/cadastrar-agendamento/', views.cadastrarAgendamentoAdm, name='cadastrarAgendamentoAdm'),
    path('adm/listar-agendamento/', views.listarAgendamentoAdm, name='listarAgendamentoAdm'),
]