from decimal import Decimal
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator

class Client(models.Model):
    full_name = models.CharField("ФИО", max_length=150)
    iin = models.CharField("ИИН", max_length=12, unique=True, validators=[RegexValidator(r"^[0-9]{12}$", "ИИН должен содержать 12 цифр.")])
    phone = models.CharField("Телефон", max_length=20, blank=True)
    email = models.EmailField("Email", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["id"]
    def __str__(self):
        return self.full_name

class Account(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="accounts", verbose_name="Клиент")
    number = models.CharField("Номер счёта", max_length=20, unique=True, validators=[RegexValidator(r"^KZ[0-9A-Z]{18}$", "Формат: KZ и 18 латинских букв/цифр.")])
    currency = models.CharField("Валюта", max_length=3, choices=[("KZT", "KZT"), ("USD", "USD"), ("EUR", "EUR")], default="KZT")
    balance = models.DecimalField("Баланс", max_digits=16, decimal_places=2, default=0, validators=[MinValueValidator(Decimal("0"))])
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["id"]
        constraints = [models.CheckConstraint(condition=models.Q(balance__gte=0), name="non_negative_balance")]
    def __str__(self):
        return self.number
