var selected = null; 	// текущий пункт меню
user_type = null;		// тип пользователя: 0 - студент, 1 - препод, 2 - админ

// шаблон GET-запроса
function getRequest(request, handler) {
	var xhr = new XMLHttpRequest();
	xhr.open("GET", request, true);
	var loadingPlace = document.getElementById("loadingPlace");
	loadingPlace.className="loading"
	xhr.onreadystatechange = function() {
		if (xhr.readyState != 4) return;
		if (xhr.status == 200) {
			// если пришёл ответ
			var data = JSON.parse(xhr.responseText);
			console.log (xhr.responseText);
			if (data.status == "ERROR") {
				console.log(data.message);
				if (data.msg == "auth failed") {
				    WrongPassword();
				}
			}
			else {
				// обработка данных
				// console.log(xhr.responseText);
				loadingPlace.innerHTML="";
				handler(data.data);
			}
		} else {
			console.log(xhr.status + ': ' + xhr.statusText);
		}
	}
	xhr.send();
	createLoading(loadingPlace);
}

function exit() {
    ["uid", "user", "user_type"].forEach(x=> deleteCookie(x));
    document.location.href = "/";
}

function createLoading(loadingPlace) {
	['loader--dot', 'loader--dot', 'loader--dot','loader--dot','loader--dot','loader--dot','loader--text'].forEach(x=>{
		var div = document.createElement('div');
		div.className=x;
		loadingPlace.appendChild(div);
	})
}

function deleteCookie(name) {
    setCookie(name, "", {
        expires: -1
    })
}

function WrongPassword() {
    var answer = confirm ("Something went wrong.")
    if (answer) {
        deleteCookie("uid");
        document.location.href = host;
    }
}

// выделение нужного пункта бокового меню
function updateMenu(params) {
	if (selected != null) {
		var opt = selected.getElementsByClassName("option-sel")[0];
		opt.className = "option";
	}
	var button = document.getElementById(params);
	if (button != null) {
    	var opt = button.getElementsByClassName("option")[0];
    	opt.className = "option-sel";
    	selected = button;
	}
}

// обновление заголовка (фио, дата)
function updateUserInfo() {

	var type = null;
	var rank_name = document.getElementById("rank_name");

	if (user_type == 0) {
		type = "students";
		rank_name.innerHTML = "студент";
	}
	else if (user_type == 1) {
		type = "professors";
		rank_name.innerHTML = "преподаватель";
	}
	else if (user_type == 3) {
		type = "admin";
		rank_name.innerHTML = "администратор";
	}

	//getRequest(host + "/get?data=" + type + "&uid=" + uid, userHandler);
	console.log(user);
	userHandler(JSON.parse(getCookie("user")));
}

function userHandler(data) {

	var info = data[0];

	// определение имени
	var title_name = document.getElementById("title_name");
	//ещё один хак
	if (user_type == 0)
		title_name.innerHTML = info["first_name"] +" "+ info["middle_name"] +" "+ info["last_name"];
    else
        title_name.innerHTML = info["last_name"] +" "+ info["middle_name"] +" "+ info["first_name"];
	// определение даты и номера недели
	var date_pl = document.getElementById("date_pl");
	var week_pl = document.getElementById("week_pl");

	var datee = new Date();
	var weke = new Date(2017, 7, 28); // начало учебного года
	var options = {
	  year: 'numeric',
	  month: 'long',
	  day: 'numeric',
	  weekday: 'long',
	  timezone: 'UTC'
	};
	date_pl.innerHTML = "Cегодня "+ datee.toLocaleString("ru", options);
	week_pl.innerHTML = parseInt((datee - weke)/(24*3600*1000*7) + 1) + " неделя";
}

// загрузка списка дисциплин
function updateDisciplines() {
	getRequest(host + "/get?data=disciplines&uid=" + uid, discHandler);
}

function fillOption(data, select, emptyField=null){
    if (emptyField){
	    var option = document.createElement("option");
	    option.id = -1;
	    option.innerHTML = emptyField;
		select.appendChild(option);
	}
	for (let key in data) {
	    let value = data[key];
	    var option = document.createElement("option");
	    option.id = value["id"];
	    option.innerHTML = value["name"];

		select.appendChild(option);
	}
}

