from django.contrib import admin

from .models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('feedback_name', 'feedback_email',
                    'feedback_message', 'created_at',)
    ordering = ('-created_at',)


class Users(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name',
                    'email', 'is_superuser', 'is_staff',)
    search_fields = ('username', 'is_staff',)
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
    tag_list.short_title = 'Список кабинетов'


admin.site.register(Feedback, FeedbackAdmin)
