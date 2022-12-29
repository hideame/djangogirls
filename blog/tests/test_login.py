from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginTest(TestCase):
    # テスト用DBにユーザを作成
    fixtures = [
        "users",
    ]
    list_url = reverse("post_list")

    def admin_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="admin"))

    def staff_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="staff01"))

    def user_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="user01"))

    def test_正常系_admin権限ログイン(self):
        self.admin_login()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_正常系_staff権限ログイン(self):
        self.staff_login()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_正常系_user権限ログイン(self):
        self.user_login()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_正常系_未ログイン(self):
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_正常系_admin権限_管理画面(self):
        self.admin_login()
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/blog/post/")
        self.assertEqual(response.status_code, 200)

    def test_異常系_staff権限_管理画面(self):
        self.staff_login()
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/blog/post/")
        self.assertEqual(response.status_code, 403)

    def test_異常系_user権限_管理画面(self):
        self.user_login()
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)

    def test_異常系_未ログイン_管理画面(self):
        self.client.logout()
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
