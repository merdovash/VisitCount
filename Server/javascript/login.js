host = "";
uid = null;

function login() {
    var log = document.getElementById("log").value;
    var pass = document.getElementById("pass").value;

    var request = {
        'type': 'login',
        'user': {
            'login': log,
            'password': pass
        },
        data: {}
    }
    console.log(request)
    postRequest('/login', request, onSuccess)
}

function onSuccess(data) {
    setCookie('uid', data.uid);
    window.location.replace(data.page);
}