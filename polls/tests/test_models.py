from django.test import TestCase
from django.utils import timezone
from polls.models import Poll, Choice

class PollModelTest(TestCase):
    def test_creating_a_new_poll_and_saving_it_to_the_database(self):
        poll = Poll()
        poll.question = "What's up?"
        poll.pub_date = timezone.now()

        poll.save()

        all_polls_in_database = Poll.objects.all()
        self.assertEquals(len(all_polls_in_database), 1)
        only_poll_in_database = all_polls_in_database[0]
        self.assertEquals(only_poll_in_database, poll)

        self.assertEquals(only_poll_in_database.question, "What's up?")
        self.assertEquals(only_poll_in_database.pub_date, poll.pub_date)

    def test_verbose_name_for_pub_date(self):
        for field in Poll._meta.fields:
            if field.name == 'pub_date':
                self.assertEquals(field.verbose_name, 'Date published')

    def test_poll_objects_are_named_after_their_question(self):
        p = Poll()
        p.question = 'How is the cake?'
        self.assertEquals(unicode(p), 'How is the cake?')

    def test_poll_can_tell_you_its_total_number_of_votes(self):
        poll1 = Poll(question='who?', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="me", votes=0)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="you", votes=0)
        choice2.save()

        self.assertEquals(poll1.total_votes(), 0)

        choice1.votes = 100
        choice1.save()
        choice2.votes = 22
        choice2.save()

        self.assertEquals(poll1.total_votes(), 122)

class ChoiceModelTest(TestCase):

    def test_creating_some_choices_for_a_poll(self):
        poll = Poll()
        poll.question = "What's up?"
        poll.pub_date = timezone.now()
        poll.save()

        choice = Choice()
        choice.poll = poll
        choice.choice = "doin' fine.."
        choice.votes = 3
        choice.save()

        poll_choices = poll.choice_set.all()
        self.assertEquals(poll_choices.count(), 1)

        choice_from_db = poll_choices[0]
        self.assertEquals(choice_from_db, choice)
        self.assertEquals(choice_from_db.choice, "doin' fine..")
        self.assertEquals(choice_from_db.votes, 3)

    def test_choice_default(self):
        choice = Choice()
        self.assertEquals(choice.votes, 0)

    def test_choice_can_calculate_its_own_percentage_of_votes(self):
        poll1 = Poll(question='who?', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="me", votes=2)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="you", votes=1)
        choice2.save()

        self.assertEquals(choice1.percentage(), 100 * 2 / 3.0)
        self.assertEquals(choice2.percentage(), 100 * 1 / 3.0)

        choice1.votes = 0
        choice1.save()
        choice2.votes = 0
        choice2.save()

        self.assertEquals(choice1.percentage(), 0)
        self.assertEquals(choice2.percentage(), 0)
