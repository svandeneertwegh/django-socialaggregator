# -*- coding: utf-8 -*-
"""
Template tags
"""
from django.conf import settings
from django import template
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from socialaggregator.models import Resource

register = template.Library()

@register.simple_tag(takes_context=True)
def resource_by_feed(context, slug, template_name=settings.EDSA_TAG_TEMPLATE):
    """
    Display resources from specified feed without any pagination
    
    * ``slug`` argument is a String containing the slug feed
    * ``template_name`` is a String containing the template path to use, default to ``settings.EDSA_TAG_TEMPLATE``
    """
    resources = Resource.activated.filter(feeds__slug=slug).order_by('priority', '-resource_date')

    ctx = {
        'resources': resources,
    }

    tmpl = render_to_string(template_name, ctx)

    return mark_safe(tmpl)
