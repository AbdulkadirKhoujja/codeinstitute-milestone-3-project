from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm


class LoginForm(AuthenticationForm):
    """Present the standard Django login fields with accessible attributes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

        self.fields["username"].widget.attrs["autocomplete"] = "username"
        self.fields["password"].widget.attrs["autocomplete"] = "current-password"


class RegistrationForm(UserCreationForm):
    """Collect only the credentials needed to join ByteBoard."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["aria-describedby"] = f"{field_name}-help"

        self.fields["username"].widget.attrs["autocomplete"] = "username"
        self.fields["password1"].widget.attrs["autocomplete"] = "new-password"
        self.fields["password2"].widget.attrs["autocomplete"] = "new-password"

        if self.is_bound:
            for field_name, field in self.fields.items():
                if self[field_name].errors:
                    field.widget.attrs["aria-describedby"] += (
                        f" {field_name}-error"
                    )
