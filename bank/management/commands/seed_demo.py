from django.core.management.base import BaseCommand
from django.db import transaction
from bank.models import Client, Account
class Command(BaseCommand):
    help = "Добавить вымышленные учебные данные, без создания пользователя/пароля"
    @transaction.atomic
    def handle(self, *args, **kwargs):
        for i, name in enumerate(["Тестовый Клиент Один", "Тестовый Клиент Два", "Тестовый Клиент Три"], 1):
            client, _ = Client.objects.get_or_create(iin=f"{i:012d}", defaults={"full_name": name, "email": f"client{i}@example.com"})
            Account.objects.get_or_create(number=f"KZ{i:018d}", defaults={"client": client, "currency": "KZT", "balance": str(i * 10000)})
        self.stdout.write(self.style.SUCCESS("Добавлены 3 учебных клиента и счёта."))
