# Paste this ENTIRE file into your PythonAnywhere WSGI file:
# /var/www/aryansingla_pythonanywhere_com_wsgi.py
#
# Replace the whole file content with this, then Save and Reload the web app.

import os
import sys

# Your project folder (where manage.py and hrms_lite/ live)
project_home = '/home/aryansingla/hrms-lite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['DJANGO_SETTINGS_MODULE'] = 'hrms_lite.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
