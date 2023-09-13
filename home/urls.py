from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
  path(''       , views.index,  name='index'),
  path('predict-loan', views.loan_predict, name='loan_predict'),
  path('predict-request',views.predict_request, name='predict-request'),
  path('tables/', views.tables, name='tables'),
]
