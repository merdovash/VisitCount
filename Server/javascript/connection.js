function postRequest(name, request, handler = x => null, errorHandler = x => null) {
    //init
    var xhr = new XMLHttpRequest();
    xhr.open("POST", name, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return;
        if (xhr.status == 200) {
            // если пришёл ответ
            var data = JSON.parse(xhr.responseText);
            console.log(xhr.responseText);
            if (data.status == "OK") {
                // обработка данных
                // console.log(xhr.responseText);
                // loadingPlace.innerHTML="";
                handler(data.data);
            } else {
                errorHandler(data.message);
                console.log(data.message);
            }
        } else {
            errorHandler(xhr.status + ': ' + xhr.statusText);
            console.log(xhr.status + ': ' + xhr.statusText);
        }
    }

    //init loading visualizer
    //var loadingPlace = document.getElementById("loadingPlace");
    //loadingPlace.className="loading";
    //createLoading(loadingPlace);

    //run
    xhr.send(JSON.stringify(request));
}

function getRequest(request, handler) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", request, true);
    //var loadingPlace = document.getElementById("loadingPlace");
    //loadingPlace.className = "loading"
    xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return;
        if (xhr.status == 200) {
            // если пришёл ответ
            var data = JSON.parse(xhr.responseText);
            console.log(xhr.responseText);
            if (data.status == "ERROR") {
                console.log(data.message);
                if (data.msg == "auth failed") {
                    WrongPassword();
                }
            } else {
                // обработка данных
                // console.log(xhr.responseText);
                //loadingPlace.innerHTML = "";
                handler(data.data);
            }
        } else {
            console.log(xhr.status + ': ' + xhr.statusText);
        }
    }
    xhr.send();
    //createLoading(loadingPlace);
}

function deleteCookie(name) {
    setCookie(name, "", {
        expires: -1
    })
}

function setCookie(name, value, options) {
    options = options || {};

    var expires = options.expires;

    if (typeof expires == "number" && expires) {
        var d = new Date();
        d.setTime(d.getTime() + expires * 1000);
        expires = options.expires = d;
    }
    if (expires && expires.toUTCString) {
        options.expires = expires.toUTCString();
    }

    value = encodeURIComponent(value);

    var updatedCookie = name + "=" + value;

    for (var propName in options) {
        updatedCookie += "; " + propName;
        var propValue = options[propName];
        if (propValue !== true) {
            updatedCookie += "=" + propValue;
        }
    }

    document.cookie = updatedCookie;
}

function getCookie(name) {
    var matches = document.cookie.match(new RegExp(
        "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
}