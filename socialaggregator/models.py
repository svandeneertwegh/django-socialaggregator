"""Models for parrot.gallery"""
from importlib import import_module

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from filer.fields.image import FilerImageField

from taggit.managers import TaggableManager

from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

def validate_image_size(value):
    size = settings.EDSA_RESSOURCE_IMAGE_SIZE
    if size != 0:
        if value.size > size * 1024:
            raise ValidationError(u'The image size (%s) is bigger than %s' % (
                    filesizeformat(value.size), filesizeformat(size * 1024)))


def build_social_plugins_list():
    return [(plugin, datas["NAME"]) for plugin, datas in
            settings.EDSA_PLUGINS.items()]

SOCIAL_PLUGINS = build_social_plugins_list()
SOCIAL_LIST = settings.EDSA_RESSOURCE_BASE_MEDIA_TYPES + SOCIAL_PLUGINS

class Feed(models.Model):
    """Model for group resource by feed"""

    name = models.CharField(_('name'), max_length=250)
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    slug = models.SlugField(_('slug'), unique=True, max_length=100)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('feed')
        verbose_name_plural = _('feeds')


class Aggregator(models.Model):
    """Model for an social feed aggregator"""

    name = models.CharField(_('name'), max_length=250)
    query = models.CharField(_('query'), max_length=250)
    social_plugin = models.CharField(_('social plugin'), max_length=250,
                                     choices=SOCIAL_PLUGINS)
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    slug = models.SlugField(_('slug'), unique=True, max_length=100)
    feeds = models.ManyToManyField(Feed, verbose_name=_('feeds'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('aggregator')
        verbose_name_plural = _('aggregators')


class ResourceQuerySet(models.query.QuerySet):
    def update(self, *args, **kwargs):
        kwargs['update_date'] = timezone.now
        kwargs['updated'] = True
        super(ResourceQuerySet, self).update(*args, **kwargs)


class ResourceManager(models.Manager):
    def get_queryset(self):
        return ResourceQuerySet(self.model, using=self._db)


class ActivatedManager(ResourceManager):
    def get_queryset(self):
        queryset = super(ActivatedManager, self).get_queryset()
        return queryset.filter(activate=True)


class Resource(models.Model):
    """Model representing a resource"""
    # resource main infos
    name = models.CharField(_('name'), max_length=250)
    slug = models.SlugField(_('slug'), unique=True, max_length=100)
    description = models.TextField(_('description'), blank=True)
    short_description = models.TextField(_('short description'), blank=True)
    image = FilerImageField(verbose_name=_('image'), related_name='resource_image', null=True, blank=True, default=None, on_delete=models.CASCADE)
    thumbnail = FilerImageField(verbose_name=_('thumbnail'), related_name='resource_thumbnail', null=True, blank=True, default=None, on_delete=models.CASCADE)
    media_url = models.URLField(_('media url'), blank=True, max_length=500)
    media_url_type = models.CharField(_('media url type'), max_length=100,
                                      blank=True, choices=settings.EDSA_RESSOURCE_MEDIA_TYPE)
    # extra infos
    priority = models.IntegerField(_('display priority'), default=100)
    activate = models.BooleanField(_('activate'), default=False)
    author = models.CharField(_('author'), max_length=250)
    language = models.CharField(_('language'), max_length=2, blank=True)
    feeds = models.ManyToManyField(Feed, verbose_name=_('feeds'), on_delete=models.CASCADE)
    resource_date = models.DateTimeField(_('resource date'))
    tags = TaggableManager(blank=True)

    # social network info
    social_id = models.CharField(_('social_id'), max_length=250, blank=True)
    social_type = models.CharField(_('social plugin'), max_length=250,
                                   choices=SOCIAL_LIST,
                                   default="edsa_article")
    query = models.CharField(_('query'), max_length=250, blank=True)

    # display infos
    favorite = models.BooleanField(_('favorite'), default=False)
    view_size = models.CharField(_('view size'), max_length=100,
                                 choices=settings.EDSA_RESSOURCE_VIEW_SIZES, blank=False,
                                 default='default')
    text_display = models.CharField(_('text display'), max_length=100,
                                    choices=settings.EDSA_RESSOURCE_TEXT_DISPLAY, blank=False,
                                    default='default')
    button_label = models.CharField(_('button label'), max_length=100,
                                    blank=True)
    button_color = models.CharField(_('button color'), max_length=100,
                                    choices=settings.EDSA_RESSOURCE_BUTTON_COLOR, blank=False,
                                    default='black')
    background_color = models.CharField(_('background color'), max_length=250,
                                        blank=True,)
    new_page = models.BooleanField(_('open in new page'), default=False)

    # META DATA
    creation_date = models.DateTimeField(_('creation date'),
                                         default=timezone.now,
                                         editable=False)
    update_date = models.DateTimeField(_('update date'),
                                       default=None)
    updated = models.BooleanField(_('updated'), default=False)

    # Managers
    objects = ResourceManager()
    activated = ActivatedManager()

    def save(self, *args, **kwargs):
        if self.update_date and not self.updated:
            self.updated = True
        self.update_date = timezone.now()
        super(Resource, self).save(*args, **kwargs)

    #@models.permalink
    #def get_absolute_url(self):
        #return ('social_aggregator_resource_detail', (self.slug,))

    def __unicode__(self):
        return self.name

    def get_unified_render(self):
        """
        Get the formatter for resource datas then return the unified data render
        """
        formatter_path = getattr(settings, "RESSOURCE_FORMATTER", "socialaggregator.formatter.ResourceFormatterDefault")
        dot = formatter_path.rindex('.')
        module_name = formatter_path[:dot]
        class_name = formatter_path[dot + 1:] # Assume last item is the class to load
        try:
            _class = getattr(import_module(module_name), class_name)
        except ImportError:
            raise ImportError("'%s' cannot be imported from the setting 'RESSOURCE_FORMATTER'" % formatter_path)
        except AttributeError:
            raise AttributeError("'%s' cannot be imported from the setting 'RESSOURCE_FORMATTER'" % formatter_path)
        else:
            return _class(self).render()

    class Meta:
        ordering = ('-priority', 'name')
        verbose_name = _('resource')
        verbose_name_plural = _('resources')


# Optional plugin for DjangoCMS if installed
try:
    from cms.models import CMSPlugin
except ImportError:
    pass
else:
    class FeedPlugin(CMSPlugin):
        feed = models.ForeignKey('socialaggregator.Feed', related_name='plugins', on_delete=models.CASCADE)

        def __unicode__(self):
            return self.feed.name
