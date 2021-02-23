//扩展方法
$.extend({
    popUp: function (text, type, second = 2) {
        var types = {
            'info': {'background': "#90c24f"},
            'warning': {'background': "#f99e2b"},
            'error': {'background': "#f06a6a"}
        }
        var perfix = {
            'info': '通知',
            'warning': '警告',
            'error': '错误'
        }
        type = type in types ? type : 'info'
        $p = $('<p class="popup"></p>').text('{0}：{1}'.format(perfix[type], text)).css({
            'color': 'white',
            'width': '400px',
            'z-index': '5',
            'height': '50px',
            'line-height': '50px',
            'text-align': 'center',
            'position': 'fixed',
            'top': '50px',
            'left': '50%',
            'margin': '3px',
            'margin-left': '-200px',
            'border-radius': '5px'
        }).css(types[type]);
        $('body').append($p);
        setTimeout(() => $('p.popup').remove(), parseInt(second) * 1000)
    },
});

// 扩展方法的属性
$.fn.extend({
    insertContent: function (myValue, t) {
        var $t = $(this)[0];
        if (document.selection) { // ie
            this.focus();
            var sel = document.selection.createRange();
            sel.text = myValue;
            this.focus();
            sel.moveStart('character', -l);
            var wee = sel.text.length;
            if (arguments.length == 2) {
                var l = $t.value.length;
                sel.moveEnd("character", wee + t);
                t <= 0 ? sel.moveStart("character", wee - 2 * t - myValue.length) : sel.moveStart("character", wee - t - myValue.length);
                sel.select();
            }
        } else if ($t.selectionStart
            || $t.selectionStart == '0') {
            var startPos = $t.selectionStart;
            var endPos = $t.selectionEnd;
            var scrollTop = $t.scrollTop;
            $t.value = $t.value.substring(0, startPos)
                + myValue
                + $t.value.substring(endPos, $t.value.length);
            this.focus();
            $t.selectionStart = startPos + myValue.length;
            $t.selectionEnd = startPos + myValue.length;
            $t.scrollTop = scrollTop;
            if (arguments.length == 2) {
                $t.setSelectionRange(startPos - t,
                    $t.selectionEnd + t);
                this.focus();
            }
        } else {
            this.value += myValue;
            this.focus();
        }
    }
})

// 扩展数据的属性
String.prototype.format = function (args) {
    var result = this;
    if (arguments.length > 0) {
        if (arguments.length == 1 && typeof (args) == "object") {
            for (var key in args) {
                if (args[key] != undefined) {
                    // noinspection Annotator
                    var reg = new RegExp("({" + key + "})", "g");
                    result = result.replace(reg, args[key]);
                }
            }
        }
        else {
            for (var i = 0; i < arguments.length; i++) {
                if (arguments[i] != undefined) {
                    // noinspection Annotator
                    var reg = new RegExp("({[" + i + "]})", "g");
                    result = result.replace(reg, arguments[i]);
                }
            }
        }
    }
    return result;
}

String.prototype.args = function () {
    var args = location.search.slice(1);
    var list = args.split('&'), dict = {};
    for (var i = 0; i < list.length; i++) {
        var item = list[i].split('=');
        dict[item[0]] = item[1]
    }
    return dict
}

$(document).ajaxSuccess(function () {
    $.popUp('请求成功！', 'info', 1)
});

$(document).ajaxError(function () {
    $.popUp('请求失败！', 'error', 1)
})