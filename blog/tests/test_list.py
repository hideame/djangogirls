from blog.models import Post
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class TestListView(TestCase):
    fixtures = ["users",]
    list_url = reverse("post_list")
    new_url = reverse("post_new")

    # def admin_login(self):
    #     self.client.logout()
    #     self.client.force_login(User.objects.get(username="admin"))

    # def staff_login(self):
    #     self.client.logout()
    #     self.client.force_login(User.objects.get(username="staff01"))

    def user_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="user01"))

    def test_正常系_POSTデータなし(self):
        """初期状態では何も登録されていないことを確認"""
        self.assertEqual(Post.objects.all().count(), 0)

    def test_post_list_url(self):
        """トップページへ遷移できることをテスト"""
        self.user_login()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_post_new_url(self):
        """作成ページへ遷移できることをテスト"""
        self.user_login()
        response = self.client.get(self.new_url)
        self.assertEqual(response.status_code, 200)


class TestCreateView(TestCase):
    fixtures = ["users",]
    list_url = reverse("post_list")
    new_url = reverse("post_new")

    def admin_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="admin"))

    def staff_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="staff01"))

    def user_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="user01"))

    def test_正常系_POST(self):
        self.admin_login()
        params = {
            "title": "タイトル１",
            "text": "内容１",
        }
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(title="タイトル１").exists())
        # データの登録
        create_response = self.client.post(self.new_url, params)
        self.assertEqual(create_response.status_code, 302)
        # データが登録されていることを確認
        self.assertTrue(Post.objects.filter(title="タイトル１").exists())
        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, 200)
        self.assertTrue(
            list_response.context["posts"].filter(title="タイトル１").exists()
        )

    def test_異常系_POST_タイトルなし(self):
        self.admin_login()
        params = {
            "title": "",
            "text": "内容のみ_タイトルなし",
        }
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(text="内容のみ_タイトルなし").exists())
        # データの登録
        create_response = self.client.post(self.new_url, params)
        self.assertNotEqual(create_response.status_code, 302)
        expect_form_errors = {"title": ["このフィールドは必須です。"]}
        self.assertDictEqual(create_response.context["form"].errors, expect_form_errors)
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(text="内容のみ_タイトルなし").exists())
        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, 200)
        self.assertFalse(
            list_response.context["posts"].filter(text="内容のみ_タイトルなし").exists()
        )

