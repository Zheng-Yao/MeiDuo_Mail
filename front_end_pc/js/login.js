var vm = new Vue({
    el: '#app',
    data: {
        host,
        error_username: false,
        error_pwd: false,
        error_username_message: '请填写手机号或用户名',
        error_pwd_message: '请填写密码',

        username: '',
        password: '',
        remember: false
    },
    methods: {
        get_query_string: function (name) {
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        check_username: function () {
            if (!this.username) {
                this.error_username_message = '请填写用户名或者手机号码';
                this.error_name = true;
            } else {
                this.error_name = false;
            }
        },
        check_pwd: function () {
            if (!this.password) {
                this.error_pwd_message = '请填写密码';
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        on_submit: function () {
            this.check_username();
            this.check_pwd();
            if (this.error_name == false & this.error_password == false) {
                axios.post(this.host + '/authorizations/', {
                    'username': this.username,
                    'password': this.password,
                }, {
                    responseType: 'json',
                }).then(response => {
                    //判断是否记住密码，选择token的存储方式
                    //记住密码
                    if (this.remember) {
                        sessionStorage.clear();
                        localStorage.token = response.data.token;
                        localStorage.user_id = response.data.user_id;
                        localStorage.username = response.data.username;
                    } else {
                        localStorage.clear();
                        sessionStorage.token = response.data.token;
                        sessionStorage.user_id = response.data.user_id;
                        sessionStorage.username = response.data.username;
                    }
                    // www.meiduo.site/authorizations/?next=cart
                    // 跳转页面
                    // 这里判断地址栏上面是否有next查询字符串中的字段，如果有，则需要跳转到next指定的页面
                    var return_url = this.get_query_string('next');
                    if (!return_url) {
                        return_url = '/index.html';
                    }
                    location.href = return_url;
                }).catch(error => {
                    this.error_pwd_message = '用户名或密码错误';
                    this.error_pwd = true;
                })
            }
        },
    },
})