function discHandler(data) {
	disc_list = document.getElementById("dselec")
	disc_list.innerHTML = "";

    fillOption(data, disc_list, "Выберите дисциплину");
}

// загрузка групп преподавателя по выбранному предмету
function updateGroups(disc_id) {
	getRequest(host + "/get?data=groups&discipline_id=" + disc_id + "&uid=" + uid, groupHandler);
}

function groupHandler(data) {
	gr_list = document.getElementById("gselec")
	gr_list.innerHTML = "";

    fillOption(data, gr_list, "Выберите группу");
}

// показывает посещаемость данного студента
function updateVisitations(disc_id) {
    if (disc_id!=-1) getRequest(host + "/get?data=table&discipline_id=" + disc_id + "&uid=" + uid+"&user_type=0", tableHandler2);
}

function fillRow(tr, head, data, style, end) {
    td = document.createElement('th');

    td.className = "studname";
    td.innerHTML = head;

    tr.appendChild(td);

    for (var i=0; i<data.length; i++) {
        td = document.createElement('td');

        td.innerHTML = data[i];
        if (style) {
            for (var j=0; j<style[i].length; j++) {
                td.setAttribute(style[i][j][0],style[i][j][1]);
            }
        }

        tr.appendChild(td)
    }
    if (end != null) {
        td = document.createElement('td');
        td.innerHTML = new String(end);
        tr.appendChild(td);
    }

}

function Head(table, data) {
    // шапка дат

	var dates = data.lessons.map(x=>get_date(x[0]));

    var months_dict = ['Январь',
                       'Февраль',
                       'Март',
                       'Апрель',
                       'Май',
                       'Июнь',
                       'Июль',
                       'Август',
                       'Сентябрь',
                       'Октябрь',
                       'Ноябрь',
                       'Декабрь',
                    ];
	var months = dates.map(x=>x[1]).filter((x, i, a) => a.indexOf(x)===i);
    var months_style = months.map(x=> [["colspan", dates.filter(y=>y[1]==x).length]]);
	var months_row = document.createElement('tr');
	fillRow(months_row, "Месяц", months.map(x=>months_dict[x-1]), months_style);
	table.appendChild(months_row);

    var days = dates.map(x=>x[0]);
	var days_row = document.createElement('tr');
	fillRow(days_row, "Число", days);
	table.appendChild(days_row);

    // шапка номеров пар
	//var para = document.createElement('tr');
	//fillRow(para, "Номер пары", data.lessons.map(x=>x[0]%10));
	//table.appendChild(para);

    // шапка типов пар
	var lesson_type = document.createElement('tr');
	dict={"0": "Л", "1":"п", "2": "лр"}
	fillRow(lesson_type, "Тип пары", data.lessons.map(x=>dict[x[1]]));
	table.appendChild(lesson_type);
}

function verticalSum(table, data) {
    // строка итого
    var tt = 0;
    var sum = 0;
    var count = 0;
    var results = [];


	var total_line = document.createElement('tr');
	var d = data.students.reduce(function(acc, item) {
	    for (var i=0; i<item.visitations.length; i++) {
	        acc[i]+=parseInt(item.visitations[i]);
	    }
	    return acc;
	}, Array(data.lessons.length).fill(0)).map(x=> {
		if (x>=0) {
			count++;
			tt = Math.round(x/data.students.length*100);
			sum += tt;
			results.push(tt);
			return new String(tt);
		}
		else {
			return "-";
		}

	});
	fillRow(total_line, "Итого, %", d);
	table.appendChild(total_line);



	var td_sum = document.createElement('td');
	td_sum.innerHTML = Math.round(sum/count);
	total_line.appendChild(td_sum);
	return results;
}

