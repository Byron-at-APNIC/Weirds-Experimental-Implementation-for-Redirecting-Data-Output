#!/usr/bin/env python

import os
import sys

sys.path.append('/usr/local/django')
sys.path.append('/usr/local/django/weirdo')

os.environ['DJANGO_SETTINGS_MODULE'] = 'weirdo.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
