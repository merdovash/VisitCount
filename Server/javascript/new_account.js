function check_name()
{
    name = document.getElementById("login").value
    if (name.length>6)
    {
        document.getElementById("check_name_message").innerHTML="Проверка логина"

        xhr = new XMLHttpRequest()
        xhr.open("GET", "check_login:"+name, true)
        xhr.setRequestHeader('Content-Type', 'multipart/form-data')

        xhr.onreadystatechange = function()
        {
            if (xhr.status==200)
            {
                if (JSON.parse(xhr.responseText)["answer"]=="NO")
                {
                    document.getElementById("check_name_message").innerHTML="Этот логин свободен"
                }
                else
                {
                    document.getElementById("check_name_message").innerHTML="Этот логин занят"
                }
            }
        }
        xhr.send()
    }
    else
    {
        document.getElementById("check_name_message").innerHTML='Логин должен содержать как минимум 6 символов без знаков ";", ",", "="'
    }
}

function check_passwords()
{
    password1=document.getElementById("password").value
    password2=document.getElementById("password").value

    if (password1==password2 && password1.length>5)
    {
        document.getElementById("submit").disabled=false
    }else
    {
        document.getElementById("submit").disabled=true
        document.getElementById("submit_button_message").innerHTML="Пароли должны быть не менее 6 символов и совпадать."
    }
}