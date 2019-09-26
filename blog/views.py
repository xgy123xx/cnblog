from django.shortcuts import render,HttpResponse,redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from blog.Myforms import *
from blog.models import *
from django.db.models import F
from django.http import JsonResponse
import json
import os
from bs4 import BeautifulSoup
from cnblog import settings
from blog.utils import validCode
import time
import threading
from django.core.mail import send_mail
from django.contrib.auth.hashers import check_password,make_password
# Create your views here.
# 登录判断
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code","")
        valid_code_str = request.session.get("valid_code_str","")
        response = {"user":None,"msg":None}
        print(valid_code,"  ",valid_code_str)
        if valid_code.strip().upper() == valid_code_str.upper():
            user = auth.authenticate(username=username,password=pwd)
            if user:
                auth.login(request,user)
                response["user"] = username
            else:
                response["msg"] = "用户名或密码错误"
        else:
            response["msg"] = "验证码错误"
        return JsonResponse(response)

    return render(request,"login.html")
# 首页
def index(request):
    article_list = Article.objects.all()
    return render(request,"index.html",{"article_list":article_list})
# 个人空间
def homeSite(request,username,**kwargs):
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request,"not_found.html")

    # 查询博客
    blog_obj = user.blog

    # 查询用户下面的文章
    article_list = user.article_set.all()

    # 设置有参数的情况
    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")
        if condition == "category":
            article_list = article_list.filter(category__title=param)
        elif condition == "tag":
            article_list = article_list.filter(tags__title=param)
        else:
            year,month = param.split("-")
            article_list = article_list.filter(create_time__year=year,create_time__month=month)

    # 查询年月对于文章数
    # # 方式一：
    # date_list = Article.objects.filter(user=user).extra(select={"format_time":"date_format(create_time,'%%Y-%%m')"}).values("format_time").\
    #     annotate(c=Count("nid")).values_list("format_time","c")
    # print(ret)
    # 上述格式已经过滤好

    # # 方式二   第一个values是用截断的month分组，然后统计每组元素个数，再显示月份和统计数
    # from django.db.models.functions import TruncMonth
    # date_list = Article.objects.filter(user=user).annotate(month=TruncMonth("create_time")).values("month").annotate(c=Count("nid")).values_list("month","c")
    # print(date_list)

    # 注意，上述方法返回的还是一个datetime类,在魔板中还需要手动过滤一下。。。过滤出年月的格式

    return  render(request,"home_site.html",locals())
# 文章详情表
def article_detail(request,username,article_id):
    user = UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request,"not_found.html")
    # 查询博客
    blog_obj = user.blog

    article_obj = user.article_set.all().filter(nid=article_id).first()

    comment_list = Comment.objects.filter(article_id=article_id).all()
    return render(request,"article_detail.html",locals())
# 点赞
def digg(request):
    is_up = json.loads(request.POST.get("is_up"))
    article_id = request.POST.get("article_id")
    user_id = request.user.pk
    ret = ArticleUpDown.objects.filter(article_id=article_id,user_id=user_id).first()
    respone = {"state":True}
    if not ret:
        ArticleUpDown.objects.create(is_up=is_up,article_id=article_id,user_id=user_id)
        article_obj = Article.objects.filter(nid=article_id)
        if is_up:
            article_obj.update(up_count =F("up_count")+1)
        else:
            article_obj.update(down_count =F("down_count")+1)
    else:
        respone["state"] = False
        respone["handled"] = ret.is_up
    return JsonResponse(respone)
