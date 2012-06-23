from django.test import TestCase
from django.utils import timezone
from polls.models import Poll, Choice
from django.core.urlresolvers import reverse
from polls.forms import PollVoteForm

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

        template_names_used = [t.name for t in response.templates]
        self.assertIn('home.html', template_names_used)

        polls_in_context = response.context['polls']
        self.assertEquals(list(polls_in_context), [poll1, poll2])

        self.assertIn(poll1.question, response.content)
        self.assertIn(poll2.question, response.content)

        poll1_url = reverse('polls.views.poll', args=[poll1.id,])
        self.assertIn(poll1_url, response.content)
        poll2_url = reverse('polls.views.poll', args=[poll2.id,])
        self.assertIn(poll2_url, response.content)

class SinglePollViewTest(TestCase):

    def test_page_shows_poll_title_and_no_votes_message(self):
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        poll2 = Poll(question='life, the universe and everything', pub_date=timezone.now());
        poll2.save()

        response = self.client.get('/poll/%d/' % (poll2.id, ))

        self.assertTemplateUsed(response, 'poll.html')
        self.assertEquals(response.context['poll'], poll2)
        self.assertIn(poll2.question, response.content)
        self.assertIn('Nobody has voted on this poll yet', response.content)

    def test_page_shows_choices_using_form(self):
        poll1 = Poll(question='time', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="PM", votes=0)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="AM", votes=0)
        choice2.save()

        response = self.client.get('/poll/%d/' % (poll1.id, ))

        self.assertTrue(isinstance(response.context['form'], PollVoteForm))

        self.assertIn(choice1.choice, response.content)
        self.assertIn(choice2.choice, response.content)

    def test_view_shows_percentage_of_votes(self):
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="42", votes=1)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="The ultimate answer", votes=2)
        choice2.save()

        response = self.client.get('/poll/%d/' % (poll1.id,))

        self.assertIn('33 %: 42', response.content)
        self.assertIn('67 %: The ultimate answer', response.content)

        self.assertNotIn('Nobody has voted', response.content)

    def test_view_shows_total_votes(self):
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="42", votes=1)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="The ultimate answer", votes=2)
        choice2.save()

        response = self.client.get('/poll/%d/' % (poll1.id,))

        self.assertIn('3 votes', response.content)

        choice2.votes = 0
        choice2.save()

        response = self.client.get('/poll/%d/' % (poll1.id,))

        self.assertIn('1 vote', response.content)
        self.assertNotIn('1 votes', response.content)

    def test_view_can_handle_votes_via_POST(self):
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice="42", votes=1)
        choice1.save()
        choice2 = Choice(poll=poll1, choice="The ultimate answer", votes=3)
        choice2.save()

        post_data = { 'vote': str(choice2.id) }

        poll_url = '/poll/%d/' % (poll1.id,)
        response = self.client.post(poll_url, data=post_data)

        choice_in_db = Choice.objects.get(pk=choice2.id)

        self.assertEquals(choice_in_db.votes, 4)
        self.assertRedirects(response, poll_url)

