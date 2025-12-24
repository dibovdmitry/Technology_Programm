from django.contrib import admin

from .models import Item, ItemTag


class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_title', 'slug', 'invert_num', 'quantity',
                    'valuable', 'available', 'unique', 'invent', 'tag_list', 'user_name',)
    search_fields = ('title', 'tags__name',)
    list_filter = ('valuable', 'unique', 'tags',)

    def short_title(self, obj):
        if len(obj.title) > 100:
            return obj.title[:100] + '...'
        else:
            return obj.title

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())

    short_title.short_title = 'Описание'
    tag_list.short_title = 'Список групп'


class ItemTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'info', 'item_list',)

    def short_title(self, obj):
        if len(obj.title) > 100:
            return obj.title[:100] + '...'
        else:
            return obj.title

    def item_list(self, obj):
        return [Item.objects.get(
            pk=o.get('object_id')
        ) for o in obj.items.values()]

    short_title.short_title = 'Короткое название'
    item_list.short_title = 'Список групп'


admin.site.register(Item, ItemAdmin)
admin.site.register(ItemTag, ItemTagAdmin)
