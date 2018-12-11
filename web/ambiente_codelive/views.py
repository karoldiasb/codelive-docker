from django.shortcuts import render
from django.utils import timezone
from .forms import UserForm
from django.shortcuts import redirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
#from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin

from django.contrib.auth.admin import Group
from django.contrib.auth.models import User

from django.views.generic.base import View



from .models import Desafio

def user_register(request):
    if request.user.is_authenticated:
        return redirect('admin:index')

    if request.method == "POST":
        form = UserForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            user.is_staff = True 
            user.set_password(user.password)
            #group = Group.objects.get(name='Estudantes')
            user.save()
            #user.groups.add(group)
            registered = True
            return redirect('home')
    else:
        form = UserForm()    
    return render(request, 'admin/register_user.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect('admin:index')

    if request.method == 'POST':
        form = UserForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')        
        user = authenticate(username=username, password=password)
        
        if user:
            if user.is_active:
                login(request,user)
                return redirect('admin:index')
            else:
                return HttpResponse("Your account is not active.")
        else:
            
            return HttpResponse("Invalid login details supplied.")

    else:
        form = UserForm()
    return render(request, 'admin/logar.html', {'form':form})


def home(request):
    return render(request, 'admin/home.html', {})

def index(request):
    return render(request, 'admin/index.html', {})

def inicio(request):
    return render(request, 'admin/inicio.html', {})

def user_logout(request):
    logout(request)
    return redirect('home')
    # Redirect to a success page.


 