from django.contrib import admin

from .models import Profile, Address, Conversation, Message


class AddressAdmin(admin.ModelAdmin):
    list_display = ['address_type', 'default', 'city', 'country', 'user']
    list_filter = ['address_type', 'city', 'country']
    search_fields = ['country', 'city', 'zipcode', 'user']


admin.site.register(Profile)
admin.site.register(Address, AddressAdmin)
admin.site.register(Conversation)
admin.site.register(Message)
