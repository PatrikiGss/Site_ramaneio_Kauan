from django.urls import path

from . import views

app_name = 'cargas'

urlpatterns = [
    path('', views.CargaListView.as_view(), name='lista'),
    path('nova/', views.CargaCreateView.as_view(), name='nova'),
    path('resumo/', views.ResumoView.as_view(), name='resumo'),
    path('lixeira/', views.LixeiraListView.as_view(), name='lixeira'),
    path('<int:pk>/', views.CargaDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.CargaUpdateView.as_view(), name='editar'),
    path('<int:pk>/excluir/', views.CargaDeleteView.as_view(), name='excluir'),
    path('<int:pk>/restaurar/', views.RestaurarCargaView.as_view(), name='restaurar'),
    path('<int:pk>/excluir-definitivo/', views.ExcluirDefinitivoView.as_view(), name='excluir_definitivo'),
]
