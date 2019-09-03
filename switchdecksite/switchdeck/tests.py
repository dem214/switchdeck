from datetime import timedelta
import os
import re

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from django.core import mail

from .models import Game, GameList, Profile, Place, Comment


class ModelsTest(TestCase):
    def setUp(self):
        self.tloz = Game.objects.create(name='TLOZ')
        self.smo = Game.objects.create(name='SMO')
        self.smk = Game.objects.create(name='SMK')
        self.only_one_to_sell_and_buy = Game.objects.create(name='SSBU')

        minsk = Place.objects.create(name='minsk')

        self.mary = Profile.create_profile('mary', 'mary@example.com',
            'passwordmary', place=minsk)
        self.john = Profile.create_profile('john', 'john@example.com',
            'passwordjohn', place=minsk)

        GameList.objects.create(game=self.tloz, profile=self.john)
        self.only_s_gamelsit = GameList.objects.create(
            game=self.only_one_to_sell_and_buy,
            profile=self.john, prop='s')
        self.only_b_gamelist = GameList.objects.create(
            game=self.only_one_to_sell_and_buy,
            profile=self.john, prop='b')
        self.inactive_john_gamelist = GameList.objects.create(
            game=self.only_one_to_sell_and_buy,
            profile=self.john, active=False, prop='s')
        self.future_john_gamelist = GameList.objects.create(
            game=self.only_one_to_sell_and_buy,
            profile=self.john,
            public_date = timezone.now() + timedelta(days=1),
            prop='b'
        )


    def test_two_gaemz(self):
        self.assertEqual(Game.objects.all().count(), 4)

    def test_john_from_minsk(self):
        self.assertEqual(self.john.place.name, 'minsk')

    def test_mary_password(self):
        self.assertTrue(self.mary.user.check_password('passwordmary'))
        self.assertFalse(self.mary.user.check_password('passwordjohn'))

    def test_game_sell_list(self):
        self.assertTrue(self.only_s_gamelsit in self.
            only_one_to_sell_and_buy.gamelists_to_sell())
        self.assertEqual(self.only_one_to_sell_and_buy.gamelists_to_buy().
            count(), 1)

    def test_game_buy_list(self):
        self.assertTrue(self.only_b_gamelist in self.
            only_one_to_sell_and_buy.gamelists_to_buy())
        self.assertEqual(self.only_one_to_sell_and_buy.gamelists_to_buy().
            count(), 1)

    def test_game_sell_list_with_inactive(self):
        self.assertFalse(self.inactive_john_gamelist in \
            self.only_one_to_sell_and_buy.gamelists_to_sell())

    def test_game_buy_list_with_future(self):
        self.assertFalse(self.future_john_gamelist in \
            self.only_one_to_sell_and_buy.gamelists_to_buy())

    def test_underscored_game_name(self):
        game = Game(name="Some great name")
        self.assertEqual(game.underscored_name, "some_great_name")

    def test_game_absolute_url(self):
        self.assertEqual("/game-id/1/", self.tloz.get_absolute_url(),
            'game page now is not "/game-id/<game.id>/"')

    def test_game_oredered_objects_by_sell(self):
        gaem2 = Game.objects.create(name='name2')
        gaem1 = Game.objects.create(name='name1')
        GameList.objects.create(game=gaem2, profile=self.john, prop='s')
        GameList.objects.create(game=gaem2, profile=self.john, prop='s',
            active=False)
        GameList.objects.create(game=gaem2, profile=self.john, prop='s',
            public_date=timezone.now()+timedelta(days=1))
        GameList.objects.create(game=gaem2, profile=self.john, prop='b')
        GameList.objects.create(game=gaem1, profile=self.john, prop='s')
        GameList.objects.create(game=gaem1, profile=self.john, prop='s')
        set = list(Game.objects_ordered_by_sell())
        self.assertLess(set.index(gaem1), set.index(gaem2), "oreder is broken")
        gaem1.delete()
        gaem2.delete()

    def test_gamelist_ready_to_sell(self):
        game = Game(name='name')
        self.assertTrue(GameList(game=game, profile=self.john, prop='s',
            public_date=timezone.now()-timedelta(minutes=5)).\
            ready_to_sell)
        self.assertFalse(GameList(game=game, profile=self.john, prop='b').\
            ready_to_sell)
        self.assertFalse(GameList(game=game, profile=self.john, prop='b',
            active=False).ready_to_sell)
        self.assertFalse(GameList(game=game, profile=self.john, prop='b',
            public_date=timezone.now()+timedelta(days=1)).ready_to_sell)

    def test_profile_get_username(self):
        self.assertEqual(self.john.get_username(), 'john')

    def test_profile_get_absolute_url(self):
        self.assertEqual('/accounts/profile/john/',
            self.john.get_absolute_url(),
            'profile page is not "/accounts/profile/<username>"')


    # TODO: _list methods of GameList

