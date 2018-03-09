import React from 'react';
import ReactDOM from 'react-dom';
import Websocket from 'react-websocket'
import $ from 'jquery'

class LobbyBase extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            player_game_list: [],
            available_game_list: []
        }

        // bind button click
        this.sendSocketMessage = this.sendSocketMessage.bind(this);
    }

    componentDidMount() {}

    componentWillUnmount() {
        this.serverRequest.abort();
    }

    handleData(data) {
        //receives messages from the connected websocket
        let result = JSON.parse(data)
        
        
        // we've received an updated list of available games
        this.setState({available_game_list: result})
    }

    sendSocketMessage(message){
        // sends message to channels back-end
       const socket = this.refs.socket
       socket.state.ws.send(JSON.stringify(message))
    }

    render() {
        return (

            <div className="row">
                <Websocket ref="socket" url={this.props.socket}
                    onMessage={this.handleData.bind(this)} reconnect={true}/>
                <span>Lobby Components will go here....</span>
            </div>

        )
    }
}

LobbyBase.propTypes = {
    socket: React.PropTypes.string
};

export default LobbyBase;