# 评论
def comment(request):
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    # 防止XSS
    content=BeautifulSoup(content,"html.parser")
    for tag in content.find_all():
        print(tag.name)
        if tag.name == "script":
            tag.decompose()
    print(content)
    if not content.text:
        content = "该用户没有评论任何内容"
        print(content)
    # content="该用户没有评论任何内容"  #当评论中script被过滤掉后，没有任何内容时提示
    pid = request.POST.get("pid")
    user_id = request.user.pk

    #导入事物
    from django.db import transaction
    with transaction.atomic():
        comment_obj = Comment.objects.create(article_id=article_id,content=content,user_id=user_id,parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count")+1)
    # 将评论信息通过字典的方式返回给ajax   将时间对象转换字符串
    article_obj = Article.objects.filter(pk=article_id).first()
    #发邮件给作者   主题  邮件内容   发件人  收件人


    # t = send_mail("你的文章%s新增一条评论内容"%article_obj.title,
    #           content,
    #           settings.EMAIL_HOST_USER,
    #           ["xgy123xx@163.com"],
    #               fail_silently=False
    #           )
    # print("发送情况",t)

    t= threading.Thread(target=send_mail,args=("你的文章%s新增一条评论内容"%article_obj.title,
                                               content,
                                               settings.EMAIL_HOST_USER,
                                               [article_obj.user.email]
                                               ))
    t.start()

    response = {"create_time":comment_obj.create_time.strftime("%Y-%m-%d %H:%M"),"username":comment_obj.user.username,"content":comment_obj.content}
    return JsonResponse(response)
# 显示文章信息
@login_required
def cn_backend(request):
    print(request.GET)
    user_id = request.user.pk
    article_list = Article.objects.filter(user_id=user_id).all()
    if request.GET:
        comment_descend = request.GET.get("comment_descend","")
        up_descend = request.GET.get("up_descend","")
        print(comment_descend,up_descend)
        if comment_descend:
            order = "-comment_count" if comment_descend == "true" else "comment_count"
        else:
            order = "-up_count" if up_descend == "true" else "up_count"
        article_list = article_list.order_by(order)
    return render(request,"backend.html",locals())
# 添加文章
@login_required
def add_article(request):
    if request.method == "POST":
        user_id = request.user.pk
        title = request.POST.get("article_header")
        content = request.POST.get("article_main")
        # 内容过滤
        soup = BeautifulSoup(content,"html.parser")
        for tag in soup.find_all():
            if tag.name=="script":
                tag.decompose()
        desc =  soup.text[0:150]
        Article.objects.create(user_id=user_id,title=title,content=content,desc=desc)
        return redirect("/cn_backend/")

    return render(request,"add_article.html")
# 编辑文章
@login_required
def edit_article(request,nid):
    article_obj = Article.objects.filter(pk=nid).first()
    if not article_obj:
        return render(request,"not_found.html")
    if request.method == "POST":
        title = request.POST.get("article_header")
        content = request.POST.get("article_main")
        soup = BeautifulSoup(content,"html.parser")
        for tag in soup.find_all():
            print(tag.name)
            if tag.name == "script":
                tag.decompose()
        desc = soup.text[0:150]
        Article.objects.filter(pk=nid).update(title=title,content=content,desc=desc)
        return redirect("/cn_backend/")

    return render(request,"edit_article.html",{"article_obj":article_obj})
# 删除文章
@login_required
def delete_article(request,nid):
    Article.objects.filter(pk=nid).delete()
    return redirect("/cn_backend/")
# 标签管理
@login_required
def tag_manage(request):
    blog_id = request.user.blog.pk
    tag_list = Tag.objects.filter(blog_id=blog_id).all()
    return render(request,"tag_manage.html",locals())
# 添加标签
@login_required
def add_tag(request):
    if request.method == "POST":
        tag_title = request.POST.get("tag_title")
        con_article = request.POST.getlist("con_article")
        blog = request.user.blog
        tag_obj = Tag.objects.create(blog=blog,title=tag_title)
        object_list = []
        for i in range(len(con_article)):
            object_list.append(Article2Tag(tag=tag_obj,article_id=con_article[i]))
        Article2Tag.objects.bulk_create(object_list)
        return redirect("/tag_manage/")
    else:
        article_list = Article.objects.filter(user=request.user.pk).all()
        return render(request,"add_tag.html",{"article_list":article_list})
# 编辑标签
@login_required
def edit_tag(request,nid):
    if request.method == "POST":
        tag_title = request.POST.get("tag_title")
        con_article = request.POST.getlist("con_article")
        blog = request.user.blog
        tag_obj = Tag.objects.filter(pk=nid).update(blog=blog,title=tag_title)
        # 更新自定义第三张表
        Article2Tag.objects.filter(tag_id=nid).delete()  #先删除，再更新
        object_list = []
        for i in range(len(con_article)):
            object_list.append(Article2Tag(tag_id=nid,article_id=con_article[i]))
        Article2Tag.objects.bulk_create(object_list)
        return redirect("/tag_manage/")
    else:
        # 跨表第三张表中找到与目标tag相关联的article的列表
        article_selected = Article.objects.filter(article2tag__tag_id=nid).all()
        article_list = Article.objects.filter(user=request.user.pk).all()
        tag_obj = Tag.objects.filter(pk=nid).first()
        return render(request,"edit_tag.html",{"article_selected":article_selected,"article_list":article_list,"tag_obj":tag_obj})
# 删除标签
@login_required
def delete_tag(request,nid):
    # 删除该记录时，顺便将第三张表关联记录也删除
    Tag.objects.filter(pk=nid).delete()
    Article2Tag.objects.filter(tag_id=nid).delete()
    return redirect("/tag_manage/")
# 分类管理
@login_required
def category_manage(request):
    blog_id = request.user.blog.pk
    category_list = Category.objects.filter(blog_id=blog_id).all()
    return render(request,"category_manage.html",locals())
# 添加分类
@login_required
def add_category(request):
    if request.POST:
        category_title = request.POST.get("category_title")
        con_article = request.POST.getlist("con_article")
        blog = request.user.blog
        category_obj = Category.objects.create(title=category_title,blog=blog)
        # 使用循环添加记录
        for i in range(len(con_article)):
            article_obj = Article.objects.filter(pk=con_article[i]).first()  #找到文章对象
            category_obj.article_set.add(article_obj)
        return redirect("/category_manage/")
    else:
        article_list = Article.objects.filter(user=request.user.pk).all()
        return render(request,"add_category.html",{"article_list":article_list})
# 编辑分类
@login_required
def edit_category(request,nid):
    if request.method == "POST":
        category_title = request.POST.get("category_title")
        con_article = request.POST.getlist("con_article")
        blog = request.user.blog
        Category.objects.filter(pk=nid).update(blog=blog,title=category_title)
        article_obj_list = [Article.objects.filter(pk=con_article[i]).first() for i in range(len(con_article))]
        Category.objects.filter(pk=nid).first().article_set.set(article_obj_list)
        return redirect("/category_manage/")
    else:
        article_selected = Article.objects.filter(category_id=nid).all()
        article_list = Article.objects.filter(pk=nid).all()
        category_obj = Category.objects.filter(pk=nid).first()
        return render(request,"edit_category.html",{"article_selected":article_selected,"article_list":article_list,"category_obj":category_obj})
# 删除分类
@login_required
def delete_category(request,nid):
    Category.objects.filter(pk=nid).first().delete()
    return redirect("/category_manage/")
# 个人设置
@login_required
def personal_set(request):
    if request.method == "POST":
        print(request.POST)
        if request.FILES:
            avatar_obj =  request.FILES.get("avatar","")
            if avatar_obj and avatar_obj != "undefined":
                avatar = "avatars/%s"%avatar_obj
                print( avatar_obj )
                UserInfo.objects.filter(pk=request.user.pk).update(avatar=avatar)
            return HttpResponse("OK")
        else:
            #         用来校验邮箱或者密码
            response = {"isValid":False,"msg":""}

            if "validCode" in request.POST:# 获取验证码校验
                valid_code = request.POST.get("validCode")
                valid_code_str = request.session.get("valid_code_str","")
                if valid_code.strip().upper() == valid_code_str.upper():
                    #     获取原邮箱地址
                    #     对比ajax传过来的地址
                    #     将修改后的邮箱地址使用form校验
                    old_email = request.user.email
                    email = request.POST.get("email")
                    new_email = request.POST.get("new_email")
                    if old_email == email:
                        form = UserForms({"email":new_email})
                        form.is_valid()
                        if form.cleaned_data.get("email"):
                            response["isValid"] = True
                            UserInfo.objects.filter(pk=request.user.pk).update(email=new_email)
                        else:
                            response["msg"] = "邮箱地址不正确"
                    else:
                        response["msg"] = "原邮箱地址错误"
                else:
                    response["msg"] = "验证码错误"
                return JsonResponse(response)
            else:
                response = {"isValid":False,"msg":""}
    #             密码校验
                old_pwd = request.POST.get("old_pwd")
                new_pwd = request.POST.get("pwd")
                re_pwd = request.POST.get("re_pwd")
                pwd_str = request.user.password
                if check_password(old_pwd,pwd_str):
                        form = UserForms({"pwd":new_pwd,"re_pwd":re_pwd})
                        form.is_valid()
                        print(form.cleaned_data)
                        if form.cleaned_data.get("pwd") and form.cleaned_data.get("pwd"):
                            if new_pwd == re_pwd:
                                response["isValid"] = True
                                UserInfo.objects.filter(pk=request.user.pk).update(password=make_password(new_pwd))
                            else:
                                response["msg"] = "密码和确认密码不一致"
                        else:
                            response["msg"] = "密码格式错误"

                else:
                    response["msg"] = "原密码错误"
                return JsonResponse(response)


    return render(request,"personal_set.html",locals())
# 上传图片
def upload(request):
    upload_img = request.FILES.get("upload_img")
    path = os.path.join(settings.MEDIA_ROOT,"add_article_img",upload_img.name)
    with open(path,"wb") as f:
        for line in upload_img:
            f.write(line)
    response = {
        "error":0,
        "url":"/media/add_article_img/%s"%upload_img.name
    }

    return HttpResponse(json.dumps(response))
# 获取评论树
def get_comment_tree(request):
    article_id = request.GET.get("article_id")
    article_list = Comment.objects.filter(article_id=article_id).values("pk","content","parent_comment_id","create_time","user__username")
    return JsonResponse(list(article_list),safe=False)
# 获取验证码图片
def get_validCode_img(request):

    data = validCode.get_valid_code_img(request)
    return HttpResponse(data)
# 发送验证码邮件
def send_validCode(request):
    # 获取session中的时间参数，对比时间，if 时间间隔要》60秒 则 重置session,发送邮件 else 什么也不做返回错误消息,时间间隔小于60s
    # 发送邮件，使用线程，并且判断是否发送成功，不成功，返回参数
    response = {"state":"false","msg":""}
    valid_code_time = request.session.get("valid_code_time","")
    now_time = time.time()   #判断时间间隔是不是1min
    if not valid_code_time or int(now_time-valid_code_time) >= 60:
        # 设置时间间隔，发送邮件，
        request.session["valid_code_time"] = now_time
        data = validCode.get_valid_code_img(request)    #二进制图片内容
        file_name = os.path.join(settings.MEDIA_ROOT,"validCodeImg/%s.png"%request.user.username)
        with open(file_name,"wb+") as f:
            f.write(data)
        # 发送验证码  图片暂时不用python发,好麻烦啊啊啊...使用django发送html邮件
        from django.core.mail import EmailMultiAlternatives

        valid_code_url = "%s/media/validCodeImg/%s.png"%(settings.LOCAL_URL,request.user.username)
        html_content = "<p>您的验证码</p><img src='%s'>"%valid_code_url
        # 验证码发过去是空时
        from smtplib import SMTPRecipientsRefused
        try:
            msg = EmailMultiAlternatives("%s博客园的验证码"%request.user.username,"你没有收到html邮件", settings.EMAIL_HOST_USER,[request.user.email])
            msg.attach_alternative(html_content,"text/html")
            email_state = msg.send()
        except SMTPRecipientsRefused as e:
            email_state = False
        print(email_state)
        if email_state:
            response["msg"] = "OK"
            response["state"] = "true"
        else:
            response["msg"] = "邮箱不正确"
    else:
        remain_time = 60 - int(now_time-valid_code_time)
        response["msg"] = "请%ss后重试"%remain_time
    return JsonResponse(response)
# 登出
def logout(request):
    auth.logout(request)
    return redirect("/login/")
# 注册
def register(request):
    if request.is_ajax():
        form = UserForms(request.POST)
        response = {"user":None,"msg":None}
        if form.is_valid():
            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar = request.FILES.get("avatar")
            extra = {}
            if avatar:
                extra["avatar"]=avatar
            blog_obj = Blog.objects.create(title=user,site_name=user,theme="default.css")
            UserInfo.objects.create_user(username=user,email=email,password=pwd,blog=blog_obj,**extra)
            response["user"] = form.cleaned_data.get("user")
        else:
            print(form.cleaned_data)
            print(form.errors)
            response["msg"] = form.errors

        return JsonResponse(response)
    form = UserForms()
    return render(request,"register.html",{"form":form})