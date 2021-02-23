$(document).ready(function () {
    {

        $.ajax({
            url: "example/get_examples_user/",
            type: "post",
            dataType: 'json',
            success: function (data) {

                $('#user').DataTable({
                    data: data,
                    columns: [
                        {
                            title: '选择',
                            width: '40px',
                            data: null,
                            defaultContent: "<input type='checkbox'>"
                        },
                        {
                            title: '系统编号',
                            width: '90px',
                            data: 'id'
                        },
                        {
                            title: '用户名称',
                            width: '90px',
                            data: 'username'
                        },
                        {
                            title: '公司名称',
                            width: '150px',
                            data: 'company'
                        },
                        {
                            title: '分组名称',
                            data: 'group_name'
                        },
                        {
                            title: '任务名称',
                            data: 'task_name'
                        },
                        {
                            title: '一级网址',
                            data: 'first_url',
                            width: '350px'
                        },
                        {
                            title: '二级网址',
                            data: 'second_url',
                            width: '350px'
                        },
                        {
                            title: '创建时间',
                            data: 'create_time'
                        },
                        {
                            title: '修改时间',
                            data: 'update_time'
                        },
                    ],
                    info: false,
                    paging: false,
                    order: [[1, 'desc']],
                });
            }
        });
        $.ajax({
            url: "example/get_examples_all/",
            type: "post",
            dataType: 'json',
            success: function (data) {

                $('#all').DataTable({
                    data: data,
                    columns: [
                        {
                            title: '选择',
                            width: '40px',
                            data: null,
                            defaultContent: "<input type='checkbox'>"
                        },
                        {
                            title: '系统编号',
                            width: '90px',
                            data: 'id'
                        },
                        {
                            title: '用户名称',
                            width: '90px',
                            data: 'username'
                        },
                        {
                            title: '公司名称',
                            width: '150px',
                            data: 'company'
                        },
                        {
                            title: '分组名称',
                            data: 'group_name'
                        },
                        {
                            title: '任务名称',
                            data: 'task_name'
                        },
                        {
                            title: '一级网址',
                            data: 'first_url',
                            width: '350px'
                        },
                        {
                            title: '二级网址',
                            data: 'second_url',
                            width: '350px   '
                        },
                        {
                            title: '创建时间',
                            data: 'create_time'
                        },
                        {
                            title: '修改时间',
                            data: 'update_time'
                        },
                    ],
                    info: false,
                    paging: false,
                    order: [[1, 'desc']],
                });
                $('#all_wrapper').hide()
            }
        });
    }

    function find_ids_by_td(limit) {
        limit = limit == undefined ? 'table' : limit;
        var ids = [];
        var $tds = $('input:checkbox:checked', limit).parent().next();
        for (var i = 0; i < $tds.length; i++) {
            ids.push($tds.eq(i).text())
        }
        return ids
    }


    $('#detail').click(function () {
        var id = find_ids_by_td()[0];
        if (id) {
            $.ajax({
                url: "example/get_details/",
                data: {"id": id},
                type: "post",
                dataType: 'json',
                success: function (data) {
                    var fields = '';
                    for (i = 0; i < data.length; i++) {
                        fields = fields + (i + 1) + '.' + data[i] + '\n'
                    }
                    var option = {
                        title: id + " 跳转至【配置页面】？",
                        icon: "-48px 0",
                        btn: parseInt("0011", 2),
                        onOk: function () {
                            window.open("setting.html?id=" + id)
                        }
                    };
                    window.wxc.xcConfirm(fields, confirm, option);
                }
            });
        }
        else {
            $.popUp('未选择任务！', 'warning')
        }
    });

    $('#delete').click(function () {
        if ($('.focus').text() == "所有") {
            $.popUp('分享的模板不能删除！', 'warning')
        }
        else {
            var id = find_ids_by_td('#user')[0];
            if (id) {
                var option = {
                    title: id + " 确认删除此任务？",
                    icon: "0 -96px",
                    btn: parseInt("0011", 2),
                    onOk: function () {
                        $.ajax({
                            url: "example/delete_example/",
                            data: {"id": id},
                            type: "post",
                            dataType: 'text',
                            success: function (data) {
                                location.reload()
                            }
                        });
                    }
                };
                window.wxc.xcConfirm("", confirm, option);
            }
            else {
                $.popUp('未选择任务！', 'warning')
            }
        }
    });

    $('body>aside>button').click(function () {
        $('body>aside>button').removeClass('focus');
        $(this).addClass('focus');
        $('input:checkbox:checked').prop("checked", false);
        switch ($(this).text()) {
            case  '个人':
                $('#user_wrapper').show();
                $('#all_wrapper').hide();
                break;
            case  '所有':
                $('#user_wrapper').hide();
                $('#all_wrapper').show();
                break
        }
    })
});