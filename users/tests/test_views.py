from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.test import TestCase

from users.forms import AuthenticationForm, RegistrationForm
from users.views import home_page, login, signup, confirm


class HomePageTest(TestCase):

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_uses_correct_template(self):
        request = HttpRequest()
        response_home = home_page(request)
        with self.assertTemplateUsed('home.html'):
            render_to_string('home.html')


class SignupTest(TestCase):

    def test_url_resolves_to_signup_page(self):
        found = resolve('/signup')
        self.assertEqual(found.func, signup)

    def test_signup_correct_template(self):
        request = HttpRequest()
        response_signup = signup(request)
        with self.assertTemplateUsed('signup.html'):
            render_to_string('signup.html')

    def test_signup_registration_form(self):
        response = self.client.get('/signup')
        self.assertIsInstance(response.context['form'], RegistrationForm)


class LoginTest(TestCase):

    def test_url_resolves_to_login_page(self):
        found = resolve('/login')
        self.assertEqual(found.func, login)

    def test_login_correct_template(self):
        request = HttpRequest()
        response_login = login(request)
        with self.assertTemplateUsed('login.html'):
            render_to_string('login.html')

    def test_login_authentication_form(self):
        response = self.client.get('/login')
        self.assertIsInstance(response.context['form'], AuthenticationForm)