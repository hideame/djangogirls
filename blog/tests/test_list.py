from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from blog.models import Post

# NOTE: admin権限は利用想定していないのでテストしない
# TODO: user権限でログイン可能になったらテストケース追加する


class TestListView(TestCase):
    fixtures = [
        "users",
    ]
    list_url = reverse("post_list")
    new_url = reverse("post_new")

    def staff_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="staff01"))

    def test_正常系_POSTデータなし(self):
        """初期状態では何も登録されていないことを確認"""
        self.assertEqual(Post.objects.all().count(), 0)

    def test_正常系_list_staff権限(self):
        """トップページへ遷移できることをテスト"""
        self.staff_login()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_正常系_list_未ログイン(self):
        """トップページへ遷移できることをテスト"""
        self.client.logout()
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_正常系_new_staff権限(self):
        """記事作成ページへ遷移できることをテスト"""
        self.staff_login()
        response = self.client.get(self.new_url)
        self.assertEqual(response.status_code, 200)

    def test_正常系_new_未ログイン(self):
        """記事作成ページへ遷移できることをテスト"""
        self.client.logout()
        response = self.client.get(self.new_url)
        self.assertEqual(response.status_code, 200)


class TestCreateView(TestCase):
    fixtures = [
        "users",
    ]
    list_url = reverse("post_list")
    new_url = reverse("post_new")
    char_200 = "aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeeeffffffffffgggggggggghhhhhhhhhhiiiiiiiiiijjjjjjjjjjkkkkkkkkkkllllllllllmmmmmmmmmmnnnnnnnnnnooooooooooppppppppppqqqqqqqqqqrrrrrrrrrrsssssssssstttttttttt"

    def staff_login(self):
        self.client.logout()
        self.client.force_login(User.objects.get(username="staff01"))

    def test_正常系_POST_staff権限(self):
        self.staff_login()
        params = {
            "title": "タイトル１",
            "text": "内容１",
        }
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(title="タイトル１").exists())
        # データの登録
        create_response = self.client.post(self.new_url, params)
        self.assertEqual(create_response.status_code, 302)
        # 一覧ページを表示
        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, 200)
        # データが登録されていることを確認
        self.assertTrue(Post.objects.filter(title="タイトル１").exists())
        self.assertTrue(list_response.context["posts"].filter(title="タイトル１").exists())

    def test_異常系_POST_未ログイン(self):
        self.client.logout()
        params = {
            "title": "タイトル２",
            "text": "内容２",
        }
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(title="タイトル２").exists())
        # データの登録
        with self.assertRaises(ValueError):
            self.client.post(self.new_url, params)

    def test_異常系_POST_タイトルなし(self):
        self.staff_login()
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
        # 一覧ページを表示
        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, 200)
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(text="内容のみ_タイトルなし").exists())
        self.assertFalse(list_response.context["posts"].filter(text="内容のみ_タイトルなし").exists())

    def test_異常系_POST_コンテンツなし(self):
        self.staff_login()
        params = {
            "title": "タイトルのみ",
            "text": "",
        }
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(title="タイトルのみ").exists())
        # データの登録
        create_response = self.client.post(self.new_url, params)
        self.assertNotEqual(create_response.status_code, 302)
        expect_form_errors = {"text": ["このフィールドは必須です。"]}
        self.assertDictEqual(create_response.context["form"].errors, expect_form_errors)
        # 一覧ページを表示
        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, 200)
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(title="タイトルのみ").exists())
        self.assertFalse(list_response.context["posts"].filter(title="タイトルのみ").exists())

    def test_正常系_POST_タイトル文字数200文字(self):
        self.staff_login()
        params = {
            "title": self.char_200,
            "text": "タイトル文字数200OK",
        }
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(title=self.char_200).exists())
        # データの登録
        create_response = self.client.post(self.new_url, params)
        self.assertEqual(create_response.status_code, 302)
        # 一覧ページを表示
        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, 200)
        # データが登録されていることを確認
        self.assertTrue(Post.objects.filter(title=self.char_200).exists())
        self.assertTrue(list_response.context["posts"].filter(title=self.char_200).exists())
        print(list_response.context["posts"])

    def test_異常系_POST_タイトル文字数201文字(self):
        char_201 = self.char_200 + "z"
        self.staff_login()
        params = {
            "title": char_201,
            "text": "タイトル文字数201NG",
        }
        # データが登録されていないことを確認
        self.assertFalse(Post.objects.filter(title=char_201).exists())
        # データの登録
        create_response = self.client.post(self.new_url, params)
        self.assertNotEqual(create_response.status_code, 302)
        expect_form_errors = {"title": ["この値は 200 文字以下でなければなりません( 201 文字になっています)。"]}
        self.assertDictEqual(create_response.context["form"].errors, expect_form_errors)
        # 一覧ページを表示
        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, 200)
        # 201文字のタイトルでデータが登録されていないことを確認
        self.assertFalse(Post.objects.filter(title=char_201).exists())
        self.assertFalse(Post.objects.filter(text="タイトル文字数201NG").exists())
        self.assertFalse(list_response.context["posts"].filter(title=char_201).exists())
        self.assertFalse(list_response.context["posts"].filter(text="タイトル文字数201NG").exists())
