/**
 * Created by 徐光宇 on 2018/10/11.
 */
$("#div_digg .action").click(function () {
    //                判断是点赞还是踩#}
    var is_up = $(this).hasClass("diggit");
    $obj = $(this).children("span").first();
    $.ajax({
        url:"/digg/",
        type:"post",
        data:{
            "csrfmiddlewaretoken":$("[name='csrfmiddlewaretoken']").val(),
            "is_up":is_up,
            "article_id":article.id
        },
        success: function(data) {
            if(data.state){
                //                            点赞做局部刷新  1.获得标签里面的值  2.使用parseInt将值转换为数字  3.做加法操作并赋值#}
                var num = parseInt($obj.text());
                $obj.text(num+1)
            }else{
                var val = data.handled?"你已经推荐过了":"你已经反对过了";
                $("#digg_tips").html(val)

            }
            setTimeout(function () {
                $("#digg_tips").html("")
            },1000)

        }
    })
});
var pid = '';   //存放父类id
var pname = "";  //存放父类名字
var pcontent = "";  //存放父类的内容
//提交评论按钮
$(".comment-btn").click(function () {
    var content = $("#tbCommentBody").val();
    if(pid && content[0]=="@"){
        //                pid有值，对其内容做截断处理#}
        var index = content.indexOf("\n");
        content=content.slice(index+1);   //存放需要发送的内容
    }else{
        pid = '';
    }
    $.ajax({
        url:"/comment/",
        type:"post",
        data:{
            //                    发送消息和文章id和父评论#}
            "csrfmiddlewaretoken":$("[name='csrfmiddlewaretoken']").val(),
            "content":content,
            "article_id":article.id,
            pid:pid
        },
        success: function (data) {

            //                    ajax做出一个根评论#}
            var create_time = data.create_time;
            var username = data.username;
            var recv_content = data.content;
            console.log(recv_content);
            if(pid){
                //                  判断是否是子评论，如果是子评论则插入父评论#}
                var s = `
                     <li class="list-group-item">
                    <div>
                        <span>${create_time}</span>&nbsp;&nbsp;
                        <a href="/${username}/">${username}</a>
                    </div>
                     <div class="comment-parent well">
                        ${pname}&nbsp;&nbsp;:
                        ${pcontent}
                    </div>
                    <div class="comment-con">
                        ${recv_content}
                    </div>
                    </li>
                    `;

            }else{
                var s = `
                     <li class="list-group-item">
                    <div>
                        <span>${create_time}</span>&nbsp;&nbsp;
                        <a href="/${username}/">${username}</a>
                    </div>
                    <div class="comment-con">
                        ${recv_content}
                    </div>
                    </li>
                    `;
            }
            $(".list-group").append(s);
            pid = "";
            pname = "";
            pcontent = "";
            $("#tbCommentBody").val("");
        }

    })
});
//回复评论按钮
$(".reply_btn").click(function () {
    $("#tbCommentBody").focus();
    pname = $(this).attr("username");
    pcontent = $(this).parent().siblings(".comment-con").text();
    var str = "@"+ pname +"\n";
    $("#tbCommentBody").text(str);
    pid =  $(this).attr("user_id")
});
//评论树
$(".comment_tree_btn").click(function () {
    $(this).addClass("disabled").siblings().removeClass("disabled");
    $(".comment_tree").css("display","block").siblings(".comment_list").css("display","none");
    $.ajax({
        url:"/get_comment_tree/",
        type:"get",
        data:{
            "article_id":article.id
        },
        success: function (data) {
            console.log(data);
            $(".comment_tree").html("");
            //                            先插入根节点#}
            $.each(data, function (index,comment_obj) {

                var pk=comment_obj.pk;
                var content=comment_obj.content;
                var parent_comment_id=comment_obj.parent_comment_id;
                var create_time = comment_obj.create_time;
                var username = comment_obj.user__username;
                var s = `
                     <li class="list-group-item comment_item" comment_id=${pk}>
                    <div>
                        <span>${create_time}</span>&nbsp;&nbsp;
                        <a href="/${username}/">${username}</a>
                    </div>
                    <div class="comment-con">
                        ${content}
                    </div>
                    </li>
                    `;
                if(!parent_comment_id){

                    $(".comment_tree").append(s);
                }else{
//                                    取到父评论节点，然后将子评论插入  使用属性选择器 #}
//                                    comment_id是为了找到目标评论的属性，class="comment_item"是为了渲染评论标签#}
                    //将父评论改变样式

                    $("[comment_id = "+parent_comment_id+"]").append(s).addClass("well")
                }

            })


        }
    })
});
$(".comment_default").click(function () {
    $(this).addClass("disabled").siblings().removeClass("disabled");
    $(".comment_list").css("display","block").siblings(".comment_tree").css("display","none");
});