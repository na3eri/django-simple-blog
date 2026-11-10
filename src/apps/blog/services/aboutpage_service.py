from apps.cms.models import AboutPageData, AboutPageImage
from apps.users.models import Profile


class AboutPageService:
    def __init__(self):
        self.about_data = AboutPageData
        self.about_image = AboutPageImage

    def build_data(self):
        return self.about_data.objects.first()

    def build_images(self):
        images = list(self.about_image.objects.all())
        return {
            "first_image": images[0] if images else None,
            "second_image": images[1] if len(images) >= 2 else None,
            "third_image": images[2] if len(images) >= 3 else None,
        }

    def build_team(self):
        team_members = list(Profile.objects.all())
        return team_members
