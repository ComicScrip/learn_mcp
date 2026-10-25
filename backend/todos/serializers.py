from rest_framework import serializers

from .models import Todo


# Utilisé à la fois par l'API REST (views.py) ET par les tools MCP (mcp_server.py) :
# une seule source de vérité pour la validation et le format des données.
class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ["id", "title", "done"]
