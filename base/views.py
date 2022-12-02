from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Room,Topic
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib. auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

# Create your views here.


# rooms = [
#     {'id':1, 'name':'Lets learn python'},
#     {'id':2, 'name':'Lets learn javascript'},
#     {'id':3, 'name':'Lets learn Dart'},
#     {'id':4, 'name':'Lets learn R'},
# ]


@csrf_protect
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')
            
        user = authenticate(request, username=username, password=password)
    
        
    
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password is invalid')

        
    context = {'page': page} 
    return render(request,'base/login_register.html', context)

def LogOut(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'
    form = UserCreationForm(request.POST)
    context ={'page': page,'form': form}
    if request.method == 'POST':
        form = UserCreationForm()
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An Error occoured during registeration")
            
    return render(request, 'base/login_register.html', context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    room_count = rooms.count()
    topics = Topic.objects.all()
    context =  {'rooms': rooms, 'topics': topics, 'room_count':room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    context = {'room': room}    
    
    return render(request, 'base/room.html', context)

@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {"form": form}
    return render(request, 'base/room_form.html', context)
    
    
    
@login_required(login_url='/login')
def updateView(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse('User is not allowed here')
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room )
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, "base/room_form.html", context)    



@login_required(login_url='/login')
def deleteView(request,pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj': room}
    return render(request, 'base/delete.html', context)
 