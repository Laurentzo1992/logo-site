from django.urls import path
from . import views

urlpatterns = [
    path('blog', views.blog, name='blog'),
    path("search/",                    views.search_view,         name="search"),
    path("category/<slug:slug>/",      views.category_view,       name="category"),
    path("tag/<slug:slug>/",           views.tag_view,            name="tag"),
    path("newsletter/subscribe/",      views.newsletter_subscribe, name="newsletter"),
    path("<slug:slug>/",               views.article_detail,       name="detail"),
    path("<slug:slug>/comment/",       views.add_comment,          name="comment"),
]

