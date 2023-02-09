from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Room,Topic, Message
from .forms import RoomForm,UserForm
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
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An Error occoured during registeration")

    context = {'page': page,'form': form}
    return render(request, 'base/login_register.html', context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    conversations =  Message.objects.filter(Q(room__topic__name__icontains=q))
    room_count = rooms.count()
    topics = Topic.objects.all()
    context =  {'rooms': rooms, 'topics': topics, 'room_count':room_count, 'conversations': conversations}
    return render(request, 'base/home.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    conversations = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'topics':topics,'rooms':rooms, 'conversations':conversations}
    return render(request, 'base/profile.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    conversations = room.message_set.all()
    members = room.members.all()
    member_count= members.count()
    if request.method == 'POST':
        convo = Message.objects.create(
            user=request.user,
            room = room,
            body = request.POST.get('body')
        )
        room.members.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {'room': room, 'conversations': conversations, 'member_count':member_count, 'members': members}    
    
    return render(request, 'base/room.html', context)

@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     room.host = request.user
        #     form.save()
        return redirect('home')
    context = {"form": form, 'topics': topics}
    return render(request, 'base/room_form.html', context)
    
    
    
@login_required(login_url='/login')
def updateView(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('User is not allowed here')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name = topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()

        # form = RoomForm(request.POST, instance=room )
        # if form.is_valid():
        #     form.save()
        return redirect('room', pk=room.id)

    context = {'form': form, 'topics': topics, 'room':room}
    return render(request, "base/room_form.html", context)    



@login_required(login_url='/login')
def deleteView(request,pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj': room}
    return render(request, 'base/delete.html', context)


@login_required(login_url='/login')
def deleteMessageView(request,pk):
    conversation = Message.objects.get(id=pk)
    if request.user == conversation.user and request.method == 'POST':
        conversation.delete()
        return redirect('home')
    context = {'obj': conversation}
    return render(request, 'base/delete.html', context)
 
 
@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk = user.id)
    
    context = {'form': form }
    return render(request, 'base/update-user.html', context)