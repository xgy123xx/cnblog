from django.db import models
from django.contrib.auth.models import User,AbstractUser
# Create your models here.
class UserInfo(AbstractUser):
    """
    个人信息表
    upload_to:来指定文件存放的前缀路径
    verbose_name:
    """
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11,null=True,unique=True)
    avatar = models.FileField(upload_to="avatars/",default="avatars/default.png")
    create_time = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)

    blog = models.OneToOneField(to="blog",to_field="nid",null=True,on_delete=models.CASCADE)

    def __str__(self):
        return self.username

class Blog(models.Model):
    """
    博客信息表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name="个人博客标题",max_length=64)
    site_name = models.CharField(verbose_name="站点名",max_length=64)
    theme = models.CharField(verbose_name="博客主题",max_length=32)

    def __str__(self):
        return self.title

class Category(models.Model):
    """
    博客个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name="分类标题",max_length=32)

    blog = models.ForeignKey(verbose_name="所属博客",to="blog",to_field="nid",on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Tag(models.Model):
    """
    博客个人标签
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(verbose_name="标签名称",max_length=32)

    blog = models.ForeignKey(verbose_name="所属博客",to="blog",to_field="nid",on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Article(models.Model):
    """
    文章表
    """
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50,verbose_name="文章标题")
    desc = models.CharField(max_length=255,verbose_name="文章描述")
    create_time = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)

    comment_count = models.IntegerField(default=0)
    up_count = models.IntegerField(default=0)
    down_count = models.IntegerField(default=0)

    user = models.ForeignKey(to="UserInfo",to_field="nid",verbose_name="作者",on_delete=models.CASCADE)
    category = models.ForeignKey(to="Category",to_field="nid",null=True,on_delete=models.SET_NULL)
    tags = models.ManyToManyField(
        to="Tag",
        through='Article2Tag',
        through_fields=("article","tag"),
    )
    content = models.TextField()
    def __str__(self):
        return self.title

class Article2Tag(models.Model):
    """
    多表的第三张关联表
    """
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(to="Article",to_field="nid",verbose_name="文章",on_delete=models.CASCADE)
    tag = models.ForeignKey(to="Tag",to_field="nid",verbose_name="标签",on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('article','tag'),
        ]
    def __str__(self):
        v = self.article.title + "----" + self.tag.title
        return v

class ArticleUpDown(models.Model):
    """
    点赞表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey("UserInfo",null=True,on_delete=models.CASCADE)
    article = models.ForeignKey("Article",null=True,on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    class Meta:
        unique_together = [
            ('article',"user"),
        ]

class Comment(models.Model):
    """
    评论表
    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(verbose_name="评论者",to="UserInfo",null=True,on_delete=models.CASCADE)
    article = models.ForeignKey(verbose_name="评论文章",to="Article",null=True,on_delete=models.CASCADE)

    content = models.CharField(verbose_name="评论内容",max_length=255)
    create_time = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    parent_comment = models.ForeignKey("self",null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return self.content



