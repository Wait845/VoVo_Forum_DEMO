//加载窗口或窗口大小变动时，修改对应的宽
function adjustWidth() {
    pageWidth = window.innerWidth
    if (pageWidth > 768) {
        // document.body.style.marginLeft = (pageWidth - 768) / 2 + "px";
        // document.getElementById("main").style.marginLeft = (pageWidth - 768) / 2 + "px";
        $("#main").css("margin-left", (pageWidth - 768) / 2 + "px");
        $(".header-div").css("margin-left", (pageWidth - 768) / 2 + "px");

        // $(".user-info").css("right", (pageWidth - 768) / 2 + 20 + "px");




    }else {
    }
}
window.onload = adjustWidth
window.onresize = adjustWidth