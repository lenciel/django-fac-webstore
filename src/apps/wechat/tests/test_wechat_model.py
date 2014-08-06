from django.test import TestCase
from django.test.utils import setup_test_environment
from apps.wechat.models import WeChatProfile

setup_test_environment()


class WeChatAccessTokenModelTest(TestCase):
    def setUp(self):
        if WeChatProfile.objects.count() == 0:
            t = WeChatProfile(access_token='hi', expires_at=0)
            t.save()
        WeChatProfile.objects.clean_access_token()

    def tearDown(self):
        WeChatProfile.objects.clean_access_token()

    def test_refresh_access_token(self):
        token = 'hi'
        expires_at = 100.0
        WeChatProfile.objects.refresh_access_token(token, expires_at)
        self.assertEqual(WeChatProfile.objects.get_access_token(), token)

    def test_refresh_access_token_more(self):
        token1 = 'hi1'
        token2 = 'hi2'
        expires_at = 100.0
        WeChatProfile.objects.refresh_access_token(token1, expires_at)
        WeChatProfile.objects.refresh_access_token(token2, expires_at)
        self.assertEqual(token2, WeChatProfile.objects.get_access_token())
        self.assertEqual(1, WeChatProfile.objects.count())

    def test_is_token_expired(self):
        self.assertTrue(WeChatProfile.objects.is_access_token_expired(0))
        token = 'hi'
        expires_at = 100
        WeChatProfile.objects.refresh_access_token(token, expires_at)
        self.assertTrue(WeChatProfile.objects.is_access_token_expired(101))
        self.assertFalse(WeChatProfile.objects.is_access_token_expired(99))