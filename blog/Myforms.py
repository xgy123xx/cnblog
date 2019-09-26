from django import forms
from django.forms import widgets
from blog.models import UserInfo
from django.core.exceptions import ValidationError
class UserForms(forms.Form):
    user = forms.CharField(max_length=32,widget=widgets.TextInput(attrs={"class":"form-control"}),error_messages={"required":"用户名不能为空"},label="用户名")
    pwd = forms.CharField(max_length=32,widget=widgets.PasswordInput(attrs={"class":"form-control"}),label="密码",error_messages={"required":"密码不能为空"})
    re_pwd = forms.CharField(max_length=32,widget=widgets.PasswordInput(attrs={"class":"form-control"}),label="确认密码",error_messages={"required":"密码不能为空"})
    email = forms.EmailField(max_length=32,widget=widgets.EmailInput(attrs={"class":"form-control"}),label="邮箱",error_messages={"required":"邮箱不能为空"})

    def clean_user(self):
        user = self.cleaned_data.get("user")
        res = UserInfo.objects.filter(username=user).first()
        if not res:
            return user
        else:
            raise ValidationError("用户名已存在")

    def clean(self):
        pwd = self.cleaned_data.get("pwd")
        re_pwd = self.cleaned_data.get("re_pwd")
        if pwd and re_pwd:
            if pwd == re_pwd:
                return self.cleaned_data
            else:
                raise ValidationError("确认密码不一致")

