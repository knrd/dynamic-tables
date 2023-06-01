from django.urls import path
from . import views

urlpatterns = [
    path('table', views.TableAPIView.as_view(), name='create_table'),
    path('table/<str:table_name>', views.TableAPIView.as_view(), name='update_table'),
    path('table/<str:table_name>/row', views.TableInsertRowAPIView.as_view(), name='insert_into_table'),
    path('table/<str:table_name>/rows', views.TableFetchRowsAPIView.as_view(), name='fetch_from_table'),
]
