from base import *

DEBUG = True

INSTALLED_APPS = tuple(list(INSTALLED_APPS) + ['debug_toolbar'])
MIDDLEWARE_CLASSES = tuple(list(MIDDLEWARE_CLASSES) + ['debug_toolbar.middleware.DebugToolbarMiddleware'])

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': True,
    'SHOW_TOOLBAR_CALLBACK': lambda req: True,
}
