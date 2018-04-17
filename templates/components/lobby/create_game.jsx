import React from 'react';
import LobbyBase from './CreateGameBase.jsx'
import ReactDOM from 'react-dom'
import $ from 'jquery'

// lobby socket url
var lobby_sock = 'ws://' + window.location.host + "/ws/lobby/"
// preset the current_user
var current_user = null

// renders out the base component

$.get('http://127.0.0.1:8080/current-user/?format=json', function(result){
     //gets the current user information from Django
    current_user = result
    render_component()
})

function render_component(){
    ReactDOM.render(<LobbyBase current_user={current_user} socket={lobby_sock}/>, document.getElementById('lobby_component'))
}
