from django.test import TestCase

from news import forms


class CommentFormAvailabilityTests(TestCase):
    def test_comment_form_is_available(self):
        self.assertTrue(hasattr(forms, "CommentForm"))


class CommentFormValidationTests(TestCase):
    def test_form_limits_and_describes_member_editable_body(self):
        form = forms.CommentForm()

        self.assertEqual(list(form.fields), ["body"])
        self.assertEqual(form.fields["body"].max_length, 2000)
        self.assertEqual(
            form.fields["body"].help_text,
            "Add up to 2,000 characters of relevant discussion.",
        )
        self.assertEqual(form.fields["body"].widget.attrs["rows"], 5)
        self.assertIn("form-control", form.fields["body"].widget.attrs["class"])
        self.assertEqual(
            form.fields["body"].widget.attrs["aria-describedby"],
            "body-help",
        )

    def test_blank_and_excessive_bodies_are_rejected(self):
        blank_form = forms.CommentForm(data={"body": ""})
        long_form = forms.CommentForm(data={"body": "x" * 2001})

        self.assertFalse(blank_form.is_valid())
        self.assertIn("body", blank_form.errors)
        self.assertFalse(long_form.is_valid())
        self.assertIn("body", long_form.errors)
