from django.urls import path
from . import views
from .views import get_years, get_departments, get_department_details, user_info

urlpatterns = [
    path('years/', get_years, name='get_years'),
    path('departments/', get_departments, name='get_departments'),
    path('department_details/', get_department_details, name='get_department_details'),
    path('user-info/', user_info.as_view(), name='user_info')
]