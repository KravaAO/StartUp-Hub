from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile

@admin.register(User)
class CustomUserAdmine(UserAdmin):
    list_sidplay =('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user_username',)