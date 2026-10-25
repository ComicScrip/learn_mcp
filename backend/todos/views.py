from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Todo
from .serializers import TodoSerializer
from .stats import todo_stats


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.order_by("id")
    serializer_class = TodoSerializer

    # GET /api/todos/stats/?period=month&offset=-1
    @action(detail=False)
    def stats(self, request):
        period = "month" if request.query_params.get("period") == "month" else "week"
        offset = int(request.query_params.get("offset", 0))
        return Response(todo_stats(period, offset))
