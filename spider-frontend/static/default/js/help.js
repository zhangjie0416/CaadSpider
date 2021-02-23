$(document).ready(function () {

    {
        $.ajax({
            url: "/help/get_versions",
            type: "get",
            dataType: 'json',
            success: function (data) {
                for (var i = 0; i < data.length; i++) {
                    var li = '';
                    var numbers = data[i]['version'].match(/(\d+\.\d+)\.(\d+)/);
                    li = '<li>{0} {1}</li><p>{2}</p>'.format(data[i]['version'], data[i]['create_time'], data[i]['description']);
                    if (numbers[2] == 0) {
                        li = '{0}<h4>第{1}版发布</h4>'.format(li, numbers[1])
                    }
                    $('#versions').append(li)
                }
            }
        });
    }

    $("input:checkbox").change(function () {
        if ($(this).prop("checked")) {
            $("input:password").attr("type", "text")
        }
        else {
            $("input:text").attr("type", "password")
        }
    });

    $("#update").click(function () {
        username = $('#username').text();
        password = $('#password').val();
        $.ajax({
            url: "help/change_password/",
            data: {"username": username, "password": password},
            type: "post",
            dataType: 'text',
            success: function (data) {
                $.popUp("密码修改成功！", "success");
                $('#password').val('')
            }
        });
    })
});