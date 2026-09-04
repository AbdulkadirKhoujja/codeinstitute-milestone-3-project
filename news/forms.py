from django import forms

from .models import Post


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
