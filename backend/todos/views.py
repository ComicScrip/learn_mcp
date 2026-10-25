from rest_framework import viewsets

from .models import Todo
from .serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.order_by("id")
    serializer_class = TodoSerializer
