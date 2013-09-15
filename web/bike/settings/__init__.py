import os
from base import *

ENVIRONMENT = os.getenv("DJANGO_ENV")

if ENVIRONMENT == "production":
    from production import *
else:
    from development import *

try:
    from overrides import *
except ImportError:
    pass
