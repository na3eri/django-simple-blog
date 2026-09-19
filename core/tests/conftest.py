from pytest_factoryboy import register
from tests.factories import ProfileFactory, UserFactory

register(UserFactory)
register(ProfileFactory)