function tableHandler2(data) {
    var table = document.createElement('table');
	table.className = "tables";


    Head(table, data);

    var raspr = [0,0,0,0,0,0,0,0,0,0];

    // данные по студентам
	visit_dict = {"-1": "\?", "0": "-", "1":"+"}
	for (var key in data.students) {
	    var student = data.students[key];
	    student_line = document.createElement('tr');

	    var head = student.last_name + " " + student["first_name"][0]+ "." + student["middle_name"][0] + ".";
	    var d = student.visitations.map(x=>visit_dict[x]);
	    var c = student.visitations.map(x=> {if (x=="0") return [["class","not_visited"]]; else if (x=="-1") return [["class","not_info"]]; else return [["class","visited"]];});

	    var lessons = student.visitations.filter(x=>x=="0" || x=="1").length;
	    var count = student.visitations.filter(x=>x=="1").length;
	    var pos = Math.round(count * 100 / lessons );

	    raspr[Math.round(pos/10)] += 1;
	    fillRow(student_line, head, d, c, pos);
	    table.appendChild(student_line);
	}

	var results = [];
	var results2 = [];
	var results3 = [];

	// грязный хак!
    if (user_type == 1) {
    	results = verticalSum(table, data);


        for (var i = 0; i < results.length; i++) {
        	results2.push("");
        }

        for (var i = 0; i < results.length; i++) {
        	sum = 0;
        	for (var j = 0; j<=i; j++) sum+= results[j];
        	results3.push((sum/(i+1)));
        }
    }


    //отрисовка таблицы
	var parent = document.getElementById("place_for_table");
	parent.innerHTML = "";

	//var title = document.createElement("h3");
	//title.innerHTML = "График";
	//title.align = "center";
	//parent.appendChild(title);

	parent.appendChild(table);
	createLegend();
	if (user_type == 1) {
		var ch = document.getElementById("option-one");
		if (ch.checked) {
			professorPlots(results2, results, results3, raspr);
		}
		else {
			var place_for_stat = document.getElementById("stata");
			place_for_stat.innerHTML = "";
		}
	}
}

function createLegend() {
	var parent = document.getElementById("place_for_legend");
	parent.innerHTML = "";

	var title = document.createElement("h3");
	title.innerHTML = "Обозначения";
	title.align = "center";
	parent.appendChild(title);

	var legend_table = document.createElement('table');
	legend_table.className = "tables";
	legend_table.innerHTML =
		"<tr><td class = \"visited\" style = \"width: 20px;\">+</td><td>посетил занятие</td>"
	+ 	"<td class = \"not_visited\" style = \"width: 20px;\">-</td><td>пропустил занятие</td>"
	+	"<td class = \"not_info\" style = \"width: 20px;\">?</td><td>нет данных</td></tr>"
	+   "<tr><td style = \"width: 20px;\">Л</td><td>Лекционное занятие</td>"
	+ 	"<td style = \"width: 20px;\">п</td><td>Практическое занятие</td>"
	+	"<td style = \"width: 20px;\">лр</td><td>Лабораторная работа</td></tr>";

	parent.appendChild(legend_table);
}

function studentReq(gr_id) {

	getRequest(host+"/get?data=table&group_id="+gr_id+"&uid="+uid+"&user_type=1", tableHandler2);
}

function createNews(content) {
	var title = document.createElement("h2");
	title.innerHTML = "Новости родного ВУЗа";
	title.align = "center";
	content.appendChild(title);


	for (var i = 0; i <5; i++) {
		var subtitle = document.createElement("h3");
		subtitle.innerHTML = "Lorem ipsum";
		content.appendChild(subtitle);

		var what = document.createElement("p");
		what.setAttribute("text-align","justify");
		what.innerHTML = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed lectus orci, condimentum ut tincidunt in, vehicula at arcu. Nam ut ligula dui. Vestibulum gravida ipsum ut nisi imperdiet blandit. Donec placerat lorem ac dolor ornare accumsan. Proin massa nisl, viverra at nisi sit amet, posuere commodo tortor. Nunc tincidunt et quam vitae tristique. Nulla ante eros, ultricies ut luctus sed, blandit eget magna. Suspendisse vehicula vel leo ut ornare. Mauris gravida velit tincidunt nulla vestibulum, quis venenatis ligula lacinia.";
		content.appendChild(what);
	}
	parent.location.hash = "user:news";
}

