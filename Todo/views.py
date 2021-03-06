from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'Todo/home.html')


def signupuser(request):
    if request.method == 'GET':
        return render(request, 'Todo/signupuser.html', {'form':UserCreationForm()})
    else:
        # whe request.method == "POST"
        # create a new user
        if request.POST['password1'] == request.POST['password2']:
            try:
                # if pass1 & pass2 match, then save user
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()

                # after saving user, login user
                login(request, user)

                # after login send user to his current page
                return redirect('currenttodos')

            except IntegrityError:
                # username is already present
                return render(request, 'Todo/signupuser.html', {'form': UserCreationForm(), 'error': "Username already present. Please choose any other"})
        else:
            # password1 and password 2 are not same
            return render(request, 'Todo/signupuser.html', {'form': UserCreationForm(), 'error': "Passwords didn't match"})


@login_required
def logoutuser(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')

def loginuser(request):
    if request.method == 'GET':
        return render(request, 'Todo/loginuser.html', {'form':AuthenticationForm()})
    else:
        # user submits the details
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            # authenticate returned a None i.e username or password is wrong
            return render(request, "Todo/loginuser.html", {'form':AuthenticationForm(), 'error': "Username or password is wrong"})

        else:
            # username & password matched
            login(request, user)
            return redirect('currenttodos')


@login_required
def createtodo(request):
    if request.method == 'GET':
        return render(request, 'Todo/createtodo.html', {'form':TodoForm()})
    else:
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except:
            return render(request, 'Todo/createtodo.html', {'form':TodoForm(), 'error': 'Bad data entered. Please try again'})


@login_required
def viewtodo(request, id):
    todo = get_object_or_404(Todo, pk=id, user=request.user)
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'Todo/viewtodo.html',{'todo': todo, 'form': form})
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except:
            return render(request, 'Todo/viewtodo.html', {'todo': todo, 'form':form, 'error': 'Bad data entered. Please try again'})


@login_required
def completetodo(request, id):
    todo = get_object_or_404(Todo, pk=id, user=request.user)
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')


@login_required
def deletetodo(request, id):
    todo = get_object_or_404(Todo, pk=id, user=request.user)
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')


@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'Todo/currenttodos.html', {'todos': todos})


@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'Todo/completedtodos.html', {'todos': todos})
