from django.contrib import admin
from .models import Client, Account
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "iin", "phone", "email")
    search_fields = ("full_name", "iin")
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("id", "number", "client", "currency", "balance")
    list_filter = ("currency",)
    search_fields = ("number", "client__full_name")
