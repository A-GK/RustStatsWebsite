from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import User
from .user_data import *


def create_user(**kwargs):
    user_id = kwargs.get("user_id", "123456789012345678")
    user_name = kwargs.get("user_name", "Some username")
    avatar = kwargs.get("avatar", "f1/f1dd60a188883caf82d0cbfccfe6aba0af1732d4_full.jpg")
    user = User(user_id=user_id, user_name=user_name, avatar=avatar)
    user.save()
    return user

class UserModelTests(TestCase):
    def test_was_model_created(self):
        user = create_user()
        if not user:
            raise Exception("User wasn't created")

    def test_model_has_correct_fields(self):
        user = create_user(user_id="994", user_name="user58 :)", avatar="f1/f1dd60a188883caf82d0cbfccfe6aba0af1732d4_full.jpg")
        self.assertIs(user.user_id, "994")
        self.assertIs(user.user_name, "user58 :)")
        self.assertIs(user.avatar, "f1/f1dd60a188883caf82d0cbfccfe6aba0af1732d4_full.jpg")

    def test_model_with_invalid_fields(self):
        user = create_user()
        try:
            user.deaths = -5
            user.save()
        except Exception:
            pass
        else:
            raise Exception("This field accepted a negative number")

    def test_model_has_incorrect_fields(self):
        """Fields with data should not equal to something random"""
        user = create_user()
        self.assertIsNot(user.user_id, "9965")
        self.assertIsNot(user.user_name, "user59c hello")
        self.assertIsNot(user.avatar, "f1/invalid_invalid_invalid_full.jpg")

    def test_model_retrieving_using_pk(self):
        some_user = create_user(user_id="99")
        user = User.objects.get(pk="99")
        if not user:
            raise Exception("User doesn't not exist when it should")

    def test_model_has_correct_user_stats(self):
        user = create_user(user_id="1")
        self.assertIs(user.deaths, 0)
        user.deaths = 20
        user.save()
        user = User.objects.get(pk="1")
        self.assertIsNot(user.deaths, 0)
        self.assertIs(user.deaths, 20)


class UserDataPulling(TestCase):
    """
    Testing functions from user_data.py in the format test_<function_name>.
    All of the mock data is coming from mock_test_data.py.
    """
    def test_get_raw_user_stats(self):
        raw_user_stats = get_raw_user_stats("0000")
        self.assertEqual(raw_user_stats, steam_raw_game_stats_request_successful)

    def test_parse_raw_user_stats(self):
        raw_user_stats = get_raw_user_stats("0000")
        user_stats = parse_raw_user_stats(raw_user_stats)
        self.assertEqual(user_stats, steam_parsed_user_stats_successful)

    def test_remove_user_stats_duplicates(self):
        raw_user_stats = get_raw_user_stats("0000")
        user_stats = parse_raw_user_stats(raw_user_stats)
        user_stats_no_duplicates = remove_user_stats_duplicates(user_stats)
        self.assertEqual(user_stats_no_duplicates, parsed_user_stats_no_duplicates_successful)

    def test_convert_stats_names(self):
        raw_user_stats = get_raw_user_stats("0000")
        user_stats = parse_raw_user_stats(raw_user_stats)
        user_stats_no_duplicates = remove_user_stats_duplicates(user_stats)
        user_stats_converted_names = convert_stats_names(user_stats_no_duplicates)
        self.assertEqual(user_stats_converted_names, user_stats_converted_names_successfull)

    def test_get_user_stats(self):
        user_stats = get_user_stats("0000")
        self.assertEqual(user_stats, user_stats_converted_names_successfull)

    def test_get_user_name_and_avatar(self):
        user_name_and_avatar = get_user_name_and_avatar("0000")
        self.assertEqual(user_name_and_avatar, {'avatar': '00/0000AA_full.jpg', 'user_name': 'super cool user name'})

    def test_get_user_name_and_avatar(self):
        hours_played = get_user_hours_played("0000")
        self.assertEqual(hours_played, 7923)
    
    def test_create_user_data(self):
        """Data is created from mock_test_data.py"""
        create_user_data("0000")
        user = User.objects.get(pk="0000")
        self.assertIsNotNone(user)
        self.assertEqual(user.user_id, "0000")
        self.assertEqual(user.user_name, "super cool user name")
        self.assertEqual(user.hours_played, 7923)
        self.assertEqual(user.avatar, "00/0000AA_full.jpg")
        self.assertEqual(user.deaths, 9735)
        self.assertEqual(user.deaths_to_fall, 29)
        self.assertEqual(user.blocks_upgraded, 43872)


def create_user_stats():
    create_user_data("0000")
    user = User.objects.get(pk="0000")
    return user    

class UserStatsView(TestCase):
    def test_user_stats_view_exists(self):
        user = create_user_stats()
        response = self.client.get("/rust-stats/user-stats/" + user.user_id)
        self.assertEqual(response.status_code, 200)

    def test_user_stats_view_returns_success_true(self):
        user = create_user_stats()
        response = self.client.get("/rust-stats/user-stats/" + user.user_id)
        self.assertEqual(response.json()["success"], True)

    def test_user_stats_view_equals_model(self):
        user = create_user_stats()
        response = self.client.get("/rust-stats/user-stats/" + user.user_id).json()
        self.assertEqual(response["user_name"], user.user_name)
        self.assertEqual(response["hours_played"], user.hours_played)
        self.assertEqual(response["avatar"], user.avatar)
        self.assertEqual(response["deaths_to_selfinflicted"], user.deaths_to_selfinflicted)
        
