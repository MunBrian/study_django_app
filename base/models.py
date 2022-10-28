from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Topic(models.Model):
    # requirement - set topic name to not more than 200 characters
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # if topic is deleted, room is not deleted
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    # the field can be left free
    description = models.TextField(null=True, blank=True)
    # participants =
    # update date/time each time the room is updated
    updated = models.DateTimeField(auto_now=True)
    # add date model once when room is initially created
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # when room is deleted delete children message
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()  # force user to write a message
    # update date/time each time the room is updated
    updated = models.DateTimeField(auto_now=True)
    # add date model once when room is initially created
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.body[0:50]
