"""cnblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from blog import views
from django.views.static import serve
from cnblog import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',views.login),
    path('logout/',views.logout),
    path('index/',views.index),
    path('register/',views.register),
    path("get_validCode_img/",views.get_validCode_img),
    path("send_validCode/",views.send_validCode),
    path("digg/",views.digg),
    path("comment/",views.comment),
    path("upload/",views.upload),
    path("get_comment_tree/",views.get_comment_tree),
    path("cn_backend/",views.cn_backend),
    path("tag_manage/",views.tag_manage),
    path("category_manage/",views.category_manage),
    path("personal_set/",views.personal_set),
    path("add_article/",views.add_article),
    path("add_tag/",views.add_tag),
    path("add_category/",views.add_category),
    re_path("edit_article/(\d+)/",views.edit_article),
    re_path("edit_tag/(\d+)/",views.edit_tag),
    re_path("edit_category/(\d+)/",views.edit_category),
    re_path("delete_article/(\d+)/",views.delete_article),
    re_path("delete_tag/(\d+)/",views.delete_tag),
    re_path("delete_category/(\d+)/",views.delete_category),
    re_path(r"^$",views.index),
    re_path(r"media/(?P<path>.*)$",serve,{"document_root":settings.MEDIA_ROOT}),
    re_path(r"^(?P<username>\w+)/(?P<condition>category|tag|archive)/(?P<param>.*)/$",views.homeSite),
    re_path(r"^(?P<username>\w+)/$",views.homeSite),
    re_path(r"(?P<username>\w+)/articles/(?P<article_id>\d+)",views.article_detail)
]
