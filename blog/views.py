from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views.generic import ListView
from django.views.generic import DetailView 
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.urls import reverse
from .forms import CommentForm
from .models import Post
from .models import Comment


def home(request):
    context = {
        'title': 'Home',
        'posts': Post.objects.all()
    }

    return render(request, 'blog/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name='posts'
    ordering = ['-date_posted']
    paginate_by = 7


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name='posts'
    paginate_by = 7

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))

        return Post.objects.filter(author=user).order_by('-date_posted')



class PostDetailView(DetailView):
    model = Post
            

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = [
        'title',
        'content'
    ]

    def form_valid(self, form):
        form.instance.author = self.request.user
        
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = [
        'title',
        'content'
    ]

    def form_valid(self, form):
        form.instance.author = self.request.user

        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:

            return True

        return False



class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:

            return True

        return False


def about(request):
    context = {
        'title': 'About'
    }

    return render(request, 'blog/about.html', context)


# FUNCTION-BASED VIEW FOR POST DETAIL
def post_detail(request, slug):
    template_name = 'blog/post_detail.html'
    object = get_object_or_404(Post, id=slug)
    comment_form = CommentForm(data=request.POST)
    user = request.user
    if request.method == 'POST':
        if comment_form.is_valid():
            comment = Comment(post=object, author=request.user, content=request.POST['content'])
            comment.save()
            comment_form = CommentForm()
    context = {
        'form': comment_form,
        'object': object,
        'user': user
    }

    return render(request, template_name, context)