function getCookie(name) {
	var matches = document.cookie.match(new RegExp(
	"(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
	));
	return matches ? decodeURIComponent(matches[1]) : undefined;
}

function createVisitBody(content)
{
    console.log(uid);
	var title = document.createElement("h2");
	title.innerHTML = "Таблица посещаемости";
	title.align = "center";
	content.appendChild(title);

	var what = document.createElement("p");
	what.setAttribute("text-align","justify");
	what.innerHTML = "Благонадёжный студент нашего университета должен в обязательном порядке посещать все занятия, в противном случае он будет сурово наказан. Он будет неаттестован, а его родителей вызовут к Ректору и унизят. Особо злостных нарушителей могут даже исключить из вуза, так что их жизнь будет полностью разрушена и они опустятся на социальное дно нашего общества. Поэтому не стоит прогуливать пары, особенно лекции.";
	content.appendChild(what);

}

function createVisits(content) {
	createVisitBody(content);

	var fo = document.createElement("form");
	fo.className = "pure-form pure-form-stacked";

	var disci = document.createElement("fieldset");

	var dlabel = document.createElement("label");
	dlabel.setAttribute("for", "dselec");
	dlabel.innerHTML = "Выбор дисциплины"

	var dselec = document.createElement("select");
	dselec.id = "dselec";

	dselec.onchange = function() {
		var disc_id = dselec.options[dselec.selectedIndex].id;
		console.log(disc_id);
		if (disc_id!=-1) updateVisitations(disc_id);
	};

	content.appendChild(disci);
	updateDisciplines();

	disci.appendChild(dlabel);
	disci.appendChild(dselec);
	fo.appendChild(disci);
	content.appendChild(fo);


	var place = document.createElement("div");
	place.align = "center";
	place.id = "place_for_data";

	var place_table = document.createElement("div");
	place_table.id = "place_for_table";
	place.appendChild(place_table);

	var place_leg = document.createElement("div");
	place_leg.id = "place_for_legend";
	place.appendChild(place_leg);

	content.appendChild(place);

}

function createVisitsProf(content) {
	createVisitBody(content);

	var fo = document.createElement("form");
	fo.className = "pure-form";

	var disci = document.createElement("fieldset");

	var dlabel = document.createElement("label");
	dlabel.setAttribute("for", "dselec");
	dlabel.innerHTML = "Дисциплина";

	var dselec = document.createElement("select");
	dselec.id = "dselec";
	dselec.className = "selec";

	var glabel = document.createElement("label");
	glabel.setAttribute("for", "gselec");
	glabel.innerHTML = "Группа";


	var gselec = document.createElement("select");
	gselec.id = "gselec";
	gselec.className = "selec";

	var opt = document.createElement('option');
	opt.value = -1;
	opt.innerHTML = "Выберите группу";
	gselec.appendChild(opt);
	gselec.disabled = true;


	var chb = document.createElement('label');
	chb.className = "pure-checkbox cheb";
	chb.setAttribute("for","option-one");
	chb.innerHTML = "<input id=\"option-one\" type=\"checkbox\" value=\"\">Показывать статистику";

	dselec.onchange = function() {
		gselec.disabled = false;
		var disc_id = dselec.options[dselec.selectedIndex].id;
		console.log(disc_id);
		updateGroups(disc_id);
	};

	gselec.onchange = function() {
		gselec.disabled = false;
		var gr_id = gselec.options[gselec.selectedIndex].id;
		console.log(gr_id);
		studentReq(gr_id);
	};

	content.appendChild(disci);
	updateDisciplines();

	disci.appendChild(dlabel);
	disci.appendChild(dselec);
	disci.appendChild(glabel);
	disci.appendChild(gselec);

	fo.appendChild(disci);
	disci.appendChild(chb);
	content.appendChild(fo);

	var place = document.createElement("div");
	place.align = "center";
	place.id = "place_for_data";

	var place_table = document.createElement("div");
	place_table.id = "place_for_table";
	place.appendChild(place_table);

	var place_leg = document.createElement("div");
	place_leg.id = "place_for_legend";
	place.appendChild(place_leg);

	var place_for_stat = document.createElement('div');
	place_for_stat.id = "stata";
	place_for_stat.className = "small_chart";
	place.appendChild(place_for_stat);

	content.appendChild(place);

}

