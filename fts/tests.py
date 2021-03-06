from collections import namedtuple
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

PollInfo = namedtuple('PollInfo', ['question', 'choices'])
POLL1 = PollInfo(
        question="How awesome is TDD?",
        choices=[
            'Very awesome',
            'Quite awesome',
            'Moderately awesome',
        ],
)
POLL2 = PollInfo(
        question="Which food do you prefer?",
        choices=[
            'Beer',
            'Pizza',
            'Banana',
        ],
)

class PollsTest(LiveServerTestCase):
    fixtures = ['admin_user.json']

    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        super(PollsTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(PollsTest, cls).tearDownClass()
        cls.browser.quit()

    def test_can_create_new_poll_via_admin_site(self):
        self.login_as_admin()

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)

        self.create_poll(POLL1)

    def login_as_admin(self):
        self.browser.get(self.live_server_url + '/admin/')

        username_field = self.browser.find_element_by_name('username')
        username_field.send_keys('admin')

        password_field = self.browser.find_element_by_name('password')
        password_field.send_keys('adm1n')
        password_field.send_keys(Keys.RETURN)

    def create_poll(self, poll):
        polls_links = self.browser.find_elements_by_link_text('Polls')
        self.assertEquals(len(polls_links), 2)
        polls_links[1].click()

        self.browser.find_element_by_link_text('Add poll').click()

        question_field = self.browser.find_element_by_name('question')
        question_field.send_keys(poll.question)
        self.browser.find_element_by_link_text('Today').click()
        self.browser.find_element_by_link_text('Now').click()

        for i, choice_text in enumerate(poll.choices):
            choice_field = self.browser.find_element_by_name('choice_set-%d-choice' % i)
            choice_field.send_keys(choice_text)

        save_button = self.browser.find_element_by_css_selector("input[value='Save']")
        save_button.click()

        new_poll_links = self.browser.find_elements_by_link_text(
                poll.question
                )
        self.assertEquals(len(new_poll_links), 1)

        self.browser.get(self.live_server_url + '/admin/')

    def setup_polls_via_admin(self):
        self.login_as_admin()

        for poll_info in [POLL1, POLL2]:
            self.create_poll(poll_info)

    def test_voting_on_a_new_poll(self):
        self.setup_polls_via_admin()

        self.browser.get(self.live_server_url)
        heading = self.browser.find_element_by_tag_name('h1')
        self.assertEquals(heading.text, 'Polls')

        first_poll_title = 'How awesome is TDD?'
        self.browser.find_element_by_link_text(first_poll_title).click()

        main_heading = self.browser.find_element_by_tag_name('h1')
        self.assertEquals(main_heading.text, 'Poll Results')
        sub_heading = self.browser.find_element_by_tag_name('h2')
        self.assertEquals(sub_heading.text, first_poll_title)
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Nobody has voted on this poll yet', body.text)

        choice_inputs = self.browser.find_elements_by_css_selector(
                "input[type='radio']"
        )
        self.assertEquals(len(choice_inputs), 3)

        choice_labels = self.browser.find_elements_by_tag_name('label')
        choices_text = [c.text for c in choice_labels]
        self.assertEquals(choices_text, [
            'Vote:',
            'Very awesome',
            'Quite awesome',
            'Moderately awesome',
        ])

        chosen = self.browser.find_element_by_css_selector(
                "input[value='1']"
        )
        chosen.click()

        self.browser.find_element_by_css_selector(
                "input[type='submit']"
        ).click()

        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('100 %: Very awesome', body_text)

        self.assertIn('1 vote', body_text)
        self.assertNotIn('1 votes', body_text)

        self.browser.find_element_by_css_selector("input[value='1']").click()
        self.browser.find_element_by_css_selector("input[type='submit']").click()

        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('100 %: Very awesome', body_text)
        self.assertIn('2 votes', body_text)

        self.browser.find_element_by_css_selector("input[value='2']").click()
        self.browser.find_element_by_css_selector("input[type='submit']").click()

        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('67 %: Very awesome', body_text)
        self.assertIn('33 %: Quite awesome', body_text)
        self.assertIn('3 votes', body_text)
