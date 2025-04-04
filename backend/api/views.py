from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import DeptYear
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
import logging
import os
from datetime import datetime
from django.conf import settings

# creating users
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

# for populating year selection dropdown
def get_years(request):
    try:
        years = DeptYear.objects.values_list('year', flat=True).distinct().order_by('year')
        return JsonResponse({"years": list(years)})
    except Exception as e:
        return JsonResponse({"error returning years for dropdown": str(e)}, status=500)

# for populating department selection dropdown
def get_departments(request):
    try:
        year = request.GET.get("year")

        if not year:
            return JsonResponse({"error": "Year parameter is required"}, status=400)

        departments = list(DeptYear.objects.filter(year=year).values_list('dept_name', flat=True).distinct())

        return JsonResponse({"departments": departments})
    except Exception as e:
        return JsonResponse({"error": f"Error returning departments for dropdown: {str(e)}"}, status=500)

# for getting selected department details based on dropdown menu choices
def get_department_details(request):
    try:
        year = request.GET.get("year")
        dept_name = request.GET.get("dept_name")

        if not year or not dept_name:
            return JsonResponse({"error": "Both year and department parameters are required"}, status=400)

        department = DeptYear.objects.filter(year=year, dept_name=dept_name).first()

        if not department:
            return JsonResponse({"error": "Department not found"}, status=404)

        department_data = {
            "dept_name": department.dept_name,
            "year": department.year,
            "density": department.density,
            "keywords": department.keywords,
            "similar_depts": department.similar_depts,
            "graph_representation": department.graph_representation,
            "max_indegrees": department.max_indegrees,
            "max_outdegrees": department.max_outdegrees,
        }

        return JsonResponse({"department": department_data})

    except Exception as e:
        return JsonResponse({"error": f"Error retrieving department details: {str(e)}"}, status=500)


# for getting user info - used to prevent "non-admin (non-staff in django terms)" users cannot register new users
class user_info(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'is_staff': user.is_staff,
        })

# for writing to log file - Django's logger didn't want to play nice
def log_to_file(message):
    log_directory = os.path.join(settings.BASE_DIR, 'logs')
    os.makedirs(log_directory, exist_ok=True)
    log_file_path = os.path.join(log_directory, 'login_attempts.log')
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"{message}\n")

# overrides TokenObtainPairView view to implement logging for login attempts
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            username = request.data.get('username', 'unknown')
            ip = request.META.get('REMOTE_ADDR')
            message = f"[{time}] Successful login attempt for user: \"{username}\" from {ip}"
            log_to_file(message)
        except Exception as e:
            response = Response({"error": "Invalid credentials or account not active"}, status=400)
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            username = request.data.get('username', 'unknown')
            ip = request.META.get('REMOTE_ADDR')
            message = f"[{time}] Failed login attempt for user: \"{username}\" from {ip}"
            log_to_file(message)

        return response





