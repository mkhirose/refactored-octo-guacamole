from django.db import models
from django.contrib.auth.models import User

# 投稿テーブル
class Post(models.Model):
    title = models.CharField(max_length=200) # タイトル
    content = models.TextField() # 本文
    author = models.ForeignKey(User, on_delete=models.CASCADE) # 著者
    picture = models.ImageField(upload_to='post_images/', blank=True, null=True)  # 画像フィールド
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# いいねテーブル
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # ユーザーが同じ投稿に複数回いいねできないようにする

    def __str__(self):
        return f'{self.user} likes {self.post}'

# コメントテーブル
class Comment(models.Model):
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies') # 親コメント
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user} on {self.post}'
