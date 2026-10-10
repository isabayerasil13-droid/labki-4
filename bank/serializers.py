from rest_framework import serializers
from .models import Client, Account

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ["id", "full_name", "iin", "phone", "email", "created_at"]
        read_only_fields = ["id", "created_at"]

class AccountSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.full_name", read_only=True)
    class Meta:
        model = Account
        fields = ["id", "client", "client_name", "number", "currency", "balance", "created_at"]
        read_only_fields = ["id", "created_at"]