function createTabs(content, tabLineRule, tabRules){ //tabRule [{name:str, load:funciton}]
	function switcher (btn) {

		return function() {
			tabs.forEach(x=>x.deactivate());
			btn.activate();
		}
	}

	var tabLine = document.createElement("div");

	tabLine.className = "tab";
	var tabs = [];

	tabRules.forEach(x=>{
		var tab = document.createElement("button");
		tabLine.appendChild(tab);
		var loaded = false;

		var placer = document.createElement("div");

		tab.innerHTML = x["name"];
		tab.onclick = switcher(tab);
		tab.deactivate = ()=>{
			placer.style.display ="none";
			tab.className="";
		}
		tab.activate = ()=>{
			placer.style.display ="";
			if (!loaded)
			{
				x["load"](placer);
				loaded=true;
			}
			tab.className="active";
		};
		tabs.push(tab);
	});

	content.appendChild(tabLine);
}

function showVisitsAdmin(content)
{
	createTabs(content, {}, [
	{
		name:"Общая статистика",
		load: function(place) {

			getRequest("/get?data=total&uid="+uid, function(data){
				data = data.map(x=>{return {"id":x["id"], "%":parseFloat(x["%"]), "name":x["name"]}}); //parse % to float
				data = data.sort((x,y)=>y["%"]-x["%"]); // sort all data

				place.align = "center";
				place.id = "place_for_data";

				var place_for_stat = document.createElement('div');
				place_for_stat.id = "stata";
				place_for_stat.className = "small_chart";
				place.appendChild(place_for_stat);

				place_for_stat.innerHTML = "";

				var title = document.createElement('h2');
				title.innerHTML = "Статистика";
				title.align = "center";
				place_for_stat.appendChild(title);

				var canv = document.createElement('canvas');
				place_for_stat.appendChild(canv);

				var ctx = canv.getContext('2d');
				var myChart = new Chart(ctx, {
					type: 'line',
				    data: {
				        labels: data.map(x=>data.reduce((total, y)=>{ return (y["%"]>x["%"]?total+=1:total);}, 1)),
				        datasets: [{
				            label: 'Посещаемость0',
				            data: data.map(x=>parseFloat(x["%"])),
				            backgroundColor:
				                'rgba(255, 87, 34, 0.3)',
				            borderColor:
				                'rgba(230,74,25,1)',
				            borderWidth: 2,
				            fill: true
				        }]
				    },
				    events: "click",
				    options: {
				    	tooltip: {
				    		mode: 'nearest'
				    	},
		                responsive: true,
		                legend: {
		                    position: 'bottom',
		                },
		                hover: {
		                    mode: 'label'
		                },
		                scales: {
		                    xAxes: [{
		                            display: true,
		                            scaleLabel: {
		                                display: true,
		                                labelString: 'Группы'
		                            }
		                        }],
		                    yAxes: [{
		                            display: true,
		                            ticks: {
		                                beginAtZero: true,
		                                steps: 10,
		                                stepValue: 5,
		                                max: 100
		                            },
		                            scaleLabel: {
		                            	display: true,
		                            	labelString: "Процент посещений"
		                            }
		                        }]
		                },
		                title: {
		                    display: true,
		                    text: 'Посещаемость1'
		                },

		            }
				});

				var table_place = document.createElement('div');
				table_place.id="admin_table";
				place.appendChild(table_place);

				canv.onclick = function(evt) {
		        	console.log(data[myChart.getElementsAtEvent(evt)[0]._index]) // данные нажатой точки
		        	adminGroupsTable(myChart.getElementsAtEvent(evt)[0]._index, data)
				};

				content.appendChild(place);
			});
		}
	},
	{
		name:"Статистика по курсам",
		load: function() {

		}
	}]);
}


