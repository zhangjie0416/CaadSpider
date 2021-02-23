$(document).ready(function () {

    {
        // 新版本通知
        var username = $.cookie('username')
        var is_read = $.cookie('is_read')
        if (is_read != '1') {
            $.ajax({
                url: "/help/is_read",
                type: "get",
                data: {'username': username},
                dataType: 'json',
                success: function (data) {
                    if (data['is_read'] == '0') {
                        $.ajax({
                            url: "/help/get_versions",
                            type: "get",
                            data: {'username': username, 'version': 'latest'},
                            dataType: 'json',
                            success: function (data) {
                                var version = '版本：{0}\n日期：{1}\n说明：{2}'.format(data[0]['version'], data[0]['create_time'], data[0]['description'])
                                window.wxc.xcConfirm(version, window.wxc.xcConfirm.typeEnum.success, {
                                    onOk: function () {
                                        $.removeCookie('is_read', {path: '/'})
                                        $.cookie('is_read', '1');
                                    }
                                })
                            },
                        });
                    }
                },
            });
        }
    }

    $('#sidebar-trigger img').mouseenter(function () {
        $('header nav').toggle('fast')
    });

    $('#sidebar-nav').mouseleave(function () {
        $('header nav').toggle('fast')
    });

    $('#logout').click(function () {

        $.ajax({
            url: "/help/logout",
            type: "get",
            dataType: 'text',
            success: function (data) {
                location.href = "/login.html"
            },
        });
    });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                var csrftoken = getCookie('csrftoken');
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
});

$(document).ajaxStart(function () {
    $('#loading').show()
});

$(document).ajaxStop(function () {
    $('#loading').hide()
});

$(document).ajaxSuccess(function () {
    $.popUp('请求成功！', 'info', 1)
});

$(document).ajaxError(function () {
    $.popUp('请求失败！', 'error', 1)
})