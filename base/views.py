from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm, UserForm


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
    return render(request, 'base/login_register.html', context)


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
    return render(request, 'base/login_register.html', {'form': form})


# user profile func
def user_profile(request, pk):
    # get user
    user = User.objects.get(id=pk)
    # get all rooms related to the user
    rooms = user.room_set.all()
    # get all messages related to the user
    room_messages = user.message_set.all()
    # get all topics
    topics = Topic.objects.all
    context = {'user': user, 'rooms': rooms,
               'topics': topics, 'room_messages': room_messages}
    return render(request, 'base/profile.html', context)


# get data from db and display
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

    # get all topics from DB
    # limit to five topics
    topics = Topic.objects.all()[0:5]

    # get number of rooms
    room_count = rooms.count()

    # get all messages from DB
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}

    return render(request, 'base/home.html', context)


# rooms func
def room(request, pk):
    room = Room.objects.get(id=pk)
    # get set of messages related to the specific room in many to one relation
    # get children model through the parent model the child model name should be in lower case
    # newest comment should be first
    room_messages = room.message_set.all()
    # get participant using all() in many to many rekationship
    participants = room.participants.all()
    if request.method == "POST":
        # create message using Message model
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )

        # add user automatically as a participant when he/she comments
        room.participants.add(request.user)
        # fully reload page with a get request
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


# create room func
# user should be login in to access this page else redirect to login
@login_required(login_url="/login")
def create_room(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # get topic value from form
        topic_name = request.POST.get('room_topic')
        # create a new topic if it didn't exist or if similar, get topic from db
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


# update room func
@login_required(login_url="/login")
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)  # prefill form with the fetched room value
    topics = Topic.objects.all()

    # check if the login user is the actual user who created the room
    if request.user != room.host:
        return HttpResponse('You are not allowed to update this room!!!')

    if request.method == "POST":
        # get topic value from form
        topic_name = request.POST.get('room_topic')
        # create a new topic if it didn't exist or if similar, get topic from db
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # replace submited value with the initial room value
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect("home")
    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


# delete room func
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


# delete message func
@login_required(login_url="/login")
def delete_message(request, pk):
    message = Message.objects.get(id=pk)

    # check if the login user is the actual user who created the room
    if request.user != message.user:
        return HttpResponse('Unable to delete this message!!!')

    if request.method == "POST":
        message.delete()  # delete message from DB
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


# update user func
@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html', context)


# topic page func
def topic_pages(request):
    # get query value from the url
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)


# activities page func
def activities_page(request):
    room_messages = Message.objects. all()
    context = {"room_messages": room_messages}
    return render(request, 'base/activity.html', context)
