from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm


# Create your views here.

# rooms = [
#     {'id': 1, 'name': "Lets learn Python"},
#     {'id': 2, 'name': "Django is nice"},
#     {'id': 3, 'name': "I love React "},
# ]


# login user func
def login_page(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # check if user exist in the db
        try:
            user = User.objects.get(username=username)
        except:
            # throw error message
            messages.error(request, 'Username doesnot exist')

        # authenticate will throw back a user object with the specified crediential if user is valid else throw error
        # make sure credentials are correct
        user = authenticate(request, username=username, password=password)

        # if user exist
        if user is not None:
            # login - creates a session in the db and browser
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Please enter valid username and password")

    context = {'page': page}
    return render(request, 'base/login_registration.html', context)


# logout user
def logout_user(request):
    # delete user session
    logout(request)
    return redirect('home')


# register user
def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # commit= False - get user object once the form is valid
            user = form.save(commit=False)
            # make sure username is lower case
            user.username = user.username.lower()
            user.save()
            # log the user in
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration")
    return render(request, 'base/login_registration.html', {'form': form})


# get data from db
def home(request):
    # get query value from the url
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    # filter room by topic - (__)means going up
    # icontains - ensures that whatever value in topic name atleast contains what is in the query value - case insensitive
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()

    room_count = rooms.count()  # get number of rooms

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}

    return render(request, 'base/home.html', context)


# get requested rooms func
def room(request, pk):
    room = Room.objects.get(id=pk)
    # get set of messages related to the specific room
    # get children model through the parent model the child model name should be in lower case
    # newest comment should be first
    room_messages = room.message_set.all().order_by('-created')
    context = {'room': room, 'room_messages': room_messages}
    return render(request, 'base/room.html', context)


# create room func
# user should be login in to access this page else redirect to login
@login_required(login_url="/login")
def create_room(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


# update func
@login_required(login_url="/login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)  # prefill form with the fetched room value

    # check if the login user is the actual user who created the room
    if request.user != room.host:
        return HttpResponse('You are not allowed to update this room!!!')

    if request.method == "POST":
        # replace submited value with the initial room value
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


# delete func
@login_required(login_url="/login")
def delete_room(request, pk):
    room = Room.objects.get(id=pk)

    # check if the login user is the actual user who created the room
    if request.user != room.host:
        return HttpResponse('You are not allowed to update this room!!!')

    if request.method == "POST":
        room.delete()  # delete room from DB
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})
