from django.urls import path
from . import views

urlpatterns = [
    path('table', views.TableAPIView.as_view(), name='create_table'),
    path('table/<str:table_name>', views.TableAPIView.as_view(), name='update_table'),
    path('test_schema/', views.test_view_schema_create),
    path('test_fields/', views.test_view_fields_create),
]
