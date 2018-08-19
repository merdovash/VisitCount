host = "";
uid = null;

function postRequest(name, request, handler) {
    //init
	var xhr = new XMLHttpRequest();
	xhr.open("POST", name, true);
	xhr.setRequestHeader("Content-Type", "application/json");
	xhr.onreadystatechange = function() {
		if (xhr.readyState != 4) return;
		if (xhr.status == 200) {
			// если пришёл ответ
			var data = JSON.parse(xhr.responseText);
			console.log (xhr.responseText);
			if (data.status == "OK") {
			    // обработка данных
				// console.log(xhr.responseText);
				// loadingPlace.innerHTML="";
				handler(data.data);
			}
			else {
				console.log(data.message);
			}
		} else {
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

function login() {
    var log = document.getElementById("log").value;
    var pass = document.getElementById("pass").value;

    var request = {
        'type': 'login',
        'user':{
            'login':log,
            'password':pass
        },
        data: {}
    }
    console.log(request)
    postRequest('/login', request, onSuccess)
}

function onSuccess(data) {
    setCookie('uid', data.uid);
    window.location.replace(data.page)
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