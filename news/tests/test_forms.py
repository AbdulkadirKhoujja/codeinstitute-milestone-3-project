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

    def test_form_provides_task_specific_labels_and_guidance(self):
        form = PostForm()

        self.assertEqual(form.fields["article_url"].label, "Original article URL")
        self.assertEqual(form.fields["content"].label, "Why this story matters")
        expected_guidance = {
            "title": "Use a clear, specific headline.",
            "summary": "Summarise the story in a few sentences.",
            "article_url": "Link to the original reporting or source.",
            "content": "Explain why the story is useful to the community.",
            "category": "Choose the closest topic.",
            "status": "Publish now or keep the story private as a draft.",
        }
        for field_name, guidance in expected_guidance.items():
            self.assertEqual(form.fields[field_name].help_text, guidance)
