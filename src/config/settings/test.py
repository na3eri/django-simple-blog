from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


INSTALLED_APPS += [
    "tests.cms.cms_test_app.apps.TestAppConfig",
]