function adminGroupsTable(index, data) {
	var table_place = document.getElementById('admin_table');
	table_place.innerHTML="";

	var table = document.createElement('table');

	//head
	var tr = document.createElement('tr');
	var fields = [
		["Позиция",
			function (x,i, td) {
				td.innerHTML = data.length-i;
			}],
		["Название группы",
			function (x,i, td) {
				td.innerHTML = x["name"]
			}],
		["Процент посещений",
			function (x,i, td) {
				td.innerHTML = x['%'].toFixed(1);
				td.parentNode.onclick = showStudentsOfGroupHandler(table, x["id"]);
				//td.style.backgroundColor = 'rgb('+((255-x["%"])*2.55).toFixed()+','+(150+x["%"]).toFixed()+',150)';
			}]
	];
	fields.forEach(x=>{
		var td= document.createElement('td');
		td.innerHTML=x[0];
		tr.appendChild(td);
	});
	table.appendChild(tr);

	//body
	data.slice().reverse().forEach((x,i)=>{
		if (data.length-i>index) {
			var tr = document.createElement('tr');
			tr.className="adminTableRow"
			table.appendChild(tr);
			fields.forEach(y=>{
				var td = document.createElement('td');
				tr.appendChild(td)
				y[1](x,i,td);
			});
		}
	});

	table_place.appendChild(table);
}

function showStudentsOfGroupHandler(table, group_id){
	var tr = document.createElement('tr');
	var td3 = document.createElement('td');
	td3.colSpan=3;
	tr.appendChild(td3);
	tr.style.display ='none';
	tr.className = "adminTableSubRow";
	table.appendChild(tr);

	var dataLoaded = false;

	function fillSubTable(data){
		tr.style.display = '';
		var table2 = document.createElement('table');
		td3.appendChild(table2);

		//head
		var fields2 = [
			["№", function(x,i,td){
				td.innerHTML=data.length-i;
			}],
			["ФИО",function(x,i,td){
				td.innerHTML=x["last_name"]+" "+x["first_name"][0]+". "+x["middle_name"][0]+".";
			}],
			["Посещаемость",function(x,i,td){
				td.innerHTML=x["%"].toFixed(1);
			}]
		];
		var tr2 = document.createElement('tr');
		fields2.forEach(f=>{
			td2 = document.createElement('td');
			td2.innerHTML = f[0];
			tr2.appendChild(td2);
		});
		table2.appendChild(tr2);

		//body
		data.sort((x,y)=>x["%"]-y["%"]).forEach((x,i)=> {
			var tr2 = document.createElement('tr');
			tr2.className="adminSubTableRow";
			fields2.forEach(y=>{
				var td2 = document.createElement('td');
				y[1](x,i,td2);
				tr2.appendChild(td2);
			});
			table2.appendChild(tr2);
		});
		dataLoaded=true;
	}

	var group_id = group_id;

	return function() {
		if (!dataLoaded) getRequest("/get?data=groups_of_total&uid="+uid+"&group_id="+group_id, fillSubTable);
		else if (tr.style.display =='none') {
			tr.style.display ='';
		}else {
			tr.style.display ='none';
		}
	}
}

function downloadSettings(placer) {
	loadJS("file/settings.js", () => settings(placer));
}


function loadJS(url, onload) {
	var scriptTag = document.createElement('script');
    scriptTag.src = url;

    scriptTag.onload = onload;
    //scriptTag.onreadystatechange = implementationCode;

    document.head.appendChild(scriptTag);
}


function updateContent(params) {

	Object.keys(contents).forEach(x=>contents[x].placer.style.display="none");

	switch (params) {
		case "visits":
			if (!contents["visits"].created){
				if (user_type == "2" || user_type == 2) showVisitsAdmin(contents["visits"].placer);
				else if (user_type == "1" || user_type == 1) createVisitsProf(contents["visits"].placer);
				else createVisits(contents["visits"].placer);
				contents["visits"].created=true;
			}
			contents["visits"].placer.style.display="block";
			break;
		case "news":
			if (!contents["news"].created) {
				createNews(contents["news"].placer);
				contents["news"].created=true;
			}
			contents["news"].placer.style.display="block";
			break;
		case "settings":
			if (!contents["settings"].created) {
				downloadSettings(contents["settings"].placer);
				contents["settings"].created=true;
			}
			contents["news"].placer.style.display="block";
		case "exit":
		    contents={};
		    exit();
		    break;
		default:
			if (!contents["default"].created) {
				contents["default"].innerHTML="Тут ничего пока нет!";
				contents["default"].created=true;
			}
			contents["default"].placer.style.display="block";
	}
}

