from . import *  # NOQA

DEBUG = True

ALLOWED_HOSTS = [
    "*",
]

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

SHOW_TOOLBAR_CALLBACK = lambda request: True
