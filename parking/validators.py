import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class PasswordComplexityValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("This password must be at least 8 characters long."),
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter (A-Z)."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("This password must contain at least one lowercase letter (a-z)."),
                code='password_no_lower',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("This password must contain at least one number (0-9)."),
                code='password_no_digit',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("This password must contain at least one special character (@, #, $, etc.)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Your password must be at least 8 characters and contain uppercase, lowercase, numbers, and special characters."
        )

def validate_alphabetic(value):
    if not (2 <= len(value) <= 30):
        raise ValidationError(
            _("This field must be between 2 and 30 characters."),
            code='name_length_invalid',
        )
    if not value.isalpha():
        raise ValidationError(
            _("This field must contain only alphabets. No spaces, numbers, or special characters."),
            code='only_alpha',
        )

def validate_social_username(value):
    if not (4 <= len(value) <= 20):
        raise ValidationError(
            _("Username must be between 4 and 20 characters."),
            code='username_length_invalid',
        )
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError(
            _("Usernames can only contain letters, numbers, and underscores. No spaces or periods."),
            code='invalid_social_username',
        )
