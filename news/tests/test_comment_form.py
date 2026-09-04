from django.test import TestCase

from news import forms


class CommentFormAvailabilityTests(TestCase):
    def test_comment_form_is_available(self):
        self.assertTrue(hasattr(forms, "CommentForm"))
