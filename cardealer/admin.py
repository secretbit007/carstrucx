from django.contrib import admin

from . import models

admin.site.site_title = "Carstrucx"
admin.site.site_header = "Carstrucx administration"

class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_login', 'username', 'first_name', 'last_name', 'email', 'date_joined', 'is_active')
    
class AdAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'price', 'date_posted')
    search_fields = ('user__username', 'id',)

admin.site.register(models.CustomUser, UserAdmin)
admin.site.register(models.Ad, AdAdmin)
