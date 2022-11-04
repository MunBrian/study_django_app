from rest_framework.decorators import api_view
from rest_framework.response import Response
from base.models import Room
from .serializers import RoomSerializer
from base.api import serializers


# allow method that is used to access this view
@api_view(['GET'])
def get_routes(request):
    routes = [
        'GET /api'
        'GET /api/rooms',
        'GET /api/rooms/:id'
    ]
    return Response(routes)


@api_view(['GET'])
def get_rooms(request):
    rooms = Room.objects.all()
    # many=True - serialize a query set/many objects
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)
