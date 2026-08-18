from django.urls import path
from . import views

urlpatterns = [
    path('blog/',                      views.blog_index,          name='blog'),
    path("blog/search/",               views.search_view,         name="search"),
    path("blog/category/<slug:slug>/", views.category_view,       name="category"),
    path("blog/tag/<slug:slug>/",      views.tag_view,             name="tag"),
    path("blog/newsletter/subscribe/", views.newsletter_subscribe, name="newsletter"),
    path("blog/<slug:slug>/",          views.article_detail,       name="detail"),
    path("blog/<slug:slug>/comment/",  views.add_comment,          name="comment"),
]
