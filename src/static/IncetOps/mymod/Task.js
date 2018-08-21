layui.define(['incetops', 'form', 'layer', 'table', 'util', 'laydate'], function(exports) {
    var $ = layui.jquery,
        util = layui.util,
        form = layui.form,
        layer = layui.layer,
        table = layui.table,
        laydate = layui.laydate,
        incetops = layui.incetops;
    //数据库列表参数
    var tableOptions = {
        elem: '#taskList',
        url: '/IncetOps/api/?Action=TaskGetList',
        page: true, //开启分页
        cellMinWidth: 30,
        loading: true,
        cols: [
            [{
                type: "checkbox",
                fixed: "left",
                width: 50
            }, {
                field: 'taskId',
                title: '任务ID',
                width: 80,
                sort: true,
                align: "center"
            }, {
                field: 'taskSd',
                title: '任务描述',
                width: 150,
                align: 'center'
            }, {
                field: 'inception',
                title: 'Inception服务',
                width: 150,
                align: 'center'
            }, {
                field: 'dbId',
                title: 'MySQL实例',
                width: 200,
                align: 'center',
                templet: function(d) {
                    return '<scan title="' + d.dbSd + '">mysql://' + d.host + ':' + d.port + ':' + d.user + '</scan>';
                }
            }, {
                field: 'status',
                title: '状态',
                align: 'center',
                width: 200,
                templet: function(d) {
                    var text = d.statusMsg ? '<i class="saintic-icon saintic-icon-info" style="font-size:14px" title="' + d.statusMsg + '"></i>' : '';
                    switch (d.status) {
                        case 0:
                            text += '<span class="layui-badge layui-bg-green">执行成功</span>';
                            break;
                        case 1:
                            text += '<span class="layui-badge">自动审核失败</span>';
                            break;
                        case 2:
                            text += '<span class="layui-badge layui-bg-blue">人工审核中</span>';
                            break;
                        case 3:
                            text += '<span class="layui-badge layui-badge-orange">执行中</span>';
                            break;
                        case 4:
                            text += '<span class="layui-badge">执行异常</span>';
                            break;
                        case 5:
                            text += '<span class="layui-badge layui-bg-gray">已取消</span>';
                            break;
                        case 6:
                            text += '<span class="layui-badge layui-bg-black">已驳回</span>';
                            break;
                        case 7:
                            text += '<span class="layui-badge layui-bg-cyan">定时至' + util.toDateString((d.ctime + d.timer) * 1000) + '</span>';
                            break;
                    }
                    return text;
                }
            }, {
                field: 'sqlContent',
                title: 'SQL语句',
                align: 'center',
                minWidth: 300
            }, {
                title: '忽略警告|启用备份',
                align: 'center',
                width: 150,
                unresize: true,
                templet: function(d) {
                    var iw = d.enableIgnoreWarnings === 1 ? "checked" : "";
                    var rb = d.enableRemoteBackup === 1 ? "checked" : "";
                    return '<scan title="是否忽略警告信息：&#13;ON表示忽略警告&#13;OFF表示不忽略警告，遇到警告停止执行。"><input type="checkbox" lay-skin="switch" lay-text="ON|OFF" disabled ' + iw + '></scan>' + '&nbsp;<scan title="是否开启远程备份：&#13;ON表示启用远程备份，将会产生回滚的SQL语句。&#13;OFF表示禁用远程备份"><input type="checkbox" lay-skin="switch" lay-text="ON|OFF" disabled ' + rb + '></scan>';
                }
            }, {
                title: '动作',
                width: 140,
                toolbar: '#taskListBar',
                fixed: "right",
                align: "center"
            }]
        ],
        done: function(res, curr, count) {
            var taskId = parseInt(incetops.getUrlQuery("taskId"));
            if (taskId) {
                for (var i = 0; i < res.data.length; i++) {
                    if (res.data[i].taskId === taskId) {
                        res.data[i]["LAY_CHECKED"] = true;
                        var index = res.data[i]['LAY_TABLE_INDEX'];
                        $('.layui-table-fixed-l tr[data-index=' + index + '] input[type="checkbox"]').prop('checked', true);
                        $('.layui-table-fixed-l tr[data-index=' + index + '] input[type="checkbox"]').next().addClass('layui-form-checked');
                    }
                }
            }
        }
    };
    //初始化渲染表格
    table.render(tableOptions);
    //列表操作
    table.on('tool(taskList)', function(obj) {
        var layEvent = obj.event,
            data = obj.data;
        if (layEvent === 'detail') { //查看
            var method = data.timer > 0 ? '定时执行' : '普通执行';
            var ftime = data.ftime > 0 ? '于' + util.toDateString(data.ftime * 1000) + '开始执行' : '未执行';
            var content = ['<table class="layui-table"><colgroup><col width="120"><col width="450"><col></colgroup><tbody>',
                '<tr><td>执行方式</td><td>' + method + '</td></tr>',
                '<tr><td>申请人</td><td>' + data.applicant + "于" + util.toDateString(data.ctime * 1000) + '申请</td></tr>',
                '<tr><td>SQL语句</td><td>' + data.sqlContent + '</td></tr>',
                '<tr><td>SQLSHA1</td><td><kbd>' + data.autoviewSQLSHA1 + '</kbd></td></tr>',
                '<tr><td>自动审核结果</td><td><pre id="autoviewResult">' + incetops.syntaxHighlight(JSON.parse(data.autoviewResult)) + '</pre></td></tr>',
                '<tr><td>执行结果</td><td><pre id="executeResult">' + incetops.syntaxHighlight(JSON.parse(data.executeResult)) + '</pre></td></tr>',
                '<tr><td>执行时间</td><td>' + ftime + '</td></tr>',
                '</tbody></table>'
            ].join("");
            layer.open({
                type: 1,
                skin: 'layui-layer-molv', //样式类名
                shade: 0,
                shadeClose: true,
                maxmin: true,
                area: ['570px', '560px'],
                title: "任务ID-" + data.taskId + "：" + data.taskSd,
                content: content
            });
        } else if (layEvent === 'osc') {
            layer.open({
                type: 2,
                title: 'OSC执行进度查询',
                shadeClose: true,
                shade: false,
                maxmin: true, //开启最大化最小化按钮
                area: ['893px', '600px'],
                content: '/IncetOps/task?View=TaskOSC&sqlsha1s=' + data.autoviewSQLSHA1 + '&inception=' + data.inception + '&sqlContent=' + data.sqlContent,
                success: function(layero, index) {
                    layer.full(index);
                }
            });
        } else if (layEvent === 'rollback') {
            layer.prompt({
                formType: 0,
                title: '请输入任务中Inception的备份库地址',
                value: 'default',
            }, function(value, index, elem) {
                if (value != "default") {
                    value += ":";
                } else {
                    value = "";
                }
                incetops.ajax("/IncetOps/api/?Action=TaskRollback", function(res) {
                    layer.close(index);
                    //已经获取回滚语句，表格展示
                    var content = ['<table class="layui-table"><colgroup><col width="135"><col width="150"><col><col><col></colgroup>',
                        '<thead><tr><th>唯一序号</th><th>备份库</th><th>SQL语句</th><th>回滚语句</th><th>错误信息</th></tr></thead><tbody>'
                    ].join("");
                    content += res.data.map(function(row) {
                        var rollback = row.rollback || '';
                        return ['<tr>',
                            '<td>' + row.opid_time + '</td>',
                            '<td>' + row.backup_dbname + '</td>',
                            '<td>' + row.sql + '</td>',
                            '<td>' + rollback.replace("\n", "<br>") + '</td>',
                            '<td>' + row.errmsg + '</td>',
                            '</tr>'
                        ].join("");
                    });
                    content += '</tbody></table>';
                    layer.open({
                        type: 1,
                        skin: 'layui-layer-molv', //样式类名
                        shade: 0,
                        shadeClose: true,
                        maxmin: true,
                        area: ['560px', '400px'],
                        title: "任务ID-" + data.taskId + "的回滚语句",
                        content: content,
                        success: function(layero, index) {
                            layer.full(index);
                        }
                    });
                }, {
                    data: {
                        taskId: data.taskId,
                        backup_mysql_url: value
                    },
                    method: "post"
                });
            });
        } else if (layEvent === 'cancel') {
            layer.confirm('确定要取消当前定时执行的任务吗？', {
                icon: 3,
                title: '温馨提示',
                shade: 0
            }, function(index) {
                incetops.ajax("/IncetOps/api/?Action=TaskCancel", function(res) {
                    layer.close(index);
                    // 重载表格数据
                    table.reload("taskList", tableOptions);
                }, {
                    data: {
                        taskId: data.taskId
                    },
                    method: "delete"
                });
            });
        }
    });
    //监听添加数据库服务弹出表单
    var addTaskIndex;
    $(".addTaskBtn").click(function() {
        layer.open({
            type: 1,
            title: "添加任务",
            content: ['<div style="padding: 10px;"><form class="layui-form layui-form-pane">',
                '<div class="layui-form-item"><input class="layui-input" name="sd" placeholder="任务描述信息" value="" type="text" lay-verify="required"></div>',
                '<div class="layui-form-item"><input class="layui-input" name="applicant" placeholder="申请人" value="" type="text" lay-verify="required" list="applicant"><datalist id="applicant"></datalist></div>',
                '<div class="layui-form-item"><select id="dbOptions" name="dbId" lay-filter="db" lay-verify="required"><option value="">请选择MySQL实例</option></select></div>',
                '<div class="layui-form-item"><select id="inceptionOptions" name="inception" lay-filter="inception" lay-verify="required"><option value="">请选择Inception服务</option></select></div>',
                '<div class="layui-form-item layui-form-text"><textarea name="sqlContent" placeholder="请输入SQL语句" class="layui-textarea" lay-verify="required"></textarea></div>',
                '<div class="layui-form-item pane="">',
                '<div class="layui-inline"><label class="layui-form-label">开启备份</label><div class="layui-input-inline"><input type="checkbox" name="enableRemoteBackup" value=1 lay-skin="switch" lay-text="是|否" checked="" lay-filter="enableRemoteBackup"></div></div>',
                '<div class="layui-inline"><label class="layui-form-label">忽略警告</label><div class="layui-input-block"><input type="checkbox" name="enableIgnoreWarnings" value=1 lay-skin="switch" lay-text="是|否" lay-filter="enableIgnoreWarnings"></div></div>',
                '</div><div class="layui-form-item pane="">',
                '<div class="layui-inline"><label class="layui-form-label">立即执行</label><div class="layui-input-inline"><input type="checkbox" name="executeNow" value=1 lay-skin="switch" lay-text="是|否" checked="" lay-filter="executeNow"></div></div>',
                '<div class="layui-inline" id="executeTime" style="display:none"><label class="layui-form-label">执行时间</label><div class="layui-input-inline"><input type="text" name="timer" class="layui-input" id="timer" value=0></div></div>',
                '</div><button style="display:none" lay-submit lay-filter="checkTaskSubmit" id="checkTaskSubmit"></button>',
                '<button style="display:none" lay-submit lay-filter="addTaskSubmit" id="addTaskSubmit"></button>',
                '</form></div>'
            ].join(""),
            closeBtn: false,
            shadeClose: false,
            shade: 0.1,
            btn: ['检查', '添加', '取消'],
            btnAlign: 'c',
            area: ['560px', '580px'],
            success: function() {
                //渲染mysql
                incetops.ajax("/IncetOps/api/?Action=DBGetList", function(res) {
                    $("#dbOptions").empty();
                    $("#dbOptions").append("<option value=''>请选择MySQL实例</option>");
                    res.data.map(function(i) {
                        var c = i.host + ":" + i.port + ":" + i.user;
                        $("#dbOptions").append("<option data-ris='" + i.ris + "' value=" + i.id + ">" + i.sd + " [" + c + "] " + "</option>");
                    });
                    form.render("select");
                }, {
                    method: "get",
                    msgprefix: "MySQL实例数据异常"
                });
                //渲染inception
                incetops.ajax("/IncetOps/api/?Action=InceptionGetList", function(res) {
                    $("#inceptionOptions").empty();
                    $("#inceptionOptions").append("<option value=''>请选择Inception服务</option>");
                    res.data.map(function(i) {
                        var c = i.host + ":" + i.port;
                        $("#inceptionOptions").append("<option value='" + c + "'>" + i.sd + " [" + c + "] " + "</option>");
                    });
                    form.render("select");
                }, {
                    method: "get",
                    msgprefix: "Inception服务数据异常"
                });
                //加载申请人
                incetops.ajax("/IncetOps/api/?Action=MiscGetApplicants", function(res) {
                    $("#applicant").empty();
                    res.data.map(function(i) {
                        $("#applicant").append("<option value='" + i + "'>");
                    });
                }, {
                    method: "get",
                    msgprefix: "Inception服务数据异常"
                });
                //更新表单(例开关)
                form.render();
            },
            yes: function(index, layero) {
                //按钮【检查】的回调
                $("#checkTaskSubmit").click()
                return false;
            },
            btn2: function(index, layero) {
                //按钮【添加】的回调
                addTaskIndex = index;
                $("#addTaskSubmit").click()
                return false;
            },
            btn3: function(index, layero) {
                //按钮【取消】的回调
                layer.close(index);
            }
        });
    });
    //监听选择mysql实例
    form.on('select(db)', function(data) {
        var elem = data.elem;
        for (var i = 0; i < elem.length; i++) {
            if (elem[i].getAttribute('value') === data.value) {
                var ris = elem[i].getAttribute('data-ris');
                if (ris) {
                    var ios = document.getElementById("inceptionOptions");
                    if (ios && ios.length > 0) {
                        for (var a = 0; a < ios.length; a++) {
                            if (ios[a].getAttribute('value') === ris) {
                                ios[a].setAttribute('selected', true);
                                form.render("select");
                            } else {
                                ios[a].removeAttribute('selected');
                                form.render("select");
                            }
                        }
                    }
                }
            }
        }
    });
    //监听立即执行开关
    form.on('switch(executeNow)', function(data) {
        if (data.elem.checked === false) {
            //定时执行，开启laydate
            $("#executeTime").css('display', 'block');
            laydate.render({
                elem: "#timer",
                type: "datetime",
                theme: 'molv',
                format: "yyyy-MM-dd HH:mm:ss",
                min: Math.round(new Date().getTime() + 600000),
                value: util.toDateString(Math.round(new Date().getTime() + 600000)),
                btns: ['clear', 'confirm']
            });
        } else {
            $("#executeTime").css('display', 'none');
        }
    });
    //监听检查任务
    form.on('submit(checkTaskSubmit)', function(data) {
        if (incetops.rstrip(data.field.sqlContent).endsWith(';') === true) {
            incetops.ajax("/IncetOps/api/?Action=TaskCheck", function(res) {
                //成功通过Inception连接MySQL执行了检查，返回数组，每条SQL一个，表格展示。
                var showHtml = '<div style="padding: 10px;"><table class="layui-table" lay-skin="line"><thead><tr><th>SQL语句</th><th>错误级别</th><th>错误信息</th><th>阶段标识</th><th>阶段信息</th><th>预计影响行数</th><th>SQLSHA1</th></tr></thead><tbody>';
                for (var i = 0; i < res.data.length; i++) {
                    var d = res.data[i],
                        color = "color:#00A600";
                    if (d.errlevel === 1) {
                        color = "color:#FFB800";
                    } else if (d.errlevel === 2) {
                        color = "color:#FF0000";
                    }
                    showHtml += '<tr style="' + color + '"><td>' + d.SQL + '</td><td>' + d.errlevel + '</td><td>' + d.errormessage + '</td><td>' + d.stage + '</td><td>' + d.stagestatus + '</td><td>' + d.Affected_rows + '</td><td>' + d.sqlsha1 + '</td></tr>';
                }
                showHtml += '</tbody></table><blockquote class="layui-elem-quote"><b>请注意！</b><br>颜色全部为绿色时，即表示检查无异常；颜色存在红色时，即表示有SQL异常。<br><i>错误级别为0，颜色为绿色，表示没有错误；<br>错误级别为1，颜色为黄色，表示警告，若人工核实无误可以开启忽略警告开关；<br>错误级别为2，颜色为红色，表示错误，必须核对修改SQL语句！</i></blockquote></div>';
                layer.open({
                    type: 1,
                    title: "SQL Check Result",
                    content: showHtml,
                    shadeClose: false,
                    shade: 0,
                    area: '700px',
                    maxmin: true,
                    success: function(layero, index) {
                        layer.full(index);
                    }
                });
            }, {
                data: data.field,
                method: "post",
                msgprefix: false,
                fail: function(res) {
                    layer.msg(res.msg, {
                        icon: 2,
                        time: 3000
                    });
                }
            });
        } else {
            layer.msg("SQL not end with ; Please check !", {
                icon: 7,
                time: 3000
            });
        }
        return false;
    });
    //监听添加任务
    form.on('submit(addTaskSubmit)', function(data) {
        incetops.ajax("/IncetOps/api/?Action=TaskAdd", function(res) {
            layer.close(addTaskIndex);
            layer.msg("任务已提交", {
                icon: 1,
                time: 2000
            }, function() {
                // 重载表格数据
                table.reload("taskList", tableOptions);
            });
        }, {
            data: data.field,
            method: "post",
            msgprefix: false,
            fail: function(res) {
                layer.msg("添加失败" + res.msg, {
                    icon: 7,
                    time: 3000
                });
            }
        });
        return false; //阻止表单跳转。如果需要表单跳转，去掉这段即可。
    });
    exports("Task", null);
});