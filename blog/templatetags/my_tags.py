from django import template
from django.db.models import Count
from blog.models import *
register = template.Library()

@register.inclusion_tag("classification.html")
def get_classification_style(username):
    user = UserInfo.objects.filter(username=username).first()
    # 查询博客
    blog_obj = user.blog

    # 查询用户下面的标签和文章数
    tag_list = Tag.objects.filter(blog=blog_obj).values("pk").annotate(c=Count("article__title")).values_list("title","c")

    # 查询用户下面的分类
    category_list = Category.objects.filter(blog=blog_obj).values("pk").annotate(c=Count("article__title")).values_list("title","c")

    # 方式二   第一个values是用截断的month分组，然后统计每组元素个数，再显示月份和统计数
    from django.db.models.functions import TruncMonth
    date_list = Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values("month").annotate(c=Count("nid")).values_list("month","c")

    return {"tag_list":tag_list,"category_list":category_list,"date_list":date_list}