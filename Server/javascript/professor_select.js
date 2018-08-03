function onload_page()
{
    if (get_cookie('professor_id'))
    {
        document.getElementById('professor_id').value=get_cookie('professor_id')
        if (get_cookie('professor_locked') && get_cookie('professor_locked')=="true")
            document.getElementById('professor_id').readOnly=true
        show_disciplines()
    }
}

onload_page()

function show_disciplines()
{
    xhr3 = new XMLHttpRequest()
    xhr3.open("GET", "get_disciplines_list:"+document.getElementById("professor_id").value, true)
    xhr3.setRequestHeader('Content-Type', 'multipart/form-data')
    xhr3.onreadystatechange = function()
    {
        if (xhr3.status == 200)
        {
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
                select.setAttribute("onchange","show_groups()")

            }

            document.getElementById("discipline_id").innerHTML="Выберите дисциплину"

            t=xhr3.responseText
            //alert(t)
            data = JSON.parse(t)
            //alert(JSON.parse(data))
            discipline_id = document.getElementById("discipline_id")

            fill_select(data, select)

            discipline_id.appendChild(select)
        }
    }
    xhr3.send()
    groups={}
}

function get_cookie(cookie_name) {
    var results = document.cookie.match ('(^|;) ?' + cookie_name + '=([^;]*)(;|$)');
    return results ? decodeURIComponent(results[2]) : null;
}

function fill_select(data, select)
{
    for (var i in data)
    {
        //alert(data[i])
        option = document.createElement('option')
        option.value=data[i]["id"]
        option.innerHTML=data[i]["name"]

        select.appendChild(option)
    }
}


var groups;
function show_groups()
{
    disciplines=document.getElementById("select_discipline_id")
    discipline_id=disciplines[disciplines.selectedIndex].value

    var select = document.getElementById("select_group_id")
    if (!select)
    {
        select = document.createElement("select")
        select.setAttribute("name","select_group_id")
        select.setAttribute("id","select_group_id")
        document.getElementById("group_id").innerHTML="Выберите дисциплину"
        document.getElementById("group_id").appendChild(select)
    }
    else
    {
        while(select.firstChild)
        {
            select.removeChild(select.firstChild)
        }
    }

    if (groups[discipline_id])
    {
        group_list = groups[discipline_id]

        fill_select(group_list,select)
        show_students()
    }
    else
    {
        professor_id=document.getElementById("professor_id").value
        xhr4 = new XMLHttpRequest()
        xhr4.open("GET", "get_groups_list:"+professor_id+":"+discipline_id, true)
        xhr4.setRequestHeader('Content-Type', 'multipart/form-data')
        xhr4.onreadystatechange = function() {
            if (xhr4.status == 200)
            {
                t=xhr4.responseText
                data = JSON.parse(t)

                groups[discipline_id]=data

                show_groups()
            }
        }
        xhr4.send()
    }
}

function show_students()
{
    students_field=document.getElementById("students")

    p1= document.createElement("p")
    students_field.appendChild(p1)

    radio_all = document.createElement("input")
    radio_all.setAttribute("name","select_students")
    radio_all.setAttribute("type","radio")
    radio_all.setAttribute("value","all")
    radio_all.setAttribute("onchange","hide_list_of_students()")
    p1.appendChild(radio_all)
    p1.innerHTML+="Все"

    p2 = document.createElement("p")
    students_field.appendChild(p2)

    radio_select = document.createElement("input")
    radio_select.setAttribute("name","select_students")
    radio_select.setAttribute("type","radio")
    radio_select.setAttribute("value","select")
    radio_select.setAttribute("onchange","show_list_of_students()")
    p2.appendChild(radio_select)
    p2.innerHTML+="Выбрать"

}

function show_list_of_students()
{
    group_id=document.getElementById("select_group_id")[document.getElementById("select_group_id").selectedIndex].value

    xhr2 = new XMLHttpRequest()
    xhr2.open("GET", "get_students_list_of_group:"+group_id, true)
    xhr2.setRequestHeader('Content-Type', 'multipart/form-data')

    xhr2.onreadystatechange = function()
    {
        if (xhr2.status="200")
        {

            student_list_field=document.getElementById("students_list")

            data = xhr2.responseText
            data=JSON.parse(data)
            for (var i in data)
            {
                student=data[i]

                p = document.createElement("p")
                student_list_field.appendChild(p)

                check_box=document.createElement("input")
                p.appendChild(check_box)

                check_box.setAttribute("type","checkbox")
                check_box.setAttribute("name","students")
                check_box.setAttribute("value", student["id"])
                p.innerHTML+=student["name"][1]+" "+student["name"][0][0]+'.'+student["name"][2][0]+'.'
            }
        }
    }

    xhr2.send()
}

function hide_list_of_students()
{
    student_list_field= document.getElementById("students_list")
    while (student_list_field.firstChild) student_list_field.removeChild(student_list_field.firstChild)
}