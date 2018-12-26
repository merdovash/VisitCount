function init_table(container_id, data, params) {
    //data={column1_name: [], column2_name: []}

    var container = document.getElementById(container_id);

    var table = new Table(container, params['table']);

    var header_names = Object.keys(data);
    table.setHeader(header_names, 'header' in params ? params['header'] : {});

    var row_index = 0;
    while (row_index < data[header_names[0]].length) {
        try {
            var row = [];
            for (var i = 0; i < header_names.length; i++) {
                row.push(data[header_names[i]][row_index]);
            }
            table.addRow(row);
        } catch (e) {
            if (e instanceof RangeError) {
                break;
            }
            throw e;
        } finally {
            row_index += 1;
        }
    }

    table.render();
}


class Row {
    constructor(data, type = 'td') {
        this.type = type;
        this.data = data;
        this.dom = document.createElement('tr');

        for (var i = 0; i < data.length; i++) {
            var val = data[i];
            var el = document.createElement(this.type);
            el.innerHTML = val
            this.dom.appendChild(el);
        }

    }

    check(rules) {
        for (var i = 0; i < rules.length; i++) {
            if (!rules[i](this.data[i])) {
                return false;
            }
        }
        return true;
    }

    render() {
        return this.dom;
    }
}

class Filter {
    constructor(parent, params) {
        this.filter_row = parent;
        this.dom = document.createElement('td');
        this.dom.className = "row";
        this.dom.setAttribute('style', 'margin: auto;')
        this.cache_rule = x => true;
        this.icons = {
            0: "vertical_align_center",
            1: "vertical_align_bottom",
            2: "vertical_align_top"
        }

        if (params) {
            if (params['type']) this.type = params['type'];
            if (params['order']) this.order_as = params['order'];
        }
        if (!this.type) this.type = 'input';
        if (!this.order_as) this.order_as = 'string';

        this.order_direction = 0;

        this.init_order()
        this.init_filter();
    }

    init_filter() {
        this.filter_box = document.createElement('div');
        this.filter_box.className = 'select-wrapper'
        this.filter_box.setAttribute('style', 'margin-right:30px;');
        this.dom.appendChild(this.filter_box);
        if (this.type == 'input') {
            this.filter_el = document.createElement('input');
            this.filter_box.appendChild(this.filter_el);
            this.filter_el.setAttribute('type', 'text');
            this.filter_el.oninput = e => {
                this.filter_el = e.target
                this._rule = e.target.value;
                this.cache_rule = this.input_rules()
                this.filter_row.change();
                e.target.focus();
            };
        } else if (this.type == 'select') {
            this.filter_el = document.createElement('select');
            this.filter_box.appendChild(this.filter_el);
            this.filter_el.onchange = e => {
                this.filter_el = e.target;
                this._rule = e.target.value;
                this.cache_rule = this.select_rule();
                this.filter_row.change();
                e.target.focus();
            }
            this.items = [];
            this.new_option('Все');
        }
    }

    init_order() {
        this.order_box = document.createElement('div');
        this.order_box.setAttribute('style', 'float: right; vertical-align: center;');
        this.dom.appendChild(this.order_box);
        var icon = document.createElement('i');
        this.order_box.appendChild(icon);

        icon.className = "material-icons";
        icon.innerHTML = this.icons[this.order_direction];
        icon.onclick = e => {
            this.order_direction = (this.order_direction + 1) % 3;
            icon.innerHTML = this.icons[this.order_direction];
            this.selectOrder();
            this.filter_row.sortUpdated(this)
        }
        this.icon = icon;
        this.selectOrder();
    }

    selectOrder() {
        var col = this.filter_row.items.indexOf(this);
        if (this.order_as == 'string') {
            if (this.order_direction == 1) {
                this.cache_order = (a, b) => a.data[col] < b.data[col] ? 1 : -1;
            } else if (this.order_direction == 2) {
                this.cache_order = (a, b) => a.data[col] > b.data[col] ? 1 : -1;
            } else {
                this.cache_order = (a, b) => 0;
            }
        } else if (this.order_as == 'number') {
            if (this.order_direction == 1) {
                this.cache_order = (a, b) => a.data[col] < b.data[col];
            } else if (this.order_direction == 2) {
                this.cache_order = (a, b) => a.data[col] > b.data[col];
            } else {
                this.cache_order = (a, b) => 0;
            }
        }

    }

