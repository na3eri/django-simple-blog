import factory
from apps.users.models import Profile, User
from django.db.models.signals import post_save


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = "test@example.com"
    password = "test"
    is_superuser = True
    is_staff = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw_password = extracted or "test"

        self.set_password(raw_password)

        if create:
            self.save(update_fields=["password"])


@factory.django.mute_signals(post_save)
class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile
        skip_postgeneration_save = True

    user = factory.SubFactory(UserFactory)

    full_name = "test"
    email = factory.Sequence(lambda n: f"profile{n}@example.com")
    role = Profile.ProfileRole.CONTENT_EDITOR
    job_title = "test"
    short_bio = "test"
    x_url = "https://x.com/test"
    facebook_url = "https://facebook.com/test"
    instagram_url = "https://instagram.com/test"
    linkedin_url = "https://linkedin.com/in/test"
