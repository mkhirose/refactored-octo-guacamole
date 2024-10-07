from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import ListView
from.models import Post, Like, Comment
from django.db.models import Count
from.forms import PostForm, CommentForm, CustomPasswordResetForm, CustomSetPasswordForm

# サインアップ
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'blog/signup.html', {'form': form})

# ホーム
# def home(request):
#     # 投稿一覧を表示
#     posts = Post.objects.all().order_by('-created_at')
#     return render(request, 'blog/home.html', {'posts': posts})

class HomeView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 10  # ページネーション: 1ページ10件表示

    def get_queryset(self):
        # 並び替えパラメータ 'ordering' を取得（デフォルトは '-created_at'）
        ordering = self.request.GET.get('ordering', '-created_at')

        # 'like'のカウントを注釈し、いいね数を利用したソートを可能に
        queryset = Post.objects.annotate(like_count=Count('like'))

        # 並び替えロジックを適用
        if ordering == 'likes':  # いいね順
            return queryset.order_by('-like_count', '-created_at')
        elif ordering == 'oldest':  # 古い順
            return queryset.order_by('created_at')
        elif ordering == 'newest':  # 新しい順
            return queryset.order_by('-created_at')
        else:  # デフォルトは新しい順
            return queryset.order_by('-created_at')
        
# ログイン後にパスワードを変更する
def custom_password_reset_request(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user = get_object_or_404(User, username=username)
            request.session['reset_user_id'] = user.id
            return redirect('custom_password_reset_confirm')
    else:
        form = CustomPasswordResetForm()

    return render(request, 'blog/custom_password_reset_request.html', {'form': form})

def custom_password_reset_confirm(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, 'パスワードリセットリクエストが見つかりません。')
        return redirect('custom_password_reset_request')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            del request.session['reset_user_id']
            messages.success(request, 'パスワードがリセットされました。')
            return redirect('login')
    else:
        form = CustomSetPasswordForm(user)

    return render(request, 'blog/custom_password_reset_confirm.html', {'form': form})

# ログアウト
def logout_view(request):
    logout(request)
    messages.success(request, "《ログアウトしました。》")
    return redirect('login')  # 'login' はログイン画面のURL名

@login_required
# 投稿作成
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # 画像を処理するためにrequest.FILESを追加
        if form.is_valid():
            form.instance.author = request.user
            form.save()
            return redirect('home')
    else:
        form = PostForm()

    return render(request, 'blog/post_create.html', {'form': form})
# 投稿を編集
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('home')
    
    if request.method == 'POST':
        form = PostForm(request.POST,request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form, 'post': post})
    
# 投稿を削除
def delete_post(request, post_id):
    if request.method == "POST":  # POST リクエストのみ許可
        post = get_object_or_404(Post, id=post_id)
        if request.user == post.author:  # 投稿の著者のみ削除できる
            post.delete()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': '権限がありません'}, status=403)
    return JsonResponse({'success': False, 'error': '無効なリクエスト'}, status=400)

# 投稿をクリックすると詳細ページへ遷移する
def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})

# 「いいね」を押した際の動作
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # ユーザーがすでにこの投稿に「いいね」をしているか確認
    liked = Like.objects.filter(user=request.user, post=post).exists()
    
    if liked:
        # すでに「いいね」していたら削除
        Like.objects.filter(user=request.user, post=post).delete()
        liked = False
    else:
        # 「いいね」していなければ追加
        Like.objects.create(user=request.user, post=post)
        liked = True
    
    # 投稿に関連付けられた「いいね」のカウントを取得
    like_count = post.like_set.count()
    
    # JSONレスポンスを返す
    return JsonResponse({'liked': liked, 'like_count': like_count})

# コメント追加
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        content = request.POST['content']
        parent_id = request.POST.get('parent_id')  # 親コメントのIDを取得
        comment = Comment.objects.create(content=content, user=request.user, post=post)
        
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            comment.parent = parent_comment  # 親コメントを設定
            comment.save()

        return redirect('post_detail', post_id=post.id)

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post).select_related('user').prefetch_related('replies')  # 'comment_set' ではなく 'replies'
    comment_form = CommentForm()

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.user = request.user
            if 'parent_id' in request.POST:
                parent_id = request.POST.get('parent_id')
                parent_comment = Comment.objects.get(id=parent_id)
                new_comment.parent = parent_comment
            new_comment.save()
            return redirect('post_detail', post_id=post_id)

    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })
    
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # パスワードを変更した後、セッションを更新してユーザーをログアウトさせないようにする
            update_session_auth_hash(request, user)
            messages.success(request, 'パスワードが変更されました！')
            return redirect('home')  # パスワード変更後のリダイレクト先
        else:
            messages.error(request, 'エラーが発生しました。もう一度試してください。')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'blog/change_password.html', {'form': form})
