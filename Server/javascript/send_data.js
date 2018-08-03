function send_data()
{
    var professor_id=document.getElementById("professor_id").value;
    var group_id=document.getElementById("group_id").value;
    var discipline_id=document.getElementById("discipline_id").value;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "table_professor", true)
    xhr.setRequestHeader('Content-Type', 'applications/json')
    xhr.send({"professor_id":professor_id,
              "group_id":group_id,
              "discipline_id":discipline_id
              }.toString()
             );
}