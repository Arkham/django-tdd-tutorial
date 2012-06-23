from django.test import TestCase
from django.utils import timezone
from polls.models import Poll, Choice
from polls.forms import PollVoteForm

class PollsVoteFormTest(TestCase):

    def test_form_renders_poll_choices_as_radio_inputs(self):
        poll1 = Poll(question='6 times 7', pub_date=timezone.now())
        poll1.save()
        choice1 = Choice(poll=poll1, choice='42', votes=0)
        choice1.save()
        choice2 = Choice(poll=poll1, choice='The ultimate answer', votes=0)
        choice2.save()

        poll2 = Poll(question='time', pub_date=timezone.now())
        poll2.save()
        choice3 = Choice(poll=poll2, choice='PM', votes=0)
        choice3.save()

        form = PollVoteForm(poll=poll1)

        self.assertEquals(form.fields.keys(), ['vote'])

        self.assertEquals(form.fields['vote'].choices, [
            (choice1.id, choice1.choice),
            (choice2.id, choice2.choice),
        ])

        self.assertIn('input type="radio"', form.as_p())
