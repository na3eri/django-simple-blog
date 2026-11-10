from apps.blog.models import Category, Article
from apps.cms.services.site_setting_service import SiteSettingService
from apps.users.models import Profile


def global_context(request):
    service = SiteSettingService()

    categories = Category.objects.all()[:4]
    team_members = Profile.objects.all()[:4]

    return {
        "site_name": service.get_or_create_setting(
            key="site_name", value="naseri.dev-simple_blog"
        )[0].value,
        "site_x_url": service.get_or_create_setting(
            key="site_instagram_url", value="https://instagram.com/naseri.dev"
        )[0].value,
        "site_facebook_url": service.get_or_create_setting(
            key="site_instagram_url", value="https://instagram.com/naseri.dev"
        )[0].value,
        "site_instagram_url": service.get_or_create_setting(
            key="site_instagram_url", value="https://instagram.com/naseri.dev"
        )[0].value,
        "site_linkedin_url": service.get_or_create_setting(
            key="site_instagram_url", value="https://instagram.com/naseri.dev"
        )[0].value,
        "address": service.get_or_create_setting(
            key="address", value="A108 Adam Street"
        )[0].value,
        "phone_number": service.get_or_create_setting(
            key="phone_number", value="+111111111111"
        )[0].value,
        "email": service.get_or_create_setting(key="email", value="admin@example.com")[
            0
        ].value,
        "navbar_items": {
            "categories": categories,
            "team_members": team_members,
        },
        "footer_items": {
            "categories": categories,
            "team_members": team_members,
            "most_popular": Article.objects.published().popular()[:4],
            "last_articles": Article.objects.published()[:3],
        },
    }
