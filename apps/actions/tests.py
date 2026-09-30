"""Activity deduplication applies to a user, verb and target."""
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from .models import Action
from .utils import create_action


class ActionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='reader')

    def test_first_action_created(self):
        self.assertTrue(create_action(self.user, 'joined'))
        self.assertEqual(Action.objects.count(), 1)

    def test_repeated_action_deduplicated(self):
        create_action(self.user, 'joined')
        self.assertFalse(create_action(self.user, 'joined'))

    def test_different_verb_allowed(self):
        create_action(self.user, 'joined')
        self.assertTrue(create_action(self.user, 'posted'))

    def test_old_action_does_not_suppress_new(self):
        create_action(self.user, 'joined')
        Action.objects.update(created=timezone.now()-timedelta(minutes=2))
        self.assertTrue(create_action(self.user, 'joined'))

    def test_distinct_targets_allowed(self):
        other = get_user_model().objects.create_user(username='other')
        create_action(self.user, 'follows', self.user)
        self.assertTrue(create_action(self.user, 'follows', other))