    order() {
        return this.cache_order;
    }

    resetOrder() {
        this.order_direction = 0;
        this.icon.innerHTML = this.icons[0];
    }

    select_rule() {
        if (this._rule != '' && this._rule != this.items[0]) {
            return x => x == this._rule;
        }
        return x => true;
    }

    input_rules() {
        if (this._rule.length > 0) {
            if (['<', '>', '!'].includes(this._rule[0])) {
                if (this._rule.length > 1) {
                    var operator = this._rule[0];
                    var value = parseFloat(this._rule.substring(1));
                    if (operator == '>') {
                        return x => parseFloat(x) > value;
                    }
                    if (operator == '<') {
                        return x => parseFloat(x) < value;
                    }
                    if (operator == '!') {
                        return x => parseFloat(x) != value;
                    }
                }
            } else {
                return x => x.toString().indexOf(this._rule) != -1;
            }
        }
        return x => true;
    }

    rowAdded(value) {
        if (this.type == 'select') {
            if (!this.items.includes(value)) {
                this.new_option(value);
            }
        }
    }

    new_option(val) {
        this.items.push(val);
        var option = document.createElement('option');
        option.setAttribute('value', val);
        option.innerHTML = val;
        this.filter_el.appendChild(option);
    }

    render() {
        return this.dom
    }

    rule() {
        return this.cache_rule;
    }
}

class FilterRow {
    constructor(parent, count, params) {
        this.table = parent;
        this.count = count;
        this.dom = document.createElement('tr');

        this.sortedColumn = -1;

        this.items = [];
        for (var i = 0; i < count; i++) {
            this.items.push(new Filter(this, params[i.toString()]));
        }
    }

    change() {
        this.table.render();
    }

    get_rules() {
        return this.items.map(x => x.rule());
    }

    sortUpdated(item) {
        for (var i = 0; i < this.items.length; i++) {
            if (this.items[i] != item) {
                this.items[i].resetOrder();
            } else {
                this.sortedColumn = i;
            }
        }
        this.change();
    }

    getSort() {
        var items = this.items;
        var sortedColumn = this.sortedColumn;
        if (sortedColumn >= 0) {
            return items[sortedColumn].order();
        } else {
            return (a, b) => 0;
        }
    }

    rowAdded(row) {
        this.items.forEach((item, index) => {
            item.rowAdded(row.data[index]);
        });
    }

    render() {
        this.dom.innerHTML = "";
        for (var i = 0; i < this.items.length; i++) {
            this.dom.appendChild(this.items[i].render());
        }
        return this.dom;
    }
}

class Table {
    constructor(parent, params) {
        this.container = parent
        this.dom = document.createElement('table');
        this.header = document.createElement('thead');
        this.body = document.createElement('tbody');

        this.dom.appendChild(this.header);
        this.dom.appendChild(this.body)
        if (params) {
            if (params['style']) {
                this.dom.className = params['style']
            }
        }
        this.header_row_items = [];
        this.columns = [];
        this.rows = [];
        this.rendered = false;
    }

    setHeader(names, params) {
        this.filterRow = new FilterRow(this, names.length, 'filter' in params ? params['filter'] : {});
        this.headerRow = new Row(names, 'th');
    }

    addRow(row) {
        if (row instanceof Row) {
            this.rows.push(row);
            this.filterRow.rowAdded(row);
        } else if (row instanceof Array) {
            var _row = new Row(row);
            this.rows.push(_row);
            this.filterRow.rowAdded(_row);
        } else {
            throw TypeError(row + 'is not instance of Row');
        }
    }

    render() {
        if (!this.rendered) {
            this.header.appendChild(this.headerRow.render());
            this.header.appendChild(this.filterRow.render());
            this.rendered = true;
        } else {
            this.body.innerHTML = "";
        }

        var rules = this.filterRow.get_rules();

        var rows_afet_filter = []
        for (var i = 0; i < this.rows.length; i++) {
            var row = this.rows[i];
            if (row.check(rules)) {
                rows_afet_filter.push(row)
            }
        }

        var comparer = this.filterRow.getSort()
        var rows_after_sorting = rows_afet_filter.sort(comparer);
        for (var i = 0; i < rows_after_sorting.length; i++) {
            this.body.appendChild(rows_after_sorting[i].render())
        }

        this.container.appendChild(this.dom)
    }
}