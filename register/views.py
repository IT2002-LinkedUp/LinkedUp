from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def main_register(request):
    return render(request, 'registration/register.html')

def register_user(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            group = Group.objects.get(name='user')
            user.groups.add(group)
            messages.success(request, 'Account was created for ' + username)
            # print(request.POST)
            # POST request: create in users table
            return redirect("/login")
        else:
            messages.error(request, 'Invalid form submission')
    else:
        form = UserCreationForm()
    return render(request, 'registration/registeruser.html', {"form": form})

def register_company(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            company = form.save()
            company_username = form.cleaned_data.get('username')
            group = Group.objects.get(name='company')
            company.groups.add(group)
            messages.success(request, 'Account was created for ' + company_username)
            return redirect("/login")
        else:
            messages.error(request, 'Invalid form submission')
    else:
        form = UserCreationForm()
    # POST request: create in company table
    return render(request, 'registration/registercompany.html', {"form": form})