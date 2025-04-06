from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('profissionais/', views.profissionais, name='profissionais'),
    path('servicos/', views.servicos, name='servicos'),
    path('agendamentos/', views.agendamentos, name='agendamentos'),
    path('contato/', views.contato, name='contato')
]