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
]

# urlpatterns = [
#     path('', views.PostCreateView.as_view(), name='create'),
#     path('list/', views.PostListView.as_view(), name='list'),
#     path('<int:pk>/', views.PostDetailView.as_view(), name='detail'),
#     path('<int:pk>/edit/', views.PostUpdateView.as_view(), name='edit'),
#     path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete'),
#     path('<int:pk>/comment/', views.add_comment, name='add_comment'),
#     # path('login_only/', views.simple_view),
# ]