function init_table(container_id, data, params) {
    //data={column1_name: [], column2_name: []}

    var container = document.getElementById(container_id);

    var table = new Table(container);

    var header_names = Object.keys(data);
    table.setHeader(header_names, params['header']);

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
        this.cache_rule = x => true;

        if (params == null || params['type'] == null) {
            this.type = 'input';
        } else {
            this.type = params['type'];
        }

        this.make_dom(this.type);
        this.filter_row = parent;
    }

    make_dom() {
        if (this.type == 'input') {
            this.dom = document.createElement('input');
            this.dom.setAttribute('type', 'text');
            this.dom.oninput = e => {
                this.dom = e.target
                this._rule = e.target.value;
                this.cache_rule = this.input_rules()
                this.filter_row.change();
                e.target.focus();
            };
        } else if (this.type == 'select') {
            this.dom = document.createElement('select');
            this.dom.onchange = e => {
                this.dom = e.target;
                this._rule = e.target.value;
                this.cache_rule = this.select_rule();
                this.filter_row.change();
                e.target.focus();
            }
            this.items = [];
            this.new_option('Все');
        }
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
        this.dom.appendChild(option);
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

    rowAdded(row) {
        this.items.forEach((item, index) => {
            item.rowAdded(row.data[index]);
        });
    }

    render() {
        this.dom.innerHTML = "";
        for (var i = 0; i < this.items.length; i++) {
            var filter_el = document.createElement('td');
            filter_el.appendChild(this.items[i].render());

            this.dom.appendChild(filter_el);
        }
        return this.dom;
    }
}

class Table {
    constructor(parent) {
        this.container = parent
        this.dom = document.createElement('table');
        this.header_row_items = [];
        this.columns = [];
        this.rows = [];
        this.rendered = false;
    }

    setHeader(names, params) {
        this.filterRow = new FilterRow(this, names.length, params['filter']);
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
            this.container.innerHTML = "";
            this.dom.innerHTML = "";

            this.dom.appendChild(this.headerRow.render());
            this.dom.appendChild(this.filterRow.render());
            this.rendered = true;
        } else {
            var count = this.dom.getElementsByTagName('tr').length;
            for (var i = 2; i < count; i++) {
                this.dom.removeChild(this.dom.getElementsByTagName('tr')[2]);
            }
        }

        var rules = this.filterRow.get_rules();

        for (var i = 0; i < this.rows.length; i++) {
            var row = this.rows[i];
            if (row.check(rules)) {
                this.dom.appendChild(row.render())
            }
        }

        this.container.appendChild(this.dom)
    }
}