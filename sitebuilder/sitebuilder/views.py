from __future__ import unicode_literals

import json
import os
from django.conf import settings
from django.http import Http404
from django.template import Template
from django.template import Context
from django.template.loader_tags import BlockNode
from django.shortcuts import render
from django.utils._os import safe_join


def get_page_or_404(name):
    """ return page content as a django template or raise 404 error."""
    try:
        file_path = safe_join(settings.SITE_PAGES_DIRECTORY, name)
    except ValueError:
        raise Http404('Page not found')
    else:
        if not os.path.exists(file_path):
            raise Http404('Page not found')

    with open(file_path, 'r') as f:
        page = Template(f.read())

    meta = None
    for i, node in enumerate(list(page.nodelist)):
        if isinstance(node, BlockNode) and node.name == 'contact':
            meta = page.nodelist.pop(i)
            break

    page._meta = meta
    return page


def page(request, slug='index'):
    """ render the requested page if found."""
    file_name = '{}.html'.format(slug)
    page = get_page_or_404(file_name)
    context = {
        'slug': slug,
        'page': page,
    }

    if page._meta is not None:
        meta = page._meta.render(Context())
        extra_context = json.loads(meta)
        context.update(extra_context)

    return render(request, 'page.html', context)