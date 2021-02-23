$(function () {
    $('#username,#password').keydown(function () {
        if (event.keyCode == 13) login()
    });

    $('#login').click(function () {
        login()
    });

    function login() {
        //1.获取用户输入的用户名和密码
        username = $('#username').val();
        password = $('#password').val();
        //2. ajax发起登录请求
        $.ajax({
            url: "help/login",
            data: {'username': username, 'password': password},
            type: "get",
            dataType: 'text',
            success: function (data) {
                location.href = "/spider/setting.html"
            },
            error: function () {
                $.popUp("账号密码错误！", "error")
            }
        });
    }
});