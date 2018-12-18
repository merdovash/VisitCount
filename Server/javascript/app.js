var data = [{
        title: "Автоматизированная система сбора, хранения и рассылки информации о посещениях занятий обучающимися",
        desc: "Система предназанчена для контроля посещений занятий студентами. Основой проекта является автоматизированная рассылка оповещений о пропусках занятий студентами. \n Автоматизация сбора достигается путем использования смарт-карт и специального ПО с RFID-считывателем.",
        btnName: "Перейти к проекту",
        author: "Щекочихин В.П.",
        professor: "Евстигнеев В.А.",
        url: "/cabinet",
    },
    {
        title: "система2",
        desc: "описание системы",
        btnName: "Перейти к проекту",
        author: ["Смировнов В.В", "Иаванов И.И."],
        url: "https://google.com"
    }
]

function goto(url) {
    function x() {
        window.location.href = url
    }

    return x
}

var VList = new Vue({
    el: "#projects",
    data: {
        items: data
    },
    methods: {
        goto: function(url) {
            window.location.href = url
        }
    }
})


//var projects=[]
// for (var i=0; i<data.length; i++) {
//     let d = document.getElementById("projects");
//     var newProject = document.createElement("div");
//     newProject.id="project"+i;
//     d.appendChild(newProject);
// 
//     projects.push(new Vue({
//         el:newProject.id,
//         data:data[i]
//     }));
// }