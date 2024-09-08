from django import forms
from .models import Post, Comment

# 新規投稿
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

# コメント 
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

