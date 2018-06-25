var vm = new Vue({
    el: '#app',
    data: {
        host,
        error_name: false,
        error_password: false,
        error_check_password: false,
        error_phone: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,

        username: '',
        password: '',
        password2: '',
        mobile: '',
        image_code: '',
        sms_code: '',
        allow: false,

        image_code_url: '',
        image_code_id: '',
        sending_flag: false,
        sms_tip: '获取短信验证码',
        error_name_messgae: '请输入5-20个字符的用户',
        error_phone_message: '您输入的手机号格式不正确',
        error_image_code_message: '请填写图片验证码',
        error_sms_code_message: '请填写短信验证码',
    },
    //mounted:在模板渲染成html后调用，通常是初始化页面完成后，再对html的dom节点进行一些需要的操作。
    mounted: function () {
        this.get_image_code()
    },
    methods: {
        //生成UUID
        get_uuid: function () {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },
        //生成验证码
        get_image_code: function () {
            this.image_code_id = this.get_uuid();
            this.image_code_url = "http://127.0.0.1:8000/image_code/" + this.image_code_id + '/';
        },
        check_username: function () {
            var len = this.username.length;
            if (len < 5 || len > 20) {
                this.error_name = true;
            } else {
                this.error_name = false;
            }
            //判断用户的唯一性
            if (this.error_name == false) {
                axios.get(this.host + '/username/' + this.username + '/count/', {
                    responseType: 'json',
                }).then(response => {
                    if (response.data.count > 0) {
                        this.error_name_messgae = '用户已经存在';
                        this.error_name = true;
                    } else {
                        this.error_name = false;
                    }
                }).catch(error => {
                    console.log(error.response.data)
                })
            }
        },
        check_pwd: function () {
            var len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_cpwd: function () {
            if (this.password != this.password2) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
            }
        },
        check_phone: function () {
            var re = /^1[345789]\d{9}$/;
            if (re.test(this.mobile)) {
                this.error_phone = false;
            } else {
                this.error_phone = true;
            }
            // 检验手机号码是否已经被注册
            if (this.error_phone == false) {
                axios.get(this.host + '/mobiles/' + this.mobile + '/count/', {
                    responseType: 'json',
                }).then(response => {
                    if (response.data.count > 0) {
                        this.error_phone_message = '该手机已经被注册';
                        this.error_phone = true;
                    } else {
                        this.error_phone = false;
                    }
                }).catch(error => {
                    console.log(error.response.data);
                })
            }
        },
        check_image_code: function () {
            if (!this.image_code) {
                this.error_image_code = true;
            } else {
                this.error_image_code = false;
            }
        },
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        check_allow: function () {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },
        // 注册
        on_submit: function () {
            this.check_username();
            this.check_pwd();
            this.check_cpwd();
            this.check_phone();
            this.check_sms_code();
            this.check_allow();
            if (this.error_name == false && this.error_password == false && this.error_check_password == false
                && this.error_phone == false && this.error_sms_code == false && this.error_allow == false) {
                axios.post(this.host + '/user/', {
                    'username': this.username,
                    'password': this.password,
                    'password2': this.password2,
                    'moblie': this.mobile,
                    'sms_code': this.sms_code,
                    'allow': this.allow.toString(),
                }, {
                    responseType: 'json',
                }).then(response => {
                    // 保存登陆状态
                    localStorage.clear()
                    sessionStorage.clear()
                    localStorage.username = response.data.username
                    localStorage.user_id = response.data.id
                    localStorage.token = response.data.token
                    // 跳转到对应页面
                    location.href = '/index.html'; //location.assign("/index.html")
                }).catch(error => {
                    if (error.response.status == 400) {
                        this.error_sms_code_message = '短信验证码错误';
                        this.error_sms_code = true;
                    } else {
                        console.log(error.response.data);
                    }
                })
            }
        },
        //   发送短信验证
        send_sms: function () {
            if (this.sending_flag == true) {
                return;
            }
            this.sending_flag = false;
            // 校验传输参数
            this.check_phone();
            this.check_image_code();
            if (this.error_phone == true || this.error_image_code == true) {
                this.sending_flag = false;
                return;
            }
            // 向后端发送请求
            axios.get("http://127.0.0.1:8000/sms_codes/" + this.mobile + '/?image_code_id=' + this.image_code_id + '&image_code_text=' + this.image_code, {
                responseType: 'json',
            }).then(response => {
                // 表示后端发送短信成功
                // 倒计时60秒，60秒后允许用户再次点击发送短信验证码的按钮
                var num = 60;
                _this = this;
                var t = setInterval(() => {
                    if (num == 1) {
                        clearInterval(t);
                        _this.sending_flag = false;
                        _this.sms_tip = '获取短信验证码';
                    } else {
                        num -= 1;
                        _this.sms_tip = num + ' 秒';
                    }
                }, 1000, 60);
            }).catch(error => {
                    if (error.response.status == 400) {
                        this.error_image_code_message = '图片验证码有误';
                        this.error_image_code = true;
                    } else {
                        //将其他报错的信息打出在后台
                        console.log(error.response.data);
                    }
                    this.sending_flag = false;
                }
            )
        },
    }
});
