function request_table()
{
    xhr= new XMLHttpRequest()
    xhr.open("POST", "get_data_for_table", true)
    xhr.setRequestHeader('Content-Type', 'multipart/form-data')
    // TODO: какой то баг, событие вызывается два раза во время работы страницы
    xhr.onreadystatechange = function()
    {

        if (xhr.status==200)
        {
            if (!created)
            {
                create_table(xhr.responseText)
                created=true
            }
        }
        else
        {
            document.getElementById("table_place").innerHTML +="error "+xhr.status
        }
    }
    xhr.send()
}

window.onload+=request_table();

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


function contains(data, student_id, lesson_id)
{
    for (var i=0; i<data.length; i++)
    {
        if (data[i][0]==student_id && data[i][1]==lesson_id)
            return true
    }
    return false
}



function get_date(date)
{
    date2 = new Date();
    var current_year= date2.getFullYear();
    var month_start=1;
    if (date2.getMonth()>=8) month_start=8

    var start= new Date(current_year, month_start, 1);
    var start_week = start.getWeek();
    var start_day=start.getDay();

    lesson=date%10
    day=Math.floor(date/10)%10
    week=Math.floor(date/100)

    start.setDate(start.getDate()+ week*7+(start_day-day))
    return start.getDay()+'.'+(start.getMonth()+1)+'.'+start.getFullYear()+' '+["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][start.getDay()]+'\n lesson #'+lesson
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

var created = false
function create_table(values)
{
    values=JSON.parse(values)

    head = document.getElementById("table_head")
    head.innerHTML = "Professor: "+values["professor_name"][0]+' '+values["professor_name"][1]+' '+values["professor_name"][2]+', '
    head.innerHTML +='Discipline: '+values['discipline_name']+', '
    head.innerHTML +='Group: '+values['group_name']

    row_count = count(values["students"]);
    students = values["students"];
    col_count = values["lessons"].length;
    lessons = values["lessons"]
    data = values["data"];


    // create elements <table> and a <tbody>
    var p = document.getElementById("table_place");
    p.style.fontSize="11px"
    var tbl     = document.createElement("table");
    var tblBody = document.createElement("tbody");
    var table = document.createElement('table');

    for (var row = 0; row <row_count+1;row++)
    {
        var total=0
        var tblrow = document.createElement("tr");
        for (col = 0; col < col_count+2; col++)
        {
            var cell = document.createElement("td");
            var cellText=document.createTextNode("")
            if (row==0)
            {
                if (col==0)
                {
                }
                else if (col>0 && col<col_count+1)
                {
                     cellText=document.createTextNode(get_date(lessons[col-1][1]))
                     cell.setAttribute('font-size',11)
                }
                else
                {
                    cellText=document.createTextNode("ИТОГО")
                }
            }
            else
            {
                if (col==0)
                {
                    cellText= document.createTextNode(students[row-1+'']["name"][1]+' '+students[row-1+'']["name"][0][0]+'.'+students[row-1+'']["name"][2][0]+'.')
                }
                else if (col<col_count+1)
                {
                    if (contains(data,students[(row-1)+'']["id"], lessons[col-1][0]))
                    {
                        cellText=document.createTextNode('+');
                        cell.setAttribute("bgcolor", "#c9ffc6")
                        total+=1
                    }
                    else
                    {
                        cellText=document.createTextNode('-');
                        cell.setAttribute("bgcolor", "#ffbfbf")
                    }
                }
                else
                {
                    cellText=document.createTextNode(Math.round(total/(col_count)*100)+'%')
                }
            }
            cell.appendChild(cellText);
            tblrow.appendChild(cell);
        }
        tblBody.appendChild(tblrow)
    }
    // append the <tbody> inside the <table>
    tbl.appendChild(tblBody);
    // put <table> in the <body>
    p.appendChild(tbl)
    // tbl border attribute to
    tbl.setAttribute("border", "2");

}