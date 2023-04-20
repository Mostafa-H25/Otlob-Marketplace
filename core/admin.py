from django.contrib import admin

from .models import Category, Subcategory, Brand, Item, OrderItem, Order, Coupon


def delivering(modeladmin, request, queryset):
    queryset.update(shipped=True)


delivering.short_description = 'Ship Order'


def delivered(modeladmin, request, queryset):
    queryset.update(received=True)


delivered.short_description = 'Update Order to Received'


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('name',)}


class SubcategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('name',)}


class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('name',)}


class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('name', 'brand', 'seller')}


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'shipped', 'received']
    list_filter = ['ordered', 'shipped', 'received']
    search_fields = ['uuid', 'user__username']

    actions = [delivering, delivered]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Coupon)
