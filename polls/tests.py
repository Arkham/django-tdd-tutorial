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

class HomePageViewTest(TestCase):

    def test_root_url_show_all_polls(self):
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        poll2 = Poll(question='life, the universe and everything', pub_date=timezone.now())
        poll2.save()

        response = self.client.get('/')

        self.assertIn(poll1.question, response.content)
        self.assertIn(poll2.question, response.content)

    def test_root_url_show_links_to_all_polls(self):
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        poll2 = Poll(question='life, the universe and everything', pub_date=timezone.now());
        poll2.save()

        response = self.client.get('/')

        self.assertTemplateUsed(response, 'home.html')

        polls_in_context = response.context['polls']
        self.assertEquals(list(polls_in_context), [poll1, poll2])

        self.assertIn(poll1.question, response.content)
        self.assertIn(poll2.question, response.content)
