layui.define(['incetops', 'jquery', 'element'], function(exports) {
    var $ = layui.jquery,
        element = layui.element,
        incetops = layui.incetops;
    var d = {
        autoviewSQLSHA1: incetops.getUrlQuery("sqlsha1s"),
        inception: incetops.getUrlQuery("inception"),
        sqlContent: incetops.getUrlQuery("sqlContent")
    };
    console.log(d);
    var html = ['<div class="layui-card">',
        '<div class="layui-card-header">关于任务：</div>',
        '<div class="layui-card-body">',
        'Incetion: ' + d.inception + '<br>',
        '任务SQL: ' + d.sqlContent + '<br>',
        '所有sqlsha1: ' + d.autoviewSQLSHA1 + '<br>',
        '</div></div>',
        '<div class="layui-card"><div class="layui-card-header">中止OSC注意事项：</div><div class="layui-card-body">1. 在多个ALTER语句一起执行的情况下，如果取消某一个，那么整个执行过程都中止，同时被取消的语句返回是未执行状态。所以在前端实现执行错误再次执行时，这个可以归为未执行的语句<br>2. 在取消语句的错误描述信息中，报错为<code>"Execute has been abort in percent: 已执行比例, remain time: 剩余时间"</code><br>3. 在取消之后，当前语句之后的所有语句不会执行，当然状态为未执行。<br>4. 被取消语句，在取消之后，结果集stagestatus列的信息会设置为<code>"Execute Aborted"</code>。</p></div></div>',
        '<div class="layui-row layui-col-space10">'
    ].join("");
    // 执行中状态查询osc执行进度
    if (d.autoviewSQLSHA1) {
        var sqlsha1s = incetops.strip(d.autoviewSQLSHA1).split(/\s*,\s*/),
            mdnum = 12;
        if (sqlsha1s.length === 1) {
            mdnum = 12
        } else if (sqlsha1s.length === 2) {
            mdnum = 6
        } else if (sqlsha1s.length === 3) {
            mdnum = 4
        } else if (sqlsha1s.length === 4) {
            mdnum = 3
        } else if (sqlsha1s.length === 5) {
            mdnum = 2
        } else if (sqlsha1s.length === 6) {
            mdnum = 2
        } else {
            mdnum = 1
        }
        sqlsha1s.map(function(sqlsha1) {
            var filterId = sqlsha1.replace('*', '');
            layui.cache[filterId] = {
                inception: d.inception,
                percent: 0
            };
            html += ['<div class="layui-col-md' + mdnum + '">',
                '当前SQLSHA1:<code>' + sqlsha1 + '</code>',
                '<br>动作: <button class="layui-btn layui-btn-xs layui-btn-radius layui-btn-danger stoposc" data-sqlsha1="' + sqlsha1 + '">中止</button>',
                '<br>提示: <i>查询进度有时间间隔，根据服务端性能不同，进度条长时间停留在99%(或不足)可能实际上已经完成任务，请注意查看结果。</i><br>剩余时间：<b id="tip_' + filterId + '">等待结果</b>',
                '<div style="top:5px;" class="layui-progress layui-progress-big" lay-showPercent="yes" lay-filter="' + filterId + '"><div class="layui-progress-bar layui-bg-orange" lay-percent="0%"></div></div>',
                '<pre class="layui-code" id="info_' + filterId + '">无数据</pre></div>'
            ].join("");
        });
        if (typeof(layui.cache.sqlsha1s) === "object") {
            sqlsha1s.map(function(sqlsha1) {
                layui.cache.sqlsha1s.push(sqlsha1);
            });
        } else {
            layui.cache.sqlsha1s = sqlsha1s;
        }
        html += '</div>';
    }
    $("#pageContent").html(html);
    //重新渲染进度条
    element.render('progress');
    //监听中止按钮
    $(".stoposc").click(function() {
        var that = this;
        var sqlsha1 = that.getAttribute("data-sqlsha1");
        layer.confirm('确定要中止OSC执行任务吗？<br>前提要求，OSC执行的进程已经创建，且执行进度不到100%方可！', {
            icon: 3,
            title: '温馨提示'
        }, function(index) {
            layer.close(index);
            //向服务端发送删除指令
            incetops.ajax("/IncetOps/api/?Action=TaskStopOSC", function(res) {
                console.log(res.data);
            }, {
                data: {
                    "sqlsha1": sqlsha1,
                    inception: d.inception
                },
                method: "post"
            });
        });
    });
    //定时从缓存中获取sqlsha1列表查询并更新进度
    setInterval(function() {
        if (typeof(layui.cache.sqlsha1s) === "object") {
            layui.cache.sqlsha1s.map(function(sqlsha1) {
                var filterId = sqlsha1.replace('*', '');
                var sqlcache = layui.cache[filterId];
                if (sqlcache.percent < 100) {
                    incetops.ajax("/IncetOps/api/?Action=TaskQueryOSC", function(res) {
                        console.log(res);
                        layui.cache[filterId].percent = res.data.PERCENT;
                        element.progress(filterId, res.data.PERCENT + '%');
                        $("#tip_" + filterId + "").text(res.data.REMAINTIME);
                        $("#info_" + filterId + "").text(res.data.INFOMATION);
                    }, {
                        data: {
                            "sqlsha1": sqlsha1,
                            "inception": sqlcache.inception
                        },
                        method: "post",
                        msgprefix: false
                    });
                }
            });
        }
    }, 500);
    exports("OSC", null);
});