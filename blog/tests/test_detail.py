from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blog.models import Post

# NOTE: admin権限は利用想定していないのでテストしない
# TODO: user権限でログイン可能になったらテストケース追加する


class TestDetailView(TestCase):
    fixtures = [
        "users",
    ]
    user = User.objects.get(username="staff01")
    detail_url = reverse("post_detail", kwargs={"pk": 1})
    edit_url = reverse("post_edit", kwargs={"pk": 1})

    def staff_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="staff01"))

    def setUp(self):
        """テスト環境の準備用メソッド"""
        post1 = Post.objects.create(title="タイトル１", text="内容１", author=self.user)

    def test_正常系_POSTデータあり(self):
        """初期状態で1件のデータが登録されていることを確認"""
        self.assertEqual(Post.objects.all().count(), 1)

    def test_正常系_post_detail_staff権限(self):
        """詳細ページへ遷移できることをテスト"""
        self.staff_login()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "タイトル１")
        self.assertContains(response, "内容１")

    def test_正常系_detail_未ログイン(self):
        """詳細ページへ遷移できることをテスト"""
        self.client.logout()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "タイトル１")
        self.assertContains(response, "内容１")

    def test_正常系_edit_staff権限(self):
        """記事編集ページへ遷移できることをテスト"""
        self.staff_login()
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

    def test_正常系_edit_未ログイン(self):
        """記事編集ページへ遷移できることをテスト"""
        self.client.logout()
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)


class TestUpdateView(TestCase):
    fixtures = [
        "users",
    ]
    user = User.objects.get(username="staff01")
    detail_url = reverse("post_detail", kwargs={"pk": 1})
    edit_url = reverse("post_edit", kwargs={"pk": 1})
    char_200 = "aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeffffffffffgggggggggghhhhhhhhhhiiiiiiiiiijjjjjjjjjjkkkkkkkkkkllllllllllmmmmmmmmmmnnnnnnnnnnooooooooooppppppppppqqqqqqqqqqrrrrrrrrrrsssssssssstttttttttt"

    def staff_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="staff01"))

    def setUp(self):
        """テスト環境の準備用メソッド"""
        post1 = Post.objects.create(title="タイトル１", text="内容１", author=self.user)

    def test_正常系_POST_staff権限(self):
        self.staff_login()
        params = {
            "title": "タイトル２",
            "text": "内容２",
        }
        # データが更新されていないことを確認
        self.assertFalse(Post.objects.filter(title="タイトル２").exists())
        # データの更新
        update_response = self.client.post(self.edit_url, params)
        self.assertEqual(update_response.status_code, 302)
        # 詳細ページを表示
        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.status_code, 200)
        # データが更新されていることを確認
        self.assertTrue(Post.objects.filter(title="タイトル２").exists())
        self.assertContains(detail_response, "タイトル２")
        self.assertContains(detail_response, "内容２")

    def test_異常系_POST_未ログイン(self):
        self.client.logout()
        params = {
            "title": "タイトル３",
            "text": "内容３",
        }
        # データが更新されていないことを確認
        self.assertFalse(Post.objects.filter(title="タイトル３").exists())
        # データの更新
        with self.assertRaises(ValueError):
            self.client.post(self.edit_url, params)

    def test_異常系_POST_タイトルなし(self):
        self.staff_login()
        params = {
            "title": "",
            "text": "内容のみ_タイトルなし",
        }
        # データが更新されていないことを確認
        self.assertFalse(Post.objects.filter(text="内容のみ_タイトルなし").exists())
        # データの更新
        update_response = self.client.post(self.edit_url, params)
        self.assertNotEqual(update_response.status_code, 302)
        expect_form_errors = {"title": ["このフィールドは必須です。"]}
        self.assertDictEqual(update_response.context["form"].errors, expect_form_errors)
        # 詳細ページを表示
        detail_response = self.client.get(self.edit_url)
        self.assertEqual(detail_response.status_code, 200)
        # データが更新できていないことを確認
        self.assertFalse(Post.objects.filter(text="内容のみ_タイトルなし").exists())
        self.assertNotContains(detail_response, "内容のみ_タイトルなし")

    def test_異常系_POST_コンテンツなし(self):
        self.staff_login()
        params = {
            "title": "タイトルのみ",
            "text": "",
        }
        # データが更新されていないことを確認
        self.assertFalse(Post.objects.filter(title="タイトルのみ").exists())
        # データの更新
        update_response = self.client.post(self.edit_url, params)
        self.assertNotEqual(update_response.status_code, 302)
        expect_form_errors = {"text": ["このフィールドは必須です。"]}
        self.assertDictEqual(update_response.context["form"].errors, expect_form_errors)
        # 詳細ページを表示
        detail_response = self.client.get(self.edit_url)
        self.assertEqual(detail_response.status_code, 200)
        # データが更新できていないことを確認
        self.assertFalse(Post.objects.filter(title="タイトルのみ").exists())
        self.assertNotContains(detail_response, "タイトルのみ")

    def test_正常系_POST_タイトル文字数200文字(self):
        self.staff_login()
        params = {
            "title": self.char_200,
            "text": "タイトル文字数200OK",
        }
        # データが更新されていないことを確認
        self.assertFalse(Post.objects.filter(title=self.char_200).exists())
        # データの更新
        update_response = self.client.post(self.edit_url, params)
        self.assertEqual(update_response.status_code, 302)
        # 詳細ページを表示
        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.status_code, 200)
        # データが更新されていることを確認
        self.assertTrue(Post.objects.filter(title=self.char_200).exists())
        self.assertContains(detail_response, self.char_200)
        self.assertContains(detail_response, "タイトル文字数200OK")

    def test_異常系_POST_タイトル文字数201文字(self):
        char_201 = self.char_200 + "z"
        self.staff_login()
        params = {
            "title": char_201,
            "text": "タイトル文字数201NG",
        }
        # データが更新されていないことを確認
        self.assertFalse(Post.objects.filter(title=char_201).exists())
        # データの更新
        update_response = self.client.post(self.edit_url, params)
        self.assertNotEqual(update_response.status_code, 302)
        expect_form_errors = {"title": ["この値は 200 文字以下でなければなりません( 201 文字になっています)。"]}
        self.assertDictEqual(update_response.context["form"].errors, expect_form_errors)
        # 詳細ページを表示
        detail_response = self.client.get(self.detail_url)
        self.assertEqual(detail_response.status_code, 200)
        # 201文字のタイトルでデータが更新されていないことを確認
        self.assertFalse(Post.objects.filter(title=char_201).exists())
        self.assertFalse(Post.objects.filter(text="タイトル文字数201NG").exists())
        self.assertNotContains(detail_response, char_201)
        self.assertNotContains(detail_response, "タイトル文字数201NG")
