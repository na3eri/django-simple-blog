from django.db.models import Q

from apps.blog.models import Message


class ProfileMessagesService:
    def __init__(self, user, status, search_query=None):
        self.message_model = Message
        self.user = user
        self.user_profile = user.profile
        self.status = self._set_profile(status)
        self.search_query = self._set_query_set(search_query)

    @staticmethod
    def _set_profile(status: str) -> str:
        if not (status and isinstance(status, str)):
            return None

        if status.lower() not in ("inbox", "sent", "archived", "read"):
            return None

        return status.lower()

    @staticmethod
    def _set_query_set(search_query):
        if not (search_query and isinstance(search_query, str)):
            return None

        return search_query

    def get_messages(self):
        base_queryset = self.message_model.objects.active().filter(
            user_profile=self.user_profile,
        )

        if self.user.is_superuser:
            base_queryset = self.message_model.objects.active().filter(
                Q(user_profile=self.user_profile) | Q(user_profile=None)
            )

        if self.status == "sent":
            messages = base_queryset.filter(parent__isnull=True)

        if self.status == "archived":
            messages = base_queryset.filter(is_archived=True)

        if self.status == "read":
            messages = base_queryset.filter(is_read=True)

        if self.status == "inbox":
            messages = base_queryset

        if self.search_query is not None:
            messages = messages.filter(
                Q(name__icontains=self.search_query)
                | Q(email__icontains=self.search_query)
                | Q(subject__icontains=self.search_query)
                | Q(body__icontains=self.search_query)
            )

        return messages

    def total_unread_messages(self):
        filters = Q(
            user_profile=self.user_profile,
            is_read=False,
            is_deleted=False,
        )

        if self.user.is_superuser:
            filters = Q(
                user_profile=self.user_profile,
                is_read=False,
                is_deleted=False,
            ) | Q(
                user_profile=None,
                is_read=False,
                is_deleted=False,
            )

        count = self.message_model.objects.filter(filters).count()

        return count

    def get_context(self, view_context):
        return {
            "profile_instance": self.user_profile,
            "status": self.status,
            "total_unread_messages": self.total_unread_messages(),
            "custom_range": view_context["paginator"].get_elided_page_range(
                number=view_context["page_obj"].number,
                on_each_side=2,
                on_ends=1,
            ),
        }

    def set_all_messages_as_read(self):
        filters = Q(
            user_profile=self.user_profile,
            is_read=False,
            is_deleted=False,
        )

        if self.user.is_superuser:
            filters = Q(
                user_profile=self.user_profile,
                is_read=False,
                is_deleted=False,
            ) | Q(
                user_profile=None,
                is_read=False,
                is_deleted=False,
            )

        self.message_model.objects.filter(filters).update(
            is_read=True,
        )

        return True

    def delete_message(self, message_id):
        if self.user.is_superuser:
            filters = Q(
                user_profile=self.user_profile,
                is_deleted=False,
            ) | Q(user_profile=None, is_deleted=False)
        else:
            filters = Q(
                user_profile=self.user_profile,
                is_deleted=False,
            )

        try:
            message_obj = self.message_model.objects.filter(filters).get(
                Q(id=message_id)
            )
        except self.message_model.DoesNotExist:
            return False

        message_obj.is_deleted = True
        message_obj.save(update_fields=["is_deleted"])

        return True

    def archive_message(self, message_id):
        if self.user.is_superuser:
            filters = Q(
                user_profile=self.user_profile,
                is_deleted=False,
                is_archived=False,
            ) | Q(
                user_profile=None,
                is_deleted=False,
                is_archived=False,
            )
        else:
            filters = Q(
                user_profile=self.user_profile,
                is_deleted=False,
                is_archived=False,
            )

        try:
            message_obj = self.message_model.objects.filter(filters).get(
                Q(id=message_id)
            )
        except self.message_model.DoesNotExist:
            return False

        message_obj.is_archived = True
        message_obj.save(update_fields=["is_archived"])

        return True

    def reply_message(self, message_id, reply_body):
        try:
            message_obj = self.message_model.objects.filter(
                Q(
                    user_profile=self.user_profile,
                    is_deleted=False,
                )
            ).get(Q(id=message_id))
        except self.message_model.DoesNotExist:
            return False

        self.message_model.objects.create(
            user_profile=self.user_profile,
            parent=message_obj,
            name=self.user_profile.full_name,
            email=self.user_profile.email,
            subject=f"Reply to your message: {message_obj.subject}",
            body=reply_body,
        )

        return True
