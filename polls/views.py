from django.shortcuts import render
from polls.models import Poll, Choice
from polls.forms import PollVoteForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def home(request):
    context = { 'polls': Poll.objects.all() }
    return render(request, 'home.html', context)

def poll(request, poll_id):
    if request.method == 'POST':
        choice = Choice.objects.get(id=request.POST['vote'])
        choice.votes += 1
        choice.save()
        return HttpResponseRedirect(reverse('polls.views.poll', args=[poll_id,]))

    poll = Poll.objects.get(pk=poll_id)
    form = PollVoteForm(poll=poll)
    return render(request, 'poll.html', { 'poll': poll, 'form': form })
