from django import forms
from .models import Post, Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import SetPasswordForm

# 新規投稿
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'picture']
        
# コメント 
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

# ユーザ名と新しいパスワードを入力
class CustomPasswordResetForm(forms.Form):
    username = forms.CharField(label='ユーザー名', max_length=150)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("このユーザー名は存在しません。")
        return username


class CustomSetPasswordForm(SetPasswordForm):
    def save(self, commit=True):
        user = self.user
        user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
        return user
    