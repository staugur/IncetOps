layui.define(['element', 'layer', 'form', 'util'], function(exports) {
    var $ = layui.jquery,
        form = layui.form,
        util = layui.util,
        layer = layui.layer,
        device = layui.device(),
        element = layui.element;
    //阻止IE7以下访问
    if (device.ie && device.ie < 8) {
        layer.alert('如果您非得使用 IE 浏览器访问，那么请使用 IE8+');
    }
    //右下角工具
    util.fixbar({
        bgcolor: '#009688'
    });
    //公共接口
    var api = {
        ajax: function(url, success, options) {
            /*
                Ajax提交
                @param url string: 请求路径
                @param success function: success为成功后回调函数
                @param options object:
                    async是否异步; 
                    post,put,delete等方法所需data;
                    error为发生异常时或success返回中code不为0时回调函数;
                    beforeSend为请求前回调函数;
                    complete为完成请求后回调;
                    msgprefix表示success返回code不为0时提示消息的前缀。
            */
            var that = this,
                urltype = typeof url === 'string',
                successtype = typeof success === "function",
                optionstype = typeof options === "object";
            if (!url || !urltype) {
                return false;
            }
            if (success) {
                if (!successtype) {
                    return false;
                }
            }
            if (options) {
                if (!optionstype) {
                    return false;
                }
            } else {
                options = {};
            }
            return $.ajax({
                url: url,
                async: options.async || true,
                method: options.method || 'post',
                dataType: options.dataType || 'json',
                data: options.data || {},
                beforeSend: options.beforeSend ? options.beforeSend : function() {},
                success: function(res) {
                    if (res.code === 0 || res.success === true) {
                        success && success(res);
                    } else {
                        if (options.msgprefix != false) {
                            layer.msg(options.msgprefix || '' + res.msg || res.code);
                        }
                        options.fail && options.fail(res);
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    layer.msg("系统异常，请稍后再试，状态码：" + XMLHttpRequest.status + "，" + textStatus);
                },
                complete: options.complete ? options.complete : function() {}
            });
        },
        getUrlPath: function(ishref) {
            /*
                获取url路径(不包含锚部分)；如果ishref为true，则返回全路径(包含锚部分)
                比如url为http://passport.saintic.com/user/setting/，默认返回/user/setting/ ，ishref为true返回上述url
            */
            return ishref === true ? location.href : location.pathname;
        },
        getUrlQuery: function(key, acq) {
            /*
                获取URL中?之后的查询参数，不包含锚部分，比如url为http://passport.saintic.com/user/message/?status=1&Action=getCount
                若无查询的key，则返回整个查询参数对象，即返回{status: "1", Action: "getCount"}；
                若有查询的key，则返回对象值，返回值可以指定默认值acq：如key=status, 返回1；key=test返回acq
            */
            var str = location.search;
            var obj = {};
            if (str) {
                str = str.substring(1, str.length);
                // 以&分隔字符串，获得类似name=xiaoli这样的元素数组
                var arr = str.split("&");
                //var obj = new Object();
                // 将每一个数组元素以=分隔并赋给obj对象
                for (var i = 0; i < arr.length; i++) {
                    var tmp_arr = arr[i].split("=");
                    obj[decodeURIComponent(tmp_arr[0])] = decodeURIComponent(tmp_arr[1]);
                }
            }
            return key ? obj[key] || acq : obj;
        },
        isContains: function(str, substr) {
            /* 判断str中是否包含substr */
            return str.indexOf(substr) >= 0;
        },
        safeCheck: function(s) {
            /* 简单字符串安全检查 */
            try {
                if (s.indexOf("'") != -1 || s.indexOf('"') != -1 || s.indexOf("?") != -1 || s.indexOf("%") != -1 || s.indexOf(";") != -1 || s.indexOf("*") != -1 || s.indexOf("=") != -1 || s.indexOf("\\") != -1) {
                    return false
                } else {
                    return true;
                }
            } catch (e) {
                return false;
            }
        },
        isValidIP: function(ip) {
            var reg = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/
            return reg.test(ip);
        },
        verifyIpPort: function(s) {
            /* 验证IP:PORT形式的字符串 */
            var pat = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\:([0-9]|[1-9]\d{1,3}|[1-5]\d{4}|6[0-5]{2}[0-3][0-5])$/;
            return pat.test(s);
        },
        syntaxHighlight: function(json) {
            /* 格式化显示JSON数据 */
            if (typeof json != 'string') {
                json = JSON.stringify(json, undefined, 4);
            }
            json = json.replace(/&/g, '&').replace(/</g, '<').replace(/>/g, '>');
            return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function(match) {
                var cls = 'number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'key';
                    } else {
                        cls = 'string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'boolean';
                } else if (/null/.test(match)) {
                    cls = 'null';
                }
                return '<span class="' + cls + '">' + match + '</span>';
            });
        },
        strip: function(str) {
            //去除字符串两边空格
            return str.replace(/^\s+|\s+$/g, "");
        },
        rstrip: function(str) {
            //去除字符串右侧空格
            return str.replace(/(\s*$)/g, "");
        },
        lstrip: function(str) {
            //去除字符串左侧空格
            return str.replace(/^\s*/, '');
        },
        checkURL: function(URL) {
            var str = URL;
            //判断URL地址的正则表达式为:http(s)?://([\w-]+\.)+[\w-]+(/[\w- ./?%&=]*)?
            //下面的代码中应用了转义字符"\"输出一个字符"/"
            var Expression = /http(s)?:\/\/([\w-]+\.)+[\w-]+(\/[\w- .\/?%&=]*)?/;
            var objExp = new RegExp(Expression);
            if (objExp.test(str) == true) {
                return true;
            } else {
                return false;
            }
        },
        isEmptyObject: function(obj) {
            for (var key in obj) {
                return false;
            }
            return true;
        }
    };
    //获取用户信息
    function getSetUser() {
        function set() {
            //更新顶部导航昵称
            $('#nav_nickname').text(sessionStorage.getItem("nick_name"));
            //更新顶部导航头像
            $('#nav_avatar').attr('src', sessionStorage.getItem("avatar"));
        }
        if (!sessionStorage.getItem("avatar")) {
            //获取用户信息
            api.ajax(layui.cache.conf.sso_server + "/api/user/profile/", function(res) {
                var avatar = res.data.avatar || '/static/IncetOps/images/default.png';
                if (api.checkURL(avatar) === false) {
                    avatar = layui.cache.conf.sso_server + avatar;
                }
                sessionStorage.setItem("avatar", avatar);
                sessionStorage.setItem("nick_name", res.data.nick_name || '');
                set();
            }, {
                "async": true,
                "method": "get",
                "msgprefix": '拉取用户信息失败',
                "beforeSend": function(xhr) {
                    xhr.setRequestHeader("sessionId", layui.cache.conf.sessionId);
                }
            });
        } else {
            set();
        }
    }
    getSetUser();
    //隐藏左侧导航
    $(".hideMenu").click(function() {
        $(".layui-layout-admin").toggleClass("showMenu");
    })
    //手机设备的简单适配
    $('.site-tree-mobile').on('click', function() {
        $('body').addClass('site-mobile');
    });
    $('.site-mobile-shade').on('click', function() {
        $('body').removeClass('site-mobile');
    });
    //清除缓存
    $(".clearCache").click(function() {
        localStorage.clear();
        sessionStorage.clear();
        var index = layer.msg('清除缓存中，请稍候', {
            icon: 16,
            time: false,
            shade: 0
        });
        setTimeout(function() {
            layer.close(index);
            layer.msg("缓存清除成功，请刷新页面！", {
                icon: 1,
                time: 2000
            });
        }, 1000);
    });
    //更换皮肤
    function skins() {
        var skin = window.sessionStorage.getItem("skin");
        if (skin) { //如果更换过皮肤
            if (window.sessionStorage.getItem("skinValue") != "自定义") {
                $("body").addClass(window.sessionStorage.getItem("skin"));
            } else {
                $(".layui-layout-admin .layui-header").css("background-color", skin.split(',')[0]);
                $(".layui-bg-black").css("background-color", skin.split(',')[1]);
                $(".hideMenu").css("background-color", skin.split(',')[2]);
            }
        }
    }
    skins();
    $(".changeSkin").click(function() {
        layer.open({
            title: "更换皮肤",
            area: ["310px", "280px"],
            type: "1",
            content: '<div class="skins_box">' +
                '<form class="layui-form">' +
                '<div class="layui-form-item">' +
                '<input type="radio" name="skin" value="默认" title="默认" lay-filter="default" checked="">' +
                '<input type="radio" name="skin" value="橙色" title="橙色" lay-filter="orange">' +
                '<input type="radio" name="skin" value="蓝色" title="蓝色" lay-filter="blue">' +
                '<input type="radio" name="skin" value="自定义" title="自定义" lay-filter="custom">' +
                '<div class="skinCustom">' +
                '<input type="text" class="layui-input topColor" name="topSkin" placeholder="顶部颜色" />' +
                '<input type="text" class="layui-input leftColor" name="leftSkin" placeholder="左侧颜色" />' +
                '<input type="text" class="layui-input menuColor" name="btnSkin" placeholder="顶部菜单按钮" />' +
                '</div>' +
                '</div>' +
                '<div class="layui-form-item skinBtn">' +
                '<a href="javascript:;" class="layui-btn layui-btn-sm layui-btn-normal" lay-submit="" lay-filter="changeSkin">确定更换</a>' +
                '<a href="javascript:;" class="layui-btn layui-btn-sm layui-btn-primary" lay-submit="" lay-filter="noChangeSkin">我再想想</a>' +
                '</div>' +
                '</form>' +
                '</div>',
            success: function(index, layero) {
                var skin = window.sessionStorage.getItem("skin");
                if (window.sessionStorage.getItem("skinValue")) {
                    $(".skins_box input[value=" + window.sessionStorage.getItem("skinValue") + "]").attr("checked", "checked");
                };
                if ($(".skins_box input[value=自定义]").attr("checked")) {
                    $(".skinCustom").css("visibility", "inherit");
                    $(".topColor").val(skin.split(',')[0]);
                    $(".leftColor").val(skin.split(',')[1]);
                    $(".menuColor").val(skin.split(',')[2]);
                };
                form.render();
                $(".skins_box").removeClass("layui-hide");
                $(".skins_box .layui-form-radio").on("click", function() {
                    var skinColor;
                    if ($(this).find("div").text() == "橙色") {
                        skinColor = "orange";
                    } else if ($(this).find("div").text() == "蓝色") {
                        skinColor = "blue";
                    } else if ($(this).find("div").text() == "默认") {
                        skinColor = "";
                    }
                    if ($(this).find("div").text() != "自定义") {
                        $(".topColor,.leftColor,.menuColor").val('');
                        $("body").removeAttr("class").addClass("main_body " + skinColor + "");
                        $(".skinCustom").removeAttr("style");
                        $(".layui-bg-black,.hideMenu,.layui-layout-admin .layui-header").removeAttr("style");
                    } else {
                        $(".skinCustom").css("visibility", "inherit");
                    }
                });
                var skinStr, skinColor;
                $(".topColor").blur(function() {
                    $(".layui-layout-admin .layui-header").css("background-color", $(this).val() + " !important");
                })
                $(".leftColor").blur(function() {
                    $(".layui-bg-black").css("background-color", $(this).val() + " !important");
                })
                $(".menuColor").blur(function() {
                    $(".hideMenu").css("background-color", $(this).val() + " !important");
                })

                form.on("submit(changeSkin)", function(data) {
                    if (data.field.skin != "自定义") {
                        if (data.field.skin == "橙色") {
                            skinColor = "orange";
                        } else if (data.field.skin == "蓝色") {
                            skinColor = "blue";
                        } else if (data.field.skin == "默认") {
                            skinColor = "";
                        }
                        window.sessionStorage.setItem("skin", skinColor);
                    } else {
                        skinStr = $(".topColor").val() + ',' + $(".leftColor").val() + ',' + $(".menuColor").val();
                        window.sessionStorage.setItem("skin", skinStr);
                        $("body").removeAttr("class").addClass("main_body");
                    }
                    window.sessionStorage.setItem("skinValue", data.field.skin);
                    layer.closeAll("page");
                });
                form.on("submit(noChangeSkin)", function() {
                    $("body").removeAttr("class").addClass("main_body " + window.sessionStorage.getItem("skin") + "");
                    $(".layui-bg-black,.hideMenu,.layui-layout-admin .layui-header").removeAttr("style");
                    skins();
                    layer.closeAll("page");
                });
            },
            cancel: function() {
                $("body").removeAttr("class").addClass("main_body " + window.sessionStorage.getItem("skin") + "");
                $(".layui-bg-black,.hideMenu,.layui-layout-admin .layui-header").removeAttr("style");
                skins();
            }
        });
    });
    // 输出模块名及参数
    exports('incetops', api);
});