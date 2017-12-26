"""Admin for parrot.gallery"""
from django.contrib import admin
from django.db import IntegrityError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from socialaggregator.models import Feed
from socialaggregator.models import Aggregator
from socialaggregator.models import Resource


class FeedAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name', 'slug',)
    date_hierarchy = 'creation_date'
    list_filter = ('creation_date',)
    list_display = ('name', 'slug', 'creation_date')

admin.site.register(Feed, FeedAdmin)


class AggregatorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ('name', 'slug', 'query',)
    date_hierarchy = 'creation_date'
    list_filter = ('social_plugin', 'creation_date',)
    list_display = ('name', 'slug', 'query', 'social_plugin', 'creation_date')

admin.site.register(Aggregator, AggregatorAdmin)


def make_activated(modeladmin, request, queryset):
    queryset.update(activate=True)
make_activated.short_description = _("Mark selected resources as activated")


def make_unactivated(modeladmin, request, queryset):
    queryset.update(activate=False)
make_unactivated.short_description = _("Mark selected resources as \
                                        unactivated")


def make_duplicate(modeladmin, request, queryset):
    for data in queryset:
        data.pk = None
        data.activate = False
        slug = data.slug + '_copy_%i'
        name = data.name + ' Copy %i'
        ver = 0
        data.creation_date = timezone.now
        save = False
        while not save:
            try:
                data.slug = slug % ver
                data.name = name % ver
                data.update_date = None
                data.save()
                save = True
            except IntegrityError:
                ver += 1
make_duplicate.short_description = _("Duplicate selected resources")


class ResourceAdmin(admin.ModelAdmin):
    date_hierarchy = 'resource_date'
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'author', 'priority', 'view_size', 'language',
                    'social_type', 'query', 'resource_date', 'activate',
                    'updated')
    list_editable = ('priority','view_size','activate',)
    list_filter = ('social_type', 'feeds', 'view_size', 'language', 'activate', 'updated')
    ordering = ['updated', '-resource_date', 'query']
    exclude = ('updated', 'update_date',)
    actions = [make_activated, make_unactivated, make_duplicate]
    search_fields = ('name', 'author', 'description', 'short_description')
    fieldsets = ((_('Main infos'), {'fields': ('name', 'slug', 'description',
                                               'short_description', 'image',
                                               'thumbnail', 'media_url',
                                               'media_url_type','new_page')}),
                 (_('Extra infos'), {'fields': ('priority', 'activate',
                                                'author', 'language', 'feeds',
                                                'resource_date', 'tags')}),
                 (_('Social network infos'), {'fields': ('social_id',
                                                         'social_type',
                                                         'query')}),
                 (_('Display infos'), {'fields': ('favorite', 'view_size',
                                                  'text_display',
                                                  'button_label',
                                                  'button_color',
                                                  'background_color')}))

admin.site.register(Resource, ResourceAdmin)
