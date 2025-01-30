from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        views.CategoryPostsListView.as_view(),
        name='category_posts'
    ),
    path(
        'profile/<slug:username>/',
        views.UserProfileListView.as_view(),
        name='profile'
    ),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<post_id>/edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('posts/<post_id>/delete/', views.PostDeleteView.as_view(), name='delete_post'),
    path('posts/<post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<post_id>/edit_comment/<comment_id>/', views.CommentUpdateView.as_view(), name='edit_comment'),
    path('posts/<post_id>/delete_comment/<comment_id>/', views.CommentDeleteView.as_view(), name='delete_comment'),
    
]

# urlpatterns = [
#     
#     path('<int:pk>/', views.PostDetailView.as_view(), name='detail'),
#     path('list/', views.PostListView.as_view(), name='list'),
#     # path('login_only/', views.simple_view),
# ]