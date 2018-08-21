var data = null;

function logOut() {
    deleteCookie('uid');
    window.location.pathname = '/visit';
}

function load() {
    function _load(d) {
        data = d

        name = new Vue({
            'el': '#username',
            'data': {
                first_name: data.user.first_name,
                last_name: data.user.last_name,
                middle_name: data.user.middle_name
            }
        });
        groupPanel();
    }

    postRequest('/user_info', { 'user': { 'uid': getCookie('uid') } }, _load)
}

load();

var groups;

function groupPanel() {
    if (groups == null) {
        getRequest("/get?data=groups&uid=" + getCookie('uid'), function(data) {
            groups = data;
            groupsList = new Vue({
                'el': '#groupField',
                'data': {
                    'items': groups
                }
            });

            table = new Vue({
                'el': '#visit_table',
                'data': {
                    dates: [],
                    visits: [],
                    rows: []
                }
            });
        });
    }
}

var groupsStat = {}

function groupSelect(id) {
    if (groupsStat[id] == null) {
        getRequest("/get?data=group_visit&group_id=" + id + "&uid=" + getCookie('uid'), function(data) {
            groupsStat[id] = data;
            drawTable(groupsStat[id]);
        })
    }
}

var table_loaded = false;

function drawTable(t) {
    console.log(t);
    if (!table_loaded) {

        table_loaded = true;
    } else {
        table.data = t;
    }
}