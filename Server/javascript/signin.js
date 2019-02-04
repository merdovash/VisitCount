/*** @jsx React.DOM */
import AppBar from '@material-ui/core/AppBar';


var realPython = React.createClass({
    render: function() {
      return (<h2>Greetings, from Real Python!</h2>);
    }
});

ReactDOM.render(
    React.createElement(realPython, null),
    document.getElementById('content')
);