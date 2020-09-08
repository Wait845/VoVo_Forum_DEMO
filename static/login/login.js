$(document).ready(function () {
    $("#login").click(function () {
        var id = $("#id").val()
        var pwd = $("#pwd").val()
       if (!check()) {
           return false
       }else {
           // 发送LOGIN请求
           $.ajax({
               type: "POST",
               url: "/api/login/",
               async: false,
               cache: false,
               dataType: "json",
               data: {"email": id, "pwd": pwd},
               success: function (data) {
                   var code = data.code
                   var msg = data.msg
                   if (code == 302) {
                       $(location).attr('href', msg);
                   }else {
                       $(".alert-danger p").html(code + ":" + msg)
                       $(".alert-danger").css("visibility", "visible")
                   }

               },
               error: function () {
                   $(".alert-danger p").html("CLG001:未知错误")
                   $(".alert-danger").css("visibility", "visible")
               }



           });
       }
    });
});

function check() {

    var id = $("#id").val()
    var pwd = $("#pwd").val()
    var idRegex = /[a-zA-Z0-9_-]{6,18}/.test(id)
    var pwdRegex = /[a-zA-Z0-9_-]{6,18}/.test(pwd)
    if (!idRegex) {
        $("#id").focus()
        $(".alert-danger p").html("输入的邮箱有误")
        $(".alert-danger").css("visibility", "visible")
        return false
    }else if (!pwdRegex) {
        $("#pwd").focus()
        $(".alert-danger p").html("输入的密码有误")
        $(".alert-danger").css("visibility", "visible")
        return false
    }else {
        return true
    }

}

function qanda() {
    if ($("#qanda").css("display") == "none") {
        $("#qanda").css("display", "block")
    }else {
        $("#qanda").css("display", "none")
    }
}
