$(document).ready(function () {
    {
        var date = new Date();
        $('#begin_date').val(date.toISOString().substring(0, 8) + '01');
        $('#end_date').val(date.toISOString().substring(0, 10));
        $('section').width($(window).width() - 20);
        show_data()
    }

    function show_data() {
        begin_date = $('#begin_date').val() + ' 00:00:00';
        end_date = $('#end_date').val() + ' 23:59:59';
        var url = location.search;
        if (url.indexOf("id") > -1) {
            var id = url.match(/\d+/)[0];

            $.ajax({
                url: "export/show_data/",
                type: "post",
                data: {"id": id, "begin_date": begin_date, "end_date": end_date},
                dataType: "json",
                success: function (data) {

                    $('#table').html('');
                    if (data.length > 0) {
                        var table = '<table id="export" class="display" cellspacing="0"></table>';
                        $('#table').html(table);
                        // $('section').append(table)
                        var columns = [];
                        for (var key in data[0]) {
                            columns.push({"title": key, "data": key})
                        }
                        var json = {"data": data, "columns": columns};
                        $('#export').DataTable({
                            data: json["data"],
                            columns: json["columns"],
                            pageLength: 20,
                            lengthChange: false,
                            info: false,
                            order: [[0, 'desc']],
                        });
                        $('table').css({
                            'margin': '0',
                            'word-break': 'keep-all',
                            'white-space': 'nowrap',
                            'table-layout': 'auto'
                        })
                    }
                }
            })
        }
    }

    $('#search').click(function () {
        show_data()
    });

    $('#download').click(function () {
        begin_date = $('#begin_date').val() + ' 00:00:00';
        end_date = $('#end_date').val() + ' 23:59:59';
        var args = location.search.slice(1).args()
        var id = args['id']
        window.location.href = 'export/download_data' + '?id=' + id + '&begin_date=' + begin_date + '&end_date=' + end_date;
    });

    $('#table').scroll(function () {
        $('#export_wrapper').width($('section').width() + $('#table')[0].scrollLeft)
    })
});