var contents ={};


app.page("user", function() {

	host = "";
	// host = "http://127.0.0.1:5000"
	uid = getCookie("uid");
	user = getCookie("user");
	user_type = getCookie("user_type");

	var mainContent = document.getElementById("content");
	var contentNames = ["visits", "news", "settings", "default"];
	contentNames.forEach(x=>{
		var temp=document.createElement("div");
		mainContent.appendChild(temp);
		temp.id=contentNames+"Placer";
		contents[x]={
			placer:temp,
			created:false
		}
	});

	var loaderPlace = document.createElement('div');
	loaderPlace.id="loadingPlace";
	mainContent.appendChild(loaderPlace);

	// возвращает обработчик, срабатывающий при каждом открытии секции
	return function(params) {
		updateMenu(params);
		updateUserInfo()
		updateContent(params);
	}
});


function professorPlots(data1, data2, data3, raspr) {
	var place_for_stat = document.getElementById("stata");
	place_for_stat.innerHTML = "";

	var title = document.createElement('h2');
	title.innerHTML = "Статистика";
	title.align = "center";
	place_for_stat.appendChild(title);

	var canv = document.createElement('canvas');
	place_for_stat.appendChild(canv);

	var canv2 = document.createElement('canvas');
	place_for_stat.appendChild(canv2);

	var ctx = canv.getContext('2d');
	var myChart = new Chart(ctx, {
	    type: 'line',
	    data: {
	        labels: data1,
	        datasets: [{
	            label: 'Посещаемость',
	            data: data2,
	            backgroundColor:
	                'rgba(255, 87, 34, 0.3)',
	            borderColor:
	                'rgba(230,74,25,1)',
	            borderWidth: 1,
	            fill: true
	        },
	        {
	            label: 'Средняя посещаемость',
	            data: data3,
	            backgroundColor:
	                'rgba(66, 66, 66, 1)',
	            borderColor:
	                'rgba(66, 66, 66, 1)',
	            borderWidth: 1,
	            fill: false
	        }]
	    },
	    options: {
	        scales: {
	        	xAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Занятия'
                            }
                        }],
	            yAxes: [{
	                ticks: {
	                    beginAtZero:true
	                },
	                scaleLabel: {
                            	display: true,
                            	labelString: "Процент посещений"
                            }
	            }]
	        }
	    }
	});

	var ctx2 = canv2.getContext('2d');
	var myChart2 = new Chart(ctx2, {
	    type: 'bar',
	    data: {
	        labels: ["<10","10-20","20-30","30-40","40-50","50-60","60-70","70-80","80-90",">90"],
	        datasets: [{
	            label: 'Распределение по посещаемости',
	            data: raspr,
	            backgroundColor:
	                'rgba(31, 169, 244, 0.3)',
	            borderColor:
	                'rgba(3,155,229,1)',
	            borderWidth: 1
	        }]
	    },
	    options: {
	        scales: {
	        	xAxes: [{
                            display: true,
                            scaleLabel: {
                                display: true,
                                labelString: 'Процент посещений'
                            }
                        }],
	            yAxes: [{
	                ticks: {
	                    beginAtZero:true
	                },
	                scaleLabel: {
                            	display: true,
                            	labelString: "Количество студентов"
                            }
	            }]
	        }
	    }
	});
}




// Вспомогательный код для таблички!

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

    day=(date/10)%10
    week=date/100

    start.setDate(start.getDate()+ week*7+(day-start_day));
    return [start.getDate(), start.getMonth()+1];
}

// подсчёт количества объектов в словаре
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
