from django.contrib.auth.mixins import UserPassesTestMixin


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин проверки прав доступа пользователя."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user
