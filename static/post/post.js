function reply() {
    var postID = postvue.host.postID
    var content = $("#reply-box").val()
    $.ajax({
        url: '/api/reply/',
        type: 'post',
        async: false,
        cache: false,
        data: {"postID":postID, "replyContent":content},
        dataType: 'json',
        success: function (data) {
            var code = data.code
            var msg = data.msg
            // 注册成功
            if (code == "ARP004") {
                location.href = msg
            }else {
                alert("错误 " + code + msg)
            }
        },error: function () {
            // 注册失败，弹出错误信息。
            alert("CRG001:未知错误");

        }
    });
}