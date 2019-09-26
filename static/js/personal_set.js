/**
 * Created by 徐光宇 on 2018/10/10.
 */
//{#    修改头像模态框#}
$("#modify-avatar").click(function () {
    //{#       创建一个模态框：先创建模态框盒子，将其隐藏起来，需要的时候使用display#}
    if(!$("#model-yes").hasClass("btn-avatar")){
        //{#            判断是否是修改头像模态框，是则跳过，不是则创建该模态框#}
        $("#model-yes").attr("class","btn btn-default btn-avatar");
        $("#model-title").text("修改头像");
        //获取页面上原用户图片的src
        var img_src = $("#avatar-img")[0].src;
        var body_str = '<img src="'+img_src+'" alt="avatar" id="avatar-img"> <input type="file" id="avatar">';
        $(".mymodal-body").html("");
        $(".mymodal-body").append(body_str);
        $(".btn-avatar")[0].onclick = up_avatar;
        $("#avatar").change(function () {
            //{#    1.读取文件#}
            var file_obj = $(this)[0].files[0];
            //{#    2.读取路径#}
            var reader = new FileReader();
            reader.readAsDataURL(file_obj);
            //{#    3.设置图片值#}
            reader.onload = function () {
                $("#avatar-img").attr("src",reader.result)
            }
        });
    }
    $("#wrapper").css("display","block")
});
function up_avatar () {
    //{#            将文件上传到服务器#}
    var formdata = new FormData();
    formdata.append("avatar", $("#avatar")[0].files[0]);
    formdata.append( "csrfmiddlewaretoken",$("[name='csrfmiddlewaretoken']").val());
    $.ajax({
        url:"",
        type:"post",
        contentType:false,
        processData:false,
        data:formdata,
        success: function (data) {
            location.reload()
        }
    })
}
$("#inner span").first().click(function () {
    $("#wrapper").css("display","none")
}); //模态框X号
$("#model-no").click(function () {
    $("#wrapper").css("display","none")
}); // 模态框取消选项

//{#   修改邮箱模态框#}
$("#modify-email").click(function () {
    //{#            判断是否是修改头像模态框，是则跳过，不是则创建该模态框#}
    if(!$("#model-yes").hasClass("btn-email")){
        $("#model-yes").attr("class","btn btn-default btn-email");
        $("#model-title").text("修改邮箱");
        var body_str = `
                 <!--{#使用bs设计一个表格，输入原邮箱，现在邮箱，发送验证码按钮，验证码，确定，取消#}-->
            <form id="email-form">
                <div class="col-sm-8 col-sm-offset-3 form-horizontal">
                    <div class="form-group">
                        <label for="" class="col-sm-3 control-label" >原邮箱地址</label>
                        <div class="col-sm-8">
                            <input type="email" class="form-control" id="email">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="" class="col-sm-3 control-label" >修改邮箱地址</label>
                        <div class="col-sm-8">
                            <input type="email" class="form-control" id="new_email">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="validCode" class="col-sm-3 control-label">验证码</label>
                        <div class="col-sm-4">
                            <input type="text" class="form-control" id="validCode">
                        </div>
                        <input type="button" class="btn btn-default" id="send_validCode" value="发送验证码" >
                    </div>
                    <span id="error_msg" class="text-danger"></span>
                </div>
            </form>`;
        $(".mymodal-body").html("");
        $(".mymodal-body").append(body_str);
        $("#send_validCode").click(function(){
            //{#                    使用ajax向服务器发送请求，请求发送验证码#}
            $.ajax({
                url:"/send_validCode/",
                type:"post",
                data:{
                    "csrfmiddlewaretoken":$("[name='csrfmiddlewaretoken']").val()
                },
                success: function (data) {
                    console.log(data);
                    $("#error_msg").text(data["msg"]);
                    setTimeout(function () {
                        $("#error_msg").text("");
                    },3000)
                }
            })
        });
        //{#                发送表单#}
        $(".btn-email")[0].onclick = up_email;
    }
    $("#wrapper").css("display","block");
});
function up_email() {
    //{#            将文件上传到服务器#}
    $.ajax({
        url:"",
        type:"post",
        data:{
            "csrfmiddlewaretoken":$("[name='csrfmiddlewaretoken']").val(),
            "email":$("#email").val(),
            "new_email":$("#new_email").val(),
            "validCode":$("#validCode").val()

        },
        success: function (data) {
            //    获取校验返回值
            console.log(data);
            if(data.isValid){
                location.reload()
            }else{
                $("#error_msg").text(data.msg);
                setTimeout(function () {
                    $("#error_msg").text("");
                },3000)
            }
        }
    })
}
//{#    修改密码#}
$("#modify-pwd").click(function () {
    if(!$("#model-yes").hasClass("btn-modifyPwd")) {
        $("#model-yes").attr("class","btn btn-default btn-modifyPwd");
        $("#model-title").text("修改密码");
        var body_str = `<!--{#使用bs设计一个表格，输入原邮箱，现在邮箱，发送验证码按钮，验证码，确定，取消#}-->
            <form id="pwd-form">
                <div class="col-sm-8 col-sm-offset-3 form-horizontal">
                    <div class="form-group">
                        <label for="" class="col-sm-3 control-label">原密码</label>
                        <div class="col-sm-8">
                            <input type="password" class="form-control" id="old_pwd">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="" class="col-sm-3 control-label">密码</label>
                        <div class="col-sm-8">
                            <input type="password" class="form-control" id="pwd">
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="" class="col-sm-3 control-label">确认密码</label>
                        <div class="col-sm-8">
                            <input type="password" class="form-control" id="re_pwd">
                        </div>
                    </div>
                    <span id="error_msg" class="text-danger"></span>
                </div>
            </form>`;
        $(".mymodal-body").html("");
        $(".mymodal-body").append(body_str);
        $(".btn-modifyPwd")[0].onclick = up_modifyPwd;
    }
    $("#wrapper").css("display","block");
});
function up_modifyPwd() {
    //    发送ajax 将原密码，确认密码发送的服务器
    $.ajax({
        url:"",
        type:"post",
        data:{
            "csrfmiddlewaretoken":$("[name='csrfmiddlewaretoken']").val(),
            "old_pwd":$("#old_pwd").val(),
            "pwd":$("#pwd").val(),
            "re_pwd":$("#re_pwd").val()
        },
        success: function (data) {
            console.log(data);
            if(data.isValid){
                location.reload()
            }else{
                $("#error_msg").text(data.msg);
                setTimeout(function () {
                    $("#error_msg").text("");
                },3000)
            }

        }
    })
}