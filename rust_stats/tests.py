from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import User


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
