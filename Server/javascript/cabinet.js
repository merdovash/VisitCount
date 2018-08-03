

function get_cookie(cookie_name) {
    var results = document.cookie.match ('(^|;) ?' + cookie_name + '=([^;]*)(;|$)');
    return results ? decodeURIComponent(results[2]) : null;
}

user_info_is_set=false
groups=null
var xhr = new XMLHttpRequest()

function onload()
{
    uid=get_cookie("uid")

    xhr.open("GET", "/user_info:"+uid, true)
    xhr.setRequestHeader('Content-Type', 'multipart/form-data')
    xhr.onreadystatechange = function()
    {
        if (xhr.readyState !=4) return
        if (xhr.status==200)
        {
            if (user_info_is_set) return
            data = JSON.parse(xhr.responseText)
            alert(data)
            keys=["last_name","first_name","middle_name","groups"]
            for (key in keys)
            {

                alert(keys[key])
                user_info_field=document.getElementById("user_info")

                div = document.createElement("div")
                user_info_field.appendChild(div)

                div.setAttribute("id",keys[key])
                if (data[keys[key]]["attributes"])
                {
                    for (attribute in data[keys[key]]["attributes"])
                    {
                        div.setAttribute(attribute, data[keys[key]]["attributes"][attribute])
                    }
                }
                div.innerHTML=data[keys[key]]
            }
            if (data["groups"]!=null)
            {
                groups=data["groups"].split(',').map(x=>parseInt(x))
            }
            user_info_is_set=true
        }
    }
    xhr.send()
}

onload()

function select()
{
    page = document.getElementById("page_body")
    while(page.firstChild) page.removeChild(page.firstChild)

    create_form()
}

function create_form()
{
    var form = document.createElement("form")
    page.appendChild(form)

    form.setAttribute("method", "POST")
    form.setAttribute("id","main_form")
    form.setAttribute("enctype"," multipart/form-data")

    discipline_id_field = document.createElement("div")
    discipline_id_field.setAttribute("id","discipline_id")
    form.appendChild(discipline_id_field)

    if (!groups || groups.length==1) show_disciplines()
    else show_groups()
}

function show_groups()
{
    xhr.open("GET", "/get_groups_list", true)
    xhr.setRequestHeader('Content-Type', 'multipart/form-data')
    xhr.onreadystatechange = function()
    {
        if (xhr.readyState != 4)
        if (xhr.status==200)
        {
            data=JSON.parse(xhr.responseText)
            select = document.createElement("select")
            form.appendChild(select)

            select.setAttribute("name","select_group_id")
            select.setAttribute("id","select_group_id")
            select.setAttribute("onchage", "show_disciplines()")

            for (i in data)
            {
                option=document.createElement("option")
                option.value=data[i]["id"]
                option.innerHTML=data[i]["name"]

                select.appendChild(option)
            }
        }
    }
    xhr.send()
}

function show_disciplines()
{
    xhr.open("GET", "get_disciplines_list", true)
    xhr.setRequestHeader('Content-Type', 'multipart/form-data')
    xhr.onreadystatechange = function()
    {
        if (xhr.status == 200)
        {
            data = JSON.parse(xhr.responseText)

            select = document.getElementById("select_discipline_id")
            if (select)
            {
                while (select.firstChild)
                {
                    select.removeChild(select.firstChild)
                }
            }
            else
            {
                select = document.createElement("select")
                select.setAttribute("name", "select_discipline_id")
                select.setAttribute("id", "select_discipline_id")
                select.setAttribute("onchange",data["onchange"])

            }

            document.getElementById("discipline_id").innerHTML="Выберите дисциплину"


            //alert(JSON.parse(data))
            discipline_id = document.getElementById("discipline_id")

            for (i in data["data"])
            {
                option=document.createElement("option")
                option.value=data["data"][i]["id"]
                option.innerHTML=data["data"][i]["name"]

                select.appendChild(option)
            }

            discipline_id.appendChild(select)
        }
    }
    xhr.send()
}

function show_btn()
{
    if (!document.getElementById("submit_btn"))
    {
        btn =document.createElement("input")
        btn.setAttribute("type","submit")
        btn.setAttribute("id", "submit_btn")
        btn.setAttribute("onclick","request_table()")
        document.getElementById("main_form").appendChild(btn)
    }
}

Date.prototype.getWeek = function (date) {
    var target  = new Date(this.valueOf());
    var dayNr   = (this.getDay() + 6) % 7;
    target.setDate(target.getDate() - dayNr + 3);
    var firstThursday = target.valueOf();
    target.setMonth(0, 1);
    if (target.getDay() != 4) {
        target.setMonth(0, 1 + ((4 - target.getDay()) + 7) % 7);
    }
    return 1 + Math.ceil((firstThursday - target) / 604800000);
}

function get_date(date){
    date2 = new Date();
    var current_year= date2.getFullYear();
    var month_start=1;
    if (date2.getMonth()>=8) month_start=8;

    var start= new Date(current_year, month_start, 1);
    var start_week = start.getWeek();
    var start_day=start.getDay();

    lesson=date%10;
    day=Math.floor(date/10)%10;
    week=Math.floor(date/100);

    start.setDate(start.getDate()+ week*7+(start_day-day));
    return start.getDay()+"."+(start.getMonth()+1)+"."+start.getFullYear()+" #"+lesson;
}

function count(obj) {

    if (obj.__count__ !== undefined) { // Old FF
        return obj.__count__;
    }
    if (Object.keys) { // ES5
        return Object.keys(obj).length;
    }

    // Everything else:
    var c = 0, p;
    for (p in obj) {
        if (obj.hasOwnProperty(p)) {
            c += 1;
        }
    }
    return c;
}

// my codde
function create_table(text) {

	var data = JSON.parse(text);
	alert(text);

	var header = data["head"];
	for (let key in header) {
		let value = header[key];
	}

	var cols_titles = data["cols_head"];
	var length = count(cols_titles);

	var table = document.createElement('table');
	table.className = "tables";

	var headers = document.createElement('tr');

	for (let key in cols_titles) {
		let value = cols_titles[key];
		var td = document.createElement('td');
		td.className = "rotate";
		var title = document.createTextNode(get_date(value));
		var titler2 = document.createElement('span');
		var titler = document.createElement('div');

		titler.className = "rotated-text";
		titler2.className = "rotated-text__inner";
		titler2.appendChild(title)
		titler.appendChild(titler2);

		td.appendChild(titler);
		headers.appendChild(td);
	}
	table.appendChild(headers);

	var marks = document.createElement('tr');
	for (let key in cols_titles) {
		let value = cols_titles[key];
		var td = document.createElement('td');
		td.id = key;
		td.className="not_visited";
		marks.appendChild(td);
	}
	table.appendChild(marks);
	document.body.appendChild(table);

	var main = data["data"];
	for (let key in main) {
		let value = main[key];
		let kol = value["col_id"];
		var x = document.getElementById(kol);
		x.className = "visited";
	}
}

function table_request() {

    page_body=document.getElementById("page_body")

	var xhr = new XMLHttpRequest();
	var query = "http://127.0.0.1:5000/get_table:"+uid+":"+disc+"";

	xhr.open("GET", query, true);
	xhr.send();

	xhr.onreadystatechange = function() {
		if (xhr.status == 200) {
			create_table(xhr.responseText);
		}
	}
}