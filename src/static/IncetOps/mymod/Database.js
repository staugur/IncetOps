layui.define(['incetops', 'form', 'layer', 'table', 'util'], function(exports) {
    var $ = layui.jquery,
        util = layui.util,
        form = layui.form,
        layer = layui.layer,
        table = layui.table,
        incetops = layui.incetops;
    //数据库列表参数
    var tableOptions = {
        elem: '#dbList',
        url: '/IncetOps/api/?Action=DBGetList',
        cellMinWidth: 95,
        page: false,
        height: "full-125",
        cols: [
            [{
                type: "checkbox",
                fixed: "left",
                width: 50
            }, {
                field: 'id',
                title: '序号',
                width: 80,
                sort: true,
                align: "center"
            }, {
                field: 'sd',
                title: '描述信息',
                minWidth: 150,
                align: 'center',
            }, {
                field: 'host',
                title: '地址',
                align: 'center',
                templet: function(d) {
                    return d.host + ":" + d.port;
                }
            }, {
                field: 'user',
                title: '用户',
                align: 'center',
            }, {
                field: 'ris',
                title: 'Inception推荐地址',
                align: 'center',
            }, {
                field: 'ctime',
                title: '创建时间',
                align: 'center',
                width: 170,
                templet: function(d) {
                    return util.toDateString(d.ctime * 1000);
                }
            }, {
                title: '动作',
                width: 80,
                toolbar: '#dbListBar',
                fixed: "right",
                align: "center"
            }]
        ]
    };
    //初始化渲染表格
    table.render(tableOptions);
    //列表操作
    table.on('tool(dbList)', function(obj) {
        var layEvent = obj.event,
            data = obj.data;
        if (layEvent === 'del') {
            layer.confirm('确定删除此数据库记录？', {
                icon: 3,
                title: '温馨提示'
            }, function(index) {
                layer.close(index);
                //向服务端发送删除指令
                incetops.ajax("/IncetOps/api/?Action=DBDel", function(res) {
                    obj.del(); //删除对应行（tr）的DOM结构，并更新缓存
                }, {
                    data: {
                        "id": data.id
                    },
                    method: "delete"
                });
            });
        }
    });
    //监听添加数据库服务弹出表单
    var addDBIndex;
    $(".addDBBtn").click(function() {
        layer.open({
            type: 1,
            title: "添加数据库",
            content: '<div style="padding: 10px;"><form class="layui-form"><div class="layui-form-item"><input class="layui-input" name="host" placeholder="DB连接地址" value="" type="text" autofocus="autofocus" lay-verify="required"></div><div class="layui-form-item"><input class="layui-input" name="port" placeholder="DB连接端口" value="3306" type="number" lay-verify="required|number"></div><div class="layui-form-item"><input class="layui-input" name="user" placeholder="DB连接用户" value="root" type="text" lay-verify="required"></div><div class="layui-form-item"><input class="layui-input" name="passwd" placeholder="DB连接密码" value="" type="password" lay-verify="required"></div><div class="layui-form-item"><select id="risOptions" name="ris" lay-filter="ris"><option value="">请选择推荐的Inception服务</option></select></div><div class="layui-form-item"><input class="layui-input" name="sd" placeholder="连接描述信息" value="" type="text" lay-verify="required"></div><button style="display:none" lay-submit lay-filter="addDBSubmit" id="addDBSubmit"></button></form></div>',
            closeBtn: false,
            shadeClose: false,
            shade: 0.2,
            btn: ['添加', '取消'],
            btnAlign: 'c',
            area: '300px',
            success: function() {
                incetops.ajax("/IncetOps/api/?Action=InceptionGetList", function(res) {
                    $("#risOptions").empty();
                    $("#risOptions").append("<option value=''>请选择推荐的Inception服务</option>");
                    res.data.map(function(i) {
                        var c = i.host + ":" + i.port;
                        $("#risOptions").append("<option value='" + c + "'>" + i.sd + " [" + c + "] " + "</option>");
                    });
                    form.render('select');
                }, {
                    method: "get",
                    msgprefix: false
                });
            },
            yes: function(index, layero) {
                //按钮【添加】的回调
                addDBIndex = index;
                $("#addDBSubmit").click()
            },
            btn2: function(index, layero) {
                //按钮【取消】的回调
                layer.close(index);
            }
        });
    });
    form.on('submit(addDBSubmit)', function(data) {
        incetops.ajax("/IncetOps/api/?Action=DBAdd", function(res) {
            layer.close(addDBIndex);
            layer.msg("添加成功", {
                icon: 1,
                time: 2000
            }, function() {
                // 重载表格数据
                table.reload("dbList", tableOptions);
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
    exports("Database", null);
});