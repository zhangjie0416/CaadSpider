$(document).ready(function () {
    {
        $('nav a').attr('target', '_blank');
        $('.content').eq(2).height($('.content').eq(0).height() - 28);
        $('.content').setTextareaCount({
            width: "30px",
            bgColor: "#20B2AA",
            color: "#2c3e50",
            display: "inline-block"
        });
        resize();
        get_setting()
    }


    //当文档窗口发生改变时 触发
    $(window).resize(function () {
        resize()
    });

    function resize() {
        var width_section = $("section").eq(1).width();
        var width_button = $('#get_html').outerWidth();
        var width_space = 20;
        var width_input = width_section - width_button - width_space;
        $('input:text').width(width_input);
        $('#group_name').width(250);
        $('#task_name').width(250);
        $('#url').width(width_input - width_button - 8);
        $("textarea").width(width_input - 27);
        $("textarea[id='html']").width(width_input);
    }

    //弹出正确提示框
    function alert_success(txt) {
        window.wxc.xcConfirm(txt, window.wxc.xcConfirm.typeEnum.success, {
            onOk: function () {
            }
        })
    }

    var hide_line = "......省略";

    function by(property) {
        return function (a, b) {
            return a[property] - b[property];
        }
    }

    function get_setting() {
        var args = location.search;
        if (args.indexOf("id") > -1) {
            var id = args.match(/\d+/)[0];
            $.ajax({
                url: "/spider/setting/get_setting/",
                data: {"id": id},
                type: "get",
                dataType: 'json',
                success: function (data) {

                    if (data['username'] == $.cookie('username')) {
                        if (data['is_example'] == '1') {
                            $('#save_task').hide()
                        }
                        else {
                            $('#save_example').hide()
                        }
                    }
                    else {
                        $('#save_example,#save_task').hide()
                    }
                    $('#group_name').val(data['group_name']);
                    $('#task_name').val(data['task_name']);
                    if (data['is_full'] == '1') $('input:radio[value=1]').attr('checked', 'checked');
                    $('#first_urls').val(data['first_urls']);
                    $('#urls_xpath').val(data['urls_xpath']);

                    $('#timer').val(data['timer']);
                    $('#first_url').val(data['first_url']);
                    $('#second_url').val(data['second_url']);
                    var json = JSON.parse(data['data_xpath']);
                    var fields = '';
                    /*固定采集*/
                    var fix_fields = json['fix_fields'].sort(by('seq'));
                    for (i = 0; i < fix_fields.length; i++) {
                        fields = '{0}"{1}":"{2}"\n'.format(fields, fix_fields[i]['field'], fix_fields[i]['xpath'])
                    }
                    $('.content').eq(0).val(fields);
                    fields = '';
                    /*单条采集*/
                    var one_fields = json['one_fields'].sort(by('seq'));
                    for (i = 0; i < one_fields.length; i++) {
                        fields = '{0}"{1}":"{2}"\n'.format(fields, one_fields[i]['field'], one_fields[i]['xpath'])
                    }
                    $('.content').eq(1).val(fields);
                    fields = '', orders = '';
                    /*多条采集*/
                    var all_fields = json['all_fields'].sort(by('seq'));
                    for (i = 0; i < all_fields.length; i++) {
                        fields = '{0}"{1}":"{2}"\n'.format(fields, all_fields[i]['field'], all_fields[i]['xpath'])
                    }
                    $('.content').eq(2).val(fields);
                    $('#fields_setting input').val(json['all_xpath'])
                }
            });
        }
        else {
            $('#save_example,#save_task').hide()
        }
    }

    $('#fields_setting > img').click(function () {
        /*幻灯片->左-1，右1*/
        var order = $(this).index() == 3 ? -1 : 1;
        var index = $('#fields_setting div.foucs_show').index();
        $('#fields_setting>div').removeClass('foucs_show');
        var new_index = order + index;
        if (new_index == 3) {
            new_index = 0
        }
        else {
            if (new_index == -1) {
                new_index = 2
            }
        }
        $('#fields_setting>div').eq(new_index).addClass('foucs_show')
    });

    $('#get_first_urls').click(function () {
            var url = $('#first_urls').val();
            if (url.match(/[{}]/g) != null && url.match(/[{}]/g).length % 2 == 1) {
                $.popUp("例如：{1-100},{北京,上海,广州,深圳}", "error");
            }
            else {
                $.ajax({
                    url: "/spider/setting/get_first_urls/",
                    data: {"url": url},
                    type: "post",
                    dataType: 'json',
                    success: function (data) {
                        alert_success(data.join('\n'));
                    }
                });
            }
        }
    );

    $('#get_urls').click(function () {
        var url = $("#first_url").val();
        var xpath = $("#urls_xpath").val();
        $.ajax({
            url: "/spider/setting/get_urls/",
            data: {"url": url, "xpath": xpath},
            type: "post",
            dataType: 'json',
            success: function (data) {
                alert_success(data.join('\n'));
            }
        });
    });

    $('#get_fields').click(function () {
        var url = $("#second_url").val();
        var data_xpath = fields2json();
        if (data_xpath == '{}') return;
        $.ajax({
            url: "/spider/setting/get_fields/",
            data: {"url": url, "xpath": data_xpath},
            type: "post",
            dataType: 'json',
            success: function (data) {
                var list = [];
                var fields = get_fields();
                for (i = 0; i < data.length; i++) {
                    list.push(i + 1);
                    for (j = 0; j < fields.length; j++) {
                        list.push('"{0}":{1}'.format(fields[j], data[i][fields[j]]))
                    }
                }
                alert_success(list.join('\n'));
            }
        });
    });

    $('#get_html').click(function () {
        var url = $("#url").val();
        url = url.search(/http/) == 0 ? url : 'http://' + url;
        $("#url").val(url);
        url = 'http://172.16.2.82:10012/download?url={0}'.format(encodeURIComponent(url));
        window.open(url, '_blank');
    });

    $('#save_html').click(function () {
        var url = $('#url').val().trim();
        var html = $('#html').val().replace(/\s+/g, ' ').trim();
        if (url && html) {
            $.ajax({
                url: "/spider/setting/save_html/",
                data: {"url": url, "html": html},
                type: "post",
                dataType: 'text',
                success: function (data) {
                    $.popUp("缓存成功，1小时之内有效！", "success")
                }
            });
        }
        else {
            $.popUp("未添加网址或源码！", "error")
        }
    });

    $('#save_example,#save_task,#save_as_example,#save_as_task').click(function () {
        var args = location.search.slice(1).args()
        var id = args['id'] == undefined ? 0 : args['id']
        var setting = {};
        setting["id"] = id;

        setting["group_name"] = $("#group_name").val();
        setting["task_name"] = $("#task_name").val();
        setting['is_full'] = $('input:radio:checked').attr('value');
        setting["first_urls"] = $("#first_urls").val();
        setting["urls_xpath"] = $("#urls_xpath").val().replace('\\', '\\\\');
        setting["data_xpath"] = fields2json();

        setting["timer"] = $('#timer').val();
        setting["first_url"] = $('#first_url').val();
        setting['second_url'] = $('#second_url').val();
        if (setting["group_name"] == '' || setting["task_name"] == '') {
            $.popUp("分组名称和任务名称不能为空！", "error")
            return
        }
        if (setting["data_xpath"] == '{}') return;
        var url = '';
        switch ($(this)[0].id) {
            case 'save_example':
                setting["is_example"] = 1;
                url = "/spider/setting/save_setting/";
                break;
            case 'save_task':
                setting["is_example"] = 0;
                url = "/spider/setting/save_setting/";
                break;
            case 'save_as_example':
                setting["is_example"] = 1;
                url = "/spider/setting/save_as_setting/";
                break;
            case 'save_as_task':
                setting["is_example"] = 0;
                url = "/spider/setting/save_as_setting/";
                break
        }
        $.ajax({
            url: url,
            data: {"setting": JSON.stringify(setting)},
            type: "post",
            dataType: 'text',
            success: function (data) {
                var option = {
                    title: data,
                    icon: "-48px 0",
                    btn: parseInt("0011", 2),
                    onOk: function () {
                        var id = data.search(/\d+/);
                        if (id > -1) {
                            location.href = "/spider/setting.html?id=" + data.match(/\d+/)[0]
                        }
                    }
                };
                window.wxc.xcConfirm('', confirm, option);
            }
        });
    });

    function fields2json() {
        var fields = {};
        var fix_fields = $('.content').eq(0).val().replace(/\s+\n/g, '\n').split('\n').filter(item => item);
        var one_fields = $('.content').eq(1).val().replace(/\s+\n/g, '\n').split('\n').filter(item => item);
        var all_fields = $('.content').eq(2).val().replace(/\s+\n/g, '\n').split('\n').filter(item => item);
        var all_xpath = $('#fields_setting input').val();

        var fix_fields_list = [], one_fields_list = [], all_fields_list = [];

        /*固定采集*/
        for (i = 0; i < fix_fields.length; i++) {
            var fix_field = {};
            // noinspection Annotator
            var row = fix_fields[i].match(/"(.*?)":"(.*)"/);
            fix_field['seq'] = i;
            fix_field['field'] = row[1];
            fix_field['xpath'] = row[2];
            fix_fields_list.push(fix_field)
        }
        fields['fix_fields'] = fix_fields_list;
        /*单条采集*/
        for (i = 0; i < one_fields.length; i++) {
            var one_field = {};
            // noinspection Annotator
            var row = one_fields[i].match(/"(.*?)":"(.*)"/);
            one_field['seq'] = i;
            one_field['field'] = row[1];
            one_field['xpath'] = row[2];
            // 校验xpath，[.*]不能超过2个
            if (one_field['xpath'].split('.*').length > 3) {
                $.popUp('"{0}"中的.*超过2个！'.format(one_field['field']), 'error');
                return '{}'
            }
            one_fields_list.push(one_field)
        }
        fields['one_fields'] = one_fields_list;
        /*多条采集*/
        for (i = 0; i < all_fields.length; i++) {
            var all_field = {};
            var row = all_fields[i].match(/"(.*?)":"(.*)"/);
            all_field['seq'] = i;
            all_field['field'] = row[1];
            all_field['xpath'] = row[2];
            all_fields_list.push(all_field)
        }
        fields['all_fields'] = all_fields_list;
        fields['all_xpath'] = all_xpath;
        return JSON.stringify(fields)
    }

    function get_fields() {
        var fields = [];
        var fix_fields = $('.content').eq(0).val().replace(/\s+\n/g, '\n').split('\n').filter(item => item);
        var one_fields = $('.content').eq(1).val().replace(/\s+\n/g, '\n').split('\n').filter(item => item);
        var all_fields = $('.content').eq(2).val().replace(/\s+\n/g, '\n').split('\n').filter(item => item);
        /*固定采集*/
        for (i = 0; i < fix_fields.length; i++) {
            // noinspection Annotator
            var row = fix_fields[i].match(/"(.*?)":"(.*)"/);
            fields.push(row[1])
        }
        /*单条采集*/
        for (i = 0; i < one_fields.length; i++) {
            // noinspection Annotator
            var row = one_fields[i].match(/"(.*?)":"(.*)"/);
            fields.push(row[1])
        }
        /*多条采集*/
        for (i = 0; i < all_fields.length; i++) {
            // noinspection Annotator
            var row = all_fields[i].match(/"(.*?)":"(.*)"/);
            fields.push(row[1])
        }
        return fields
    }

    $(".shortcut").click(function () {
        $(".foucs_show textarea").insertContent($(this).attr('value'));
    });

    $('#first_urls').click(function () {
        var $this = $(this);
        try {
            var txt = JSON.parse($this.val()).join('\n')
        }
        catch {
            var txt = $this.val()
        }
        window.wxc.xcConfirm(txt, window.wxc.xcConfirm.typeEnum.input, {
            onOk: function () {
                var lines = $('.xcConfirm textarea').val().replace(/\s+\n/g, '\n').split('\n').filter(item => item);
                $this.val(JSON.stringify(lines))
            }
        });
        $('.xcConfirm textarea').removeAttr('disabled').css({
            'padding': '0px 5px',
            'border': '1px solid gray',
            'outline': 'none'
        })
    });
});