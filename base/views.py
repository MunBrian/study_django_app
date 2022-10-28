from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic
from .forms import RoomForm


# Create your views here.

# rooms = [
#     {'id': 1, 'name': "Lets learn Python"},
#     {'id': 2, 'name': "Django is nice"},
#     {'id': 3, 'name': "I love React "},
# ]

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
    context = {'room': room}
    return render(request, 'base/room.html', context)


# create func
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
def update_room(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)  # prefill form with the fetched room value

    if request.method == "POST":
        # replace submited value with the initial room value
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect("home")
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


# delete func
def delete_room(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == "POST":
        room.delete()  # delete room from DB
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})
