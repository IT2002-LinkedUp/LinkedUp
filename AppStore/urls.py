"""AppStore URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

import app.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', app.views.home, name='home'),
    path('', include("django.contrib.auth.urls")),
    path('nav', app.views.nav, name='nav'),
    path('register/', app.views.main_register, name='main_register'),
    path('register/user', app.views.register_user, name='register_user'),
    path('register/company', app.views.register_company, name='register_company'),
    path('user', app.views.user_home, name='user_home'),
    path('user/profile/<str:id>', app.views.user_profile, name='user_profile'),
    path('user/search', app.views.user_search, name = 'user_search'),
    path('user/search/result', app.views.user_search_result, name = 'user_search_result'),
    path('user/search/fail', app.views.search_fail, name = 'user_search_fail'),
    path('user/job/success', app.views.user_job_success, name='user_job_success'),
    path('user/job/delete', app.views.user_job_delete, name='user_job_delete'),
    path('user/job/view/<str:id>', app.views.user_view_job, name='user_view_job'),
    path('company', app.views.company_home, name='company_home'),
    path('company/job/add', app.views.add_job, name='add_job'),
    path('company/job/view/<str:id>', app.views.company_view_job, name='company_view_job'),
    path('company/job/applicants/<str:id>', app.views.view_applicants, name='view_applicants'),
    path('company/job/edit/<str:id>', app.views.edit_job, name='edit_job'),
]
