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
    
    path('adm/', views.indexAdm, name='indexAdm'),
    path('agendamentos/', views.agendamentosAdm, name='agendamentosAdm')
]