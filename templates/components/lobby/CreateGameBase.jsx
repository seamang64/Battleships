import React from 'react';
import ReactDOM from 'react-dom';
import Websocket from 'react-websocket'
import $ from 'jquery'
import CreateForm from './CreateForm'

class LobbyBase extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
			bot: false
        }

        // bind button click
        this.sendSocketMessage = this.sendSocketMessage.bind(this);
    }

    componentDidMount() {
    }

    componentWillUnmount() {
        this.serverRequest.abort();
    }

    handleData(data) {
        //receives messages from the connected websocket
        let result = JSON.parse(data)
		if (result['player'] == this.props.current_user.username) {
			if (this.state.bot) {
				window.location = '/game/' + result['game'] + '/'
			}else{
				window.location = '/lobby/'
			}
		}
    }

    sendSocketMessage(message){
        // sends message to channels back-end
		const socket = this.refs.socket;
		if (message.action== "create_bot_game") {
			this.setState({bot: true})
		}
        socket.state.ws.send(JSON.stringify(message));
    }
	
	getValue(id) {
		return document.getElementById(id).value;
	}

    render() {
        return (

            <div className="row">
                <Websocket ref="socket" url={this.props.socket}
                    onMessage={this.handleData.bind(this)} reconnect={true}/>
                <div className="col-lg-4">
                    <CreateForm player={this.props.current_user}
						sendSocketMessage={this.sendSocketMessage} />
                </div>
            </div>
        )
    }
}

LobbyBase.propTypes = {
    //socket: React.PropTypes.string
};

export default LobbyBase;
