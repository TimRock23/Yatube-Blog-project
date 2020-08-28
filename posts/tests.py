from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import File
from django.core.cache import cache

from io import BytesIO
from PIL import Image
import os

from .models import User, Post, Group, Comment, Follow


class TestSprint5(TestCase):

    def setUp(self):
        self.client_not_auth = Client()
        self.client_auth = Client()
        self.user = User.objects.create_user(
            username='TestUser',
            password='TestPorol123'
        )
        self.client_auth.force_login(self.user)
        self.reverse_profile = reverse('profile', args=[self.user.username])
        self.post = Post.objects.create(text='SomeTestText', author=self.user)
        self.reverse_index = reverse('index')
        self.reverse_new = reverse('new_post')
        self.reverse_post = reverse('post_id', args=[self.user.username,
                                                     self.post.id])
        self.reverse_post_edit = reverse('post_edit', args=[self.user.username,
                                                            self.post.id])

    def get_responses(self):
        responses = [
            self.client.get(self.reverse_index),
            self.client.get(self.reverse_profile),
            self.client.get(self.reverse_post),
        ]
        return responses

    def get_index(self):
        return self.client.get()

    def test_profile(self):
        """Проверка на создание страницы пользователя после регистрации"""
        response = self.client.get(self.reverse_profile)
        self.assertEqual(response.status_code, 200)

    def test_post_auth(self):
        """Проверка на возможность авторизованного пользователя создать пост"""
        self.client_auth.post(self.reverse_new, {'text': 'TestPostAuth'})
        self.assertTrue(Post.objects.filter(text='TestPostAuth'))

    def test_post_not_auth(self):
        """Проверка на невозможность создания поста
        у неавторизованного пользователя"""
        self.client_not_auth.post(self.reverse_new,
                                  {'text': 'TestPostNotAuth'})
        self.assertFalse(Post.objects.filter(text='TestPostNotAuth'))

    def test_post(self):
        """Проверка на наличие новой записи на главной странице,
        странцие пользователя и на странице самого поста"""
        cache.clear()
        for resp in self.get_responses():
            self.assertContains(resp, self.post.text)

    def test_change_post(self):
        """Проверка на возможность редактирования поста
        с изменением содержимого на всех связанных страницах"""
        self.client_auth.post(
            self.reverse_post_edit,
            {'text': 'ChangedTestText'}
        )
        for resp in self.get_responses():
            self.assertContains(resp, 'ChangedTestText')
            self.assertNotContains(resp, self.post.text)


class TestSprint6(TestCase):

    def setUp(self):
        self.client_auth = Client()
        self.user = User.objects.create_user(
            username='TestUser',
            password='TestPorol123'
        )
        self.client_auth.force_login(self.user)
        self.group = Group.objects.create(title='test', slug='test',
                                          description='test')
        self.post = Post.objects.create(text='SomeTestText', author=self.user)
        self.client_auth2 = Client()
        self.user2 = User.objects.create_user(
            username='TestUser2',
            password='ANaMoreBeliyPesok'
        )
        self.client_auth2.force_login(self.user2)
        self.post2 = Post.objects.create(text='AnotherText', author=self.user2)
        self.reverse_follow_index = reverse('follow_index')
        self.reverse_follow = reverse(
            'profile_follow', args=[self.user2.username]
        )
        self.reverse_unfollow = reverse(
            'profile_unfollow', args=[self.user2.username]
        )
        self.reverse_comment = reverse('add_comment', args=[
            self.user.username,
            self.post.id
        ])

    def test_error404(self):
        """Проверка о выдаче ошибки 404, если страницы не существует"""
        response = self.client.get('/random_page_404/')
        self.assertEqual(response.status_code, 404)

    def test_img(self):
        """Проверка записи, группы, профиля и главной на наличие картинки"""
        file_obj = BytesIO()
        img = Image.new('RGBA', (50, 50), color=(256, 0, 0))
        img.save(file_obj, 'png')
        file_obj.seek(0)
        image = File(file_obj, 'test_image.png')
        post = Post.objects.create(text='post with image',
                                        author=self.user, image=image,
                                        group=self.group)

        urls = [
            reverse('index'),
            reverse('post_id', args=[self.user.username, post.id]),
            reverse('profile', args=[self.user.username]),
            reverse('group', args=[post.group]),
        ]

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, '<img ')
        os.remove('media/posts/test_image.png')

    def test_not_img(self):
        """Проверка защиты от загрузки файлов не-графических форматов"""
        not_image = SimpleUploadedFile(
            name='test_not_img.txt',
            content=b'abc',
            content_type='text/plain',
        )
        url = reverse('new_post')
        response = self.client_auth.post(url,
                                         {'text': 'post without image',
                                          'image': not_image})
        error = ('Загрузите правильное изображение. Файл, который вы '
                 'загрузили, поврежден или не является изображением.')
        self.assertFormError(response, 'form', 'image', error)

    def test_cache(self):
        """Проверка на работу кеша"""
        url = reverse('index')
        self.client.get(url)
        post = Post.objects.create(text='CacheTest', author=self.user)
        response_before = self.client.get(url)
        self.assertNotContains(response_before, post.text)
        cache.clear()
        response_after = self.client.get(url)
        self.assertContains(response_after, post.text)

    def test_follow(self):
        """Проверка на возможность подписаться"""
        self.client_auth.get(self.reverse_follow)
        self.assertTrue(Follow.objects.filter(user=self.user,
                                              author=self.user2))

    def test_unfollow(self):
        """Проверка на возможность отписаться"""
        self.client_auth.get(self.reverse_follow)
        self.assertTrue(Follow.objects.filter(user=self.user,
                                              author=self.user2))
        self.client_auth.get(self.reverse_unfollow)
        self.assertFalse(Follow.objects.filter(user=self.user,
                                               author=self.user2))

    def test_follow_post(self):
        """Проверка появления нового поста у подписчика"""
        self.client_auth.get(self.reverse_follow)
        response_before = self.client_auth.get(self.reverse_follow_index)
        post = Post.objects.create(text='OneMoreTest', author=self.user2)
        self.assertNotContains(response_before, post.text)
        response_after = self.client_auth.get(self.reverse_follow_index)
        self.assertContains(response_after, post.text)

    def test_unfollow_post(self):
        """Проверка на отсутствие поста у неподписанного юзера"""
        post = Post.objects.create(text='AnotherTest', author=self.user2)
        response = self.client_auth.get(self.reverse_follow_index)
        self.assertNotContains(response, post.text)

    def test_comment_not_auth(self):
        """Проверка того, что неавторизированный пользователь
        не может комментировать посты"""
        text = 'TestTestTest'
        self.client.post(self.reverse_comment, {'text': text})
        self.assertFalse(Comment.objects.filter(post=self.post, text=text))

    def test_comment_auth(self):
        """Проверка того, что только авторизированный пользователь
        может комментировать посты"""
        self.client_auth.post(self.reverse_comment, {'text': 'HelloKitty'})
        self.assertTrue(Comment.objects.filter(post=self.post,
                                               text='HelloKitty'))

    def tearDown(self):
        cache.clear()
