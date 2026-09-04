from django import forms

from .models import Comment
from .models import Post


class CommentForm(forms.ModelForm):
    """Collect comment content without exposing ownership or moderation."""

    body = forms.CharField(
        help_text="Add up to 2,000 characters of relevant discussion.",
        max_length=2000,
        widget=forms.Textarea(
            attrs={
                "aria-describedby": "body-help",
                "class": "form-control",
                "rows": 5,
            }
        ),
    )

    class Meta:
        model = Comment
        fields = ["body"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.is_bound and self["body"].errors:
            self.fields["body"].widget.attrs["aria-describedby"] += (
                " body-error"
            )


class PostForm(forms.ModelForm):
    """Collect the story data a member is permitted to control."""

    class Meta:
        model = Post
        fields = [
            "title",
            "summary",
            "article_url",
            "content",
            "category",
            "status",
        ]
        labels = {
            "article_url": "Original article URL",
            "content": "Why this story matters",
        }
        help_texts = {
            "title": "Use a clear, specific headline.",
            "summary": "Summarise the story in a few sentences.",
            "article_url": "Link to the original reporting or source.",
            "content": "Explain why the story is useful to the community.",
            "category": "Choose the closest topic.",
            "status": "Publish now or keep the story private as a draft.",
        }
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 8}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"
            field.widget.attrs["aria-describedby"] = f"{field_name}-help"
            if self.is_bound and self[field_name].errors:
                field.widget.attrs["aria-describedby"] += (
                    f" {field_name}-error"
                )