class ViewTest(TestCase):
    def setUp(self):
        self.tloz = Game.objects.create(name='TLOZ')
        self.smo = Game.objects.create(name='SMO')
        self.smk = Game.objects.create(name='SMK')

        minsk = Place.objects.create(name='minsk')
        np = Place.objects.create(name='np')

        self.john = Profile.create_profile('john', 'john@example.com',
            'passwordjohn', place=minsk)
        self.mary = Profile.create_profile('mary', 'mary@example.com',
        'passwordmary', place=np)

        self.c = Client()

    def test_login(self):
        c = Client()
        response = c.post("/accounts/login/",
            {'username': 'john',
            'password': 'passwordjohn'},
            follow=True)
        self.assertEqual(200, response.status_code, 'login page not return 200 \
on succsess')
        self.assertEqual((self.john.get_absolute_url(), 302),
            response.redirect_chain[-1],
            'ok login not redirect to profile page by default')

    def test_login_failed(self):
        c = Client()
        response = c.post("/accounts/login/",
            {'username': 'john',
            'password': 'wrongpassword'})
        self.assertIn('error', str(response.content))

    def test_index(self):
        resp = self.c.get('/')
        self.assertEqual(200, resp.status_code, 'index is not accesible')

    def test_profile_logged_redirection(self):
        logged_c = Client()
        logged_c.login(username='john', password='passwordjohn')
        resp = logged_c.get("/accounts/profile", follow=True)
        self.assertEqual((self.john.get_absolute_url(), 302),
            resp.redirect_chain[-1],
            'logged profile not redirect to profile page')

    def test_profile_unlogged(self):
        resp = self.c.get("/accounts/profile/", follow=True)
        self.assertEqual(302, resp.redirect_chain[0][1], 'not redirected')
        self.assertIn("?next=/accounts/profile",
        resp.redirect_chain[0][0], 'next arg setted wrong')

    def test_game_id(self):
        resp = self.c.get(f"/game-id/{self.tloz.id}/")
        self.assertEqual(200,
            resp.status_code,
            'game page is not reachable by id')
        self.assertIn("TLOZ", str(resp.content),
            'game name not presented on game page')

    def test_lot(self):
        gl = GameList.objects.create(game=self.tloz, profile=self.john, prop='s')
        resp = self.c.get(f"/lot/{gl.id}/")
        self.assertEqual(200, resp.status_code,
            'gamelist (lot) is not reachable')
        self.assertIn("TLOZ", str(resp.content),
            'game name not presented on gamelist (lot) page')

    def test_add_game_form(self):
        c = Client()
        c.login(username="john", password="passwordjohn")
        self.assertEqual(200, c.get("/add-game/keep/").status_code,
            'get page for adding keep game is not reachable')

    def test_sign_up_access(self):
        resp = self.c.get("/accounts/signup/")
        self.assertEqual(200, resp.status_code,
            'Sign Up page not accessible via "/accounts/signup"')

    def test_sign_up_success_redirecting(self):
        resp = self.c.post("/accounts/signup/",
            {'username': 'foo',
            'email': 'foo@bar.spam',
            'password1': 'foobarpassword',
            'password2': 'foobarpassword'},
            follow=True
        )
        self.assertEqual(200, resp.status_code,
            'Submit button on signup form dont return OK status code')
        self.assertEqual(302, resp.redirect_chain[0][1],
            'Submit button dont redirecting')
        self.assertEqual("/accounts/need-confirmation/",
            resp.redirect_chain[0][0],
            'Submitting not redirectin to "/accounts/need-confirmation/"')

    def test_sign_up_create_inactive_user(self):
        resp = self.c.post("/accounts/signup/",
            {'username': 'mariah',
            'email': 'foo@bar.spam',
            'password1': 'foobarpassword',
            'password2': 'foobarpassword'},
        )
        mariah = Profile.objects.filter(user__username='mariah')[0]
        self.assertFalse(mariah.user.is_active,
            'Signed not confirmed user is active')
        mariah.user.delete()

    def test_sign_up_email(self):
        mail.outbox = []
        resp = self.c.post("/accounts/signup/",
            {'username': 'mariah',
            'email': 'foo@bar.spam',
            'password1': 'foobarpassword',
            'password2': 'foobarpassword'},
        )

        self.assertFalse(Client().login(username='mariah',
            password='foobarpassword'), 'can log in without confirmation')

        self.assertEqual(1, len(mail.outbox), 'send not 1 email')
        self.assertEqual('foo@bar.spam', mail.outbox[0].message().get('To'),
            'send message to wrong email')

        activate_url_pattern = "/accounts/activate/"
        regex = r"https?://.*(?P<local_ref>"+activate_url_pattern+r"[^/]*/[^/]*/)"
        result = re.search(regex, str(mail.outbox[0].message()))
        local_ref = result.group('local_ref')
        resp = Client().get(local_ref)
        self.assertEqual(200, resp.status_code, 'activation link is accessible')
        self.assertTrue(Client().login(username='mariah',
            password='foobarpassword'), 'cannot log in after confirmation')

        mariah = Profile.objects.filter(user__username='mariah')[0]
        mariah.user.delete()

    def test_place_list_accessable(self):
        resp = self.c.get("/place/")
        self.assertEqual(200, resp.status_code, 'places list is not accessable')

    def test_place_accessable(self):
        resp = self.c.get("/place/minsk/")
        self.assertEqual(200, resp.status_code, 'place is not accessable')
        self.assertIn("Minsk", str(resp.content), 'Title name is not on place page')

    def test_user_list_page(self):
        resp = self.c.get("/accounts/")
        self.assertEqual(200, resp.status_code, 'Accounts list is not accessable')
