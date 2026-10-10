from apps.cms.models import SiteSetting


class SiteSettingService:
    def __init__(self):
        self.model = SiteSetting

    def get_settings(self):
        return self.model.objects.all()

    def get_or_create_setting(
        self,
        key,
        value="EMPTY VALUE",
        setting_type="text",
        description="",
        detail="",
    ):
        return self.model.objects.get_or_create(
            key=key,
            defaults={
                "value": value,
                "type": setting_type,
                "description": description,
                "detail": detail,
            },
        )
