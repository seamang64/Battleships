import React from 'react';
import LobbyBase from './LobbyBase.jsx'
import ReactDOM from 'react-dom'
import $ from 'jquery'

// lobby socket url
var lobby_sock = 'ws://' + window.location.host + "/lobby/"
// preset the current_user
var current_user = null

// renders out the base component
function render_component(){
    ReactDOM.render(<LobbyBase current_user={current_user} socket={lobby_sock}/>, document.getElementById('lobby_component'))
}


render_component()
