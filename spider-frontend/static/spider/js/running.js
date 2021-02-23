$(document).ready(function () {
    {
        var month_ago = new Date(new Date().getTime() - 60 * 60 * 24 * 7 * 1000).toISOString().substring(0, 10)
        $('#from_date').val(month_ago);
        $('#from_date').hide()
        show_start()
        show_stop(month_ago)
    }

    function show_start(from_date = '1900-01-01') {
        $.ajax({
            url: "running/get_start_list/",
            type: "post",
            data: {'from_date': from_date},
            dataType: 'json',
            success: function (data) {
                $('section').append($('<table id="start" class="display" cellspacing="0" width="100%"></table>'))
                $('#start').DataTable({
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
                            width: '80px',
                            data: 'id'
                        },
                        {
                            title: '用户名称',
                            width: '80px',
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
                            title: '采集方式',
                            width: '80px',
                            data: 'is_full',
                            render: function (data) {
                                return data == '0' ? '增量' : '全量'
                            }
                        },
                        {
                            title: '创建时间',
                            data: 'create_time'
                        },
                        {
                            title: '修改时间',
                            data: 'update_time'
                        },
                        {
                            title: '开始',
                            width: '35px',
                            data: null,
                            defaultContent: '',
                            className: 'button_start',
                        },
                        {
                            title: '结束',
                            width: '35px',
                            data: null,
                            defaultContent: '',
                            className: 'button_stop'
                        },
                        {
                            title: '开始时间',
                            data: 'begin_time'
                        },
                        {
                            title: '结束时间',
                            data: 'finish_time'
                        },
                        {
                            title: '采集进度',
                            data: 'progress',
                            className: 'progress'
                        },
                        {
                            title: '定时/天',
                            width: '80px',
                            data: 'timer'
                        }
                    ],
                    stripeClasses: "",
                    columnDefs: [
                        {
                            orderable: false,
                            targets: [0, 9, 10]
                        }
                    ],
                    info: false,
                    paging: false,
                    order: [[1, 'desc']]
                });
                $('.button_start', '#start').css("opacity", 1);
                $('.button_stop', '#start').click(function () {
                    var id = $(this).siblings().eq(1).text();
                    var status = 0;
                    var url = 'running/stop_running/';
                    start_stop(id, status, url)
                })
                $('.progress', '#start').each(function () {
                    var progess = $(this).text().match(/[^%]+/)[0]
                    $(this).css({'background-size': '{0}% 100%'.format(progess), 'background-repeat': 'no-repeat'})
                })
            }
        });
    }

    function show_stop(from_date, hide = true) {
        $.ajax({
            url: "running/get_stop_list/",
            type: "post",
            data: {'from_date': from_date},
            dataType: 'json',
            success: function (data) {
                $('section').append($('<table id="stop" class="display" cellspacing="0" width="100%"></table>'))
                $('#stop').DataTable({
                    data: data,
                    columns: [
                        {
                            title: '选择',
                            width: '40px',
                            defaultContent: "<input type='checkbox'>"
                        },
                        {
                            title: '系统编号',
                            width: '80px',
                            data: 'id'
                        },
                        {
                            title: '用户名称',
                            width: '80px',
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
                            title: '采集方式',
                            width: '80px',
                            data: 'is_full',
                            render: function (data) {
                                return data == '0' ? '增量' : '全量'
                            }
                        },
                        {
                            title: '创建时间',
                            data: 'create_time'
                        },
                        {
                            title: '修改时间',
                            data: 'update_time'
                        },
                        {
                            title: '开始',
                            width: '35px',
                            defaultContent: '',
                            className: 'button_start',
                        },
                        {
                            title: '结束',
                            width: '35px',
                            defaultContent: '',
                            className: 'button_stop'
                        },
                        {
                            title: '开始时间',
                            data: 'begin_time'
                        },
                        {
                            title: '结束时间',
                            data: 'finish_time'
                        },
                        {
                            title: '采集进度',
                            data: 'progress',
                            className: 'progress'
                        },
                        {
                            title: '定时/天',
                            width: '80px',
                            data: 'timer'
                        }
                    ],
                    stripeClasses: "",
                    columnDefs: [
                        {
                            orderable: false,
                            targets: [0, 9, 10]
                        }
                    ],
                    info: false,
                    paging: false,
                    order: [[1, 'desc']],
                });
                $('.button_stop', '#stop').css("opacity", 1);
                $('.button_start', '#stop').click(function () {
                    var id = $(this).siblings().eq(1).text();
                    var status = 1;
                    var url = 'running/start_running/';
                    start_stop(id, status, url)
                });
                $('.progress', '#stop').each(function () {
                    var progess = $(this).text().match(/[^%]+/)[0]
                    $(this).css({'background-size': '{0}% 100%'.format(progess), 'background-repeat': 'no-repeat'})
                })
                if (hide) $('#stop_wrapper').hide()
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

    $('#from_date').change(function () {
        var from_date = $('#from_date').val()
        $('#stop_wrapper').remove()
        show_stop(from_date, hide = false)
    })

    $('#detail').click(function () {
        var id = find_ids_by_td()[0];
        if (id) {
            $.ajax({
                url: "running/get_details/",
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


    $('#export').click(function () {
        var ids = find_ids_by_td();
        if (ids.length > 0) {
            var option = {
                title: " 跳转至【采集-导出页面】？",
                icon: "-48px 0",
                btn: parseInt("0011", 2),
                onOk: function () {
                    window.open("export.html?id=" + ids.toString())
                }
            };
            window.wxc.xcConfirm("", confirm, option);
        }
        else {
            $.popUp('未选择任务！', 'warning')
        }
    });

    $('#delete').click(function () {
        var id = find_ids_by_td()[0];
        if (id) {
            var option = {
                title: id + " 确认删除此任务？",
                icon: "0 -96px",
                btn: parseInt("0011", 2),
                onOk: function () {
                    $.ajax({
                        url: "running/delete_running/",
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
    });

    $('#log_url,#log_field').click(function () {
        var id = find_ids_by_td()[0];
        if (id) {
            var type = $(this)[0].id == 'log_url' ? 'urls' : 'data';
            $.ajax({
                url: "http://172.16.2.82:10010/spider_logs/select_logs?id={0}&type={1}".format(id, type),
                type: "get",
                dataType: 'json',
                success: function (data) {
                    var log = "";
                    for (var i = 0; i < data.length; i++) {
                        log = log + JSON.stringify(data[i]).replace(/\\"/g, '') + '\n'
                    }
                    show_log();
                    $('#popup textarea').text(log)
                }
            });
        }
        else {
            $.popUp('未选择任务！', 'warning')
        }
    });

    $('#check_all').click(function () {
        var table = $('#start_wrapper').is(':hidden') ? '#stop' : '#start'
        if ($(this).prop("checked")) {
            $('input:checkbox', table).prop("checked", true);
        }
        else {
            $('input:checkbox', table).prop("checked", false);
        }

    })

    $('#more_start').click(function () {
        var id = find_ids_by_td('#stop').toString();
        var status = 1;
        var url = 'running/start_running/';
        if (id.length > 0) {
            start_stop(id, status, url)
        }
        else {
            $.popUp('未选择任务！', 'warning')
        }
    });

    $('#more_stop').click(function () {
        var id = find_ids_by_td('#start').toString();
        var status = 0;
        var url = 'running/stop_running/';
        if (id.length > 0) {
            start_stop(id, status, url)
        }
        else {
            $.popUp('未选择任务！', 'warning')
        }
    });

    $('#more_timer').click(function () {
        var ids = find_ids_by_td().toString();
        if (ids.length > 0) {
            var txt = '0'
            window.wxc.xcConfirm(txt, window.wxc.xcConfirm.typeEnum.custom, {
                title: '定时',
                icon: "-48px 0",
                btn: window.wxc.xcConfirm.btnEnum.okcancel,
                onOk: function () {
                    var timer = parseInt($('.xcConfirm textarea').val())
                    if (ids.length > 0) {
                        $.ajax({
                            url: 'running/update_timers/',
                            type: "post",
                            data: {'id': ids, 'timer': timer},
                            dataType: 'json',
                            success: function (data) {
                                location.reload();
                            }
                        });
                    }
                }
            });
            $('.xcConfirm textarea').removeAttr('disabled').css({
                'padding': '0px 5px',
                'border': '1px solid gray',
                'outline': 'none'
            })
        }
        else {
            $.popUp('未选择任务！', 'warning')
        }
    })

    function start_stop(id, status, url) {
        $.ajax({
            url: url,
            data: {"id": id, "status": status},
            type: "post",
            dataType: 'text',
            success: function (data) {
                location.reload();
            }
        });
    }

    $('#popup .title span').click(function () {
        show_log()
    });

    function show_log() {
        $('#popup').css({
            left: ($(window).width() - $('#popup').width()) / 2,
        }).toggle();
        $('#mask_shadow').toggle()
    }

    $('body>aside>button').click(function () {
        $('body>aside>button').removeClass('focus');
        $(this).addClass('focus');
        $('input:checkbox:checked').prop("checked", false);
        switch ($(this).text()) {
            case  '运行':
                $('#start_wrapper,#reload').show();
                $('#stop_wrapper,#from_date').hide();
                break;
            case  '结束':
                $('#start_wrapper,#reload').hide();
                $('#stop_wrapper,#from_date').show();
                break
        }
    })
    var timer = null
    $('#reload').click(function () {
        if ($(this).prop('value') == '1') {
            $(this).text('关闭(5s)')
            $(this).prop('value', '0')
            timer = setInterval(function () {
                $('#start_wrapper').remove()
                show_start()
            }, 5000)
        }
        else {
            $(this).text('刷新(5s)')
            $(this).prop('value', '1')
            clearInterval(timer)
        }
    })
});