from django.db.models.deletion import ProtectedError
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .models import Client, Account
from .serializers import ClientSerializer, AccountSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "iin", "phone", "email"]
    ordering_fields = ["id", "full_name", "created_at"]
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({"detail": "Сначала удалите счета этого клиента."}, status=status.HTTP_409_CONFLICT)

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.select_related("client").all()
    serializer_class = AccountSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["number", "client__full_name"]
    ordering_fields = ["id", "balance", "created_at"]
    def get_queryset(self):
        qs = super().get_queryset()
        client = self.request.query_params.get("client")
        currency = self.request.query_params.get("currency")
        if client:
            if not client.isascii() or not client.isdigit() or len(client) > 18:
                raise ValidationError({"client": "Нужен числовой ID клиента."})
            qs = qs.filter(client_id=int(client))
        if currency:
            if currency not in {"KZT", "USD", "EUR"}:
                raise ValidationError({"currency": "Выберите KZT, USD или EUR."})
            qs = qs.filter(currency=currency)
        return qs
