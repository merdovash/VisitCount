var data = null;

function load(){
    function _load(d) {
        data = d
    }

    postRequest('/user_info', {user: {uid:getCookie('uid')}}, _load)
}

load();

name = new Vue(
    el: '#username',
    data: {
        first_name: data.user.first_name,
        last_name: data.user.last_name,
        middle_name: data.user.middle_name
    }
);