layui.define(['incetops', 'form', 'layer', 'table', 'util'], function(exports) {
    var $ = layui.jquery,
        util = layui.util,
        form = layui.form,
        layer = layui.layer,
        table = layui.table,
        incetops = layui.incetops;
    //Inception列表参数
    var tableOptions = {
        elem: '#inceptionList',
        url: '/IncetOps/api/?Action=InceptionGetList',
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
                minWidth: 200,
                align: 'center',
            }, {
                field: 'host',
                title: '地址',
                align: 'center',
                templet: function(d) {
                    return d.host + ":" + d.port;
                }
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
                toolbar: '#inceptionListBar',
                fixed: "right",
                align: "center"
            }]
        ]
    };
    //初始化渲染表格
    table.render(tableOptions);
    //列表操作
    table.on('tool(inceptionList)', function(obj) {
        var layEvent = obj.event,
            data = obj.data;
        if (layEvent === 'del') {
            layer.confirm('确定删除此Inception记录？', {
                icon: 3,
                title: '温馨提示'
            }, function(index) {
                layer.close(index);
                //向服务端发送删除指令
                incetops.ajax("/IncetOps/api/?Action=InceptionDel", function(res) {
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
    //监听添加Inception服务弹出表单
    var addInceptionIndex;
    $(".addInceptinBtn").click(function() {
        layer.open({
            type: 1,
            title: "添加Inception",
            content: '<div style="padding: 10px;"><form class="layui-form"><div class="layui-form-item"><input class="layui-input" name="connect" placeholder="连接地址:端口" value="" type="text" autofocus="autofocus" lay-verify="required|hostport"></div><div class="layui-form-item"><input class="layui-input" name="sd" placeholder="连接描述信息" value="" type="text" lay-verify="required"></div><button style="display:none" lay-submit lay-filter="addInceptionSubmit" id="addInceptionSubmit"></button></form></div>',
            closeBtn: false,
            shadeClose: false,
            shade: 0,
            btn: ['添加', '取消'],
            btnAlign: 'c',
            area: '280px',
            yes: function(index, layero) {
                //按钮【添加】的回调
                addInceptionIndex = index;
                $("#addInceptionSubmit").click()
            },
            btn2: function(index, layero) {
                //按钮【取消】的回调
                layer.close(index);
            }
        });
    });
    //监听添加Inception表单验证与提交
    form.verify({
        hostport: function(value, item) { //value：表单的值、item：表单的DOM对象
            if (incetops.verifyIpPort(value) != true) {
                return '连接格式错误';
            }
        }
    });
    form.on('submit(addInceptionSubmit)', function(data) {
        incetops.ajax("/IncetOps/api/?Action=InceptionAdd", function(res) {
            layer.close(addInceptionIndex);
            layer.msg("添加成功", {
                icon: 1,
                time: 2000
            }, function() {
                // 重载表格数据
                table.reload("inceptionList", tableOptions);
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
    exports("Inception", null);
});