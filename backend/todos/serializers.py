from rest_framework import serializers

from .models import Todo


# Utilisé à la fois par l'API REST (views.py) ET par les tools MCP (mcp_server.py) :
# une seule source de vérité pour la validation et le format des données.
class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ["id", "title", "done", "created_at", "done_at"]
        read_only_fields = ["created_at", "done_at"]

    def update(self, instance, validated_data):
        # Via l'API REST aussi, cocher une tâche doit renseigner done_at.
        if "done" in validated_data:
            instance.set_done(validated_data.pop("done"))
        return super().update(instance, validated_data)
