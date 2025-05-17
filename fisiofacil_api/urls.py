from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from fisiofacil import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import TokenVerifyView
from fisiofacil.views import DeletarAgendamentoView


router = routers.DefaultRouter()
router.register(r'profissionais', views.ProfissionalViewSet)
router.register(r'servicos', views.ServicoViewSet)
router.register(r'profissional-servicos', views.ProfissionalServicoViewSet)
router.register(r'profissional-servicos-detalhado', views.ProfissionalServicoDetalhadoViewSet, basename='profissional-servicos-detalhado')
router.register(r'profissional-servicos-ativos', views.ProfissionalServicoAtivoViewSet, basename='profissional-servicos-ativos')
router.register(r'agendamentos', views.AgendamentoViewSet)
router.register(r'clientes', views.ClienteViewSet)
router.register(r'prontuarios', views.ProntuarioViewSet),

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/agendamentos/delete/", DeletarAgendamentoView.as_view(), name="agendamento-delete"),  # Mova para cá
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # rota de login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # refresh do token
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('', include('fisiofacil.urls'))
]
