from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'index.html', {'page': page,
                                          'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'group.html', {'group': group, 'page': page,
                                          'paginator': paginator})


@login_required
def new_post(request):
    if request.method != 'POST':
        form = PostForm()
        return render(request, 'new_post.html', {'form': form})

    form = PostForm(request.POST, files=request.FILES or None, )
    if form.is_valid():
        post_new = form.save(commit=False)
        post_new.author = request.user
        post_new.save()
        return redirect('index')

    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    length = len(post_list)
    following = Follow.objects.filter(
        user__username=request.user, author__username=username).exists()
    context = {
        'author': author,
        'page': page,
        'length': length,
        'paginator': paginator,
        'following': following,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    post_list = post.author.posts.all()
    length = post_list.count()
    comments = post.comments.all()
    form = CommentForm()
    user = request.user
    context = {'author': post.author, 'post': post,
               'length': length, 'items': comments,
               'form': form, 'user': user,
               }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)

    if request.user != user:
        return redirect('post_id', username=post.author.username,
                        post_id=post_id)

    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)

    if form.is_valid():
        form.save()
        return redirect('post_id', username=username, post_id=post_id)

    return render(request, 'new_post.html', {'post': post, 'form': form})


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    comments = post.comments.all()

    if request.method != 'POST':
        form = CommentForm()
        return render(request, 'includes/comments.html', {'form': form,
                                                          'post': post,
                                                          'user': user,
                                                          'items': comments})

    form = CommentForm(request.POST)
    if form.is_valid():
        comment_new = form.save(commit=False)
        comment_new.post = post
        comment_new.author = request.user
        comment_new.save()
        return redirect('post_id', username=username, post_id=post_id)

    return render(request, 'includes/comments.html', {'form': form,
                                                      'post': post,
                                                      'user': user,
                                                      'items': comments})


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page,
                                           'paginator': paginator})


@login_required
def profile_follow(request, username):
    following = get_object_or_404(User, username=username)
    if following != request.user and not Follow.objects.filter(
            user=request.user, author=following
            ).exists():
        Follow.objects.create(user=request.user, author=following)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    following = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=following).exists():
        Follow.objects.filter(user=request.user, author=following).delete()
    return redirect('profile', username=username)
