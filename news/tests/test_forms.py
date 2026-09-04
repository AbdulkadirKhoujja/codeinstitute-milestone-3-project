from django.test import TestCase

from news.forms import PostForm


class PostFormTests(TestCase):
    def test_form_exposes_only_member_editable_fields(self):
        form = PostForm()

        self.assertEqual(
            list(form.fields),
            [
                "title",
                "summary",
                "article_url",
                "content",
                "category",
                "status",
            ],
        )
        self.assertNotIn("author", form.fields)
        for field in form.fields.values():
            self.assertIn("form-", field.widget.attrs["class"])

    def test_required_and_url_validation_use_field_errors(self):
        form = PostForm(
            data={
                "title": "",
                "summary": "",
                "article_url": "not-a-url",
                "content": "",
                "category": "",
                "status": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)
        self.assertIn("article_url", form.errors)
        self.assertIn("category", form.errors)
        self.assertIn("status", form.errors)
