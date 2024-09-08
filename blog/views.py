from django.shortcuts import render
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from.models import Post, Like
from.forms import PostForm, CommentForm

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

def home(request):
    # 投稿一覧を表示
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'blog/home.html', {'posts': posts})

@login_required
# 投稿作成
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
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
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form, 'post': post})
    
# 投稿を削除
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('home')
    
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    
    return render(request, 'blog/post_delete_confirm.html', {'post': post})

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
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        form = CommentForm()
    
    return render(request, 'blog/add_comment.html', {'form': form, 'post': post})
