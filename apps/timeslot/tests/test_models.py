import test_utils

from datetime import datetime

from challenges.models import (Submission, Phase, Challenge, Category,
                               Project)
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from timeslot.models import TimeSlot, Release
from timeslot.tests.fixtures import (create_project, create_challenge,
                                     create_phase, create_user,
                                     create_category, create_submission)



class TimeSlotModelTest(test_utils.TestCase):

    def setUp(self):
        """Actions to be performed at the beginning of each test"""
        # setup ignite challenge
        self.project = create_project(settings.IGNITE_PROJECT_SLUG)
        self.challenge = create_challenge(settings.IGNITE_CHALLENGE_SLUG,
                                          self.project)
        now = datetime.utcnow()
        past = now - relativedelta(days=30)
        future = now + relativedelta(days=30)
        # create the Ideation and Development phases
        idea_data = {'order': 1, 'start_date': past, 'end_date': now}
        self.ideation = create_phase(settings.IGNITE_IDEATION_NAME,
                                     self.challenge, idea_data)
        dev_data = {'order': 2, 'start_date': now, 'end_date': future}
        self.development = create_phase(settings.IGNITE_DEVELOPMENT_NAME,
                                        self.challenge, dev_data)

    def tearDown(self):
        """Actions to be performed at the end of each test"""
        for model in [Submission, Phase, Challenge, Category, Project,
                      TimeSlot, User]:
            model.objects.all().delete()

    def create_release(self, name, is_current, extra_data=None):
        """Helper to create releases"""
        data = {'name': name,
                'is_current': True}
        if extra_data:
            data.update(extra_data)
        return Release.objects.create(**data)

    def test_release_creation(self):
        """Create a Release with the minimum data"""
        data = {'name': 'Release', 'is_current': True,}
        release = Release.objects_create(**data)

    def test_current_release_creation(self):
        """Test the current release mechanics"""
        release = self.create_release('Release', True)
        self.assertEqual(release, Release.objects.get_current())
        self.assertEqual(Release.objects.filter(is_current=True).count(), 1)
        # add an extra current release
        new_release = self.create_release('New release', True)
        self.assertEqual(new_release, Release.objects.get_current())
        self.assertEqual(Release.objects.filter(is_current=True).count(), 1)

    def create_simple_timeslot(self):
        """Create a ``TimeSlot`` with the less possible data"""
        release = Release.objects.create(name='Release', is_current=True)
        data = {
            'start_date': datetime.utcnow(),
            'end_date': datetime.utcnow() + relativedelta(hours=1),
            'release': release,
            }
        timeslot = TimeSlot.objects.create(**data)
        assert timeslot.id, "TimeSlot not created"
