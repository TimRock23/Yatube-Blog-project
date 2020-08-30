from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField('title', max_length=200)
    slug = models.SlugField('slug', blank=True, null=True, unique=True)
    description = models.TextField('description', )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Время публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='posts',
                              verbose_name='Группа')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    like_num = models.IntegerField(default=0, verbose_name='Лайки')
    like_done = models.ManyToManyField(User, related_name='liked')

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('Текст комментария', max_length=1000)
    created = models.DateTimeField('Время публикации', auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')

    class Meta:
        unique_together = ['user', 'author']

