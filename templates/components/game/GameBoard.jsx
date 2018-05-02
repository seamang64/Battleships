import React, {Component, PropTypes} from 'react'
import ReactDOM from 'react-dom'
import $ from 'jquery'
import GameCell from './GameCell'
import Websocket from 'react-websocket'



class GameBoard extends Component {
    // initialise state variables for the component
    constructor(props) {
        super(props)
        this.state = {
            game: null,
            cells: null,
			shipyard: null,
			vertical: false,
			player_num: 0,
			cur_ship: 0,
			player_ready: false,
        }
 
        // bind functions
        this.sendSocketMessage = this.sendSocketMessage.bind(this);
        this.isPlayerTurn = this.isPlayerTurn.bind(this);
		this.shipRotate = this.shipRotate.bind(this);
		this.shipConfirm = this.shipConfirm.bind(this);
		this.getGame = this.getGame.bind(this);
		this.updateGame = this.updateGame.bind(this);
 
    }
 
    componentDidMount() {
		//get initial game information from the backend
        this.getGame()
    }
 
    componentWillUnmount() {
        this.serverRequest.abort();
    }
 
	//basic game information stored in a url along with an array containing the templates for ships to be placed
	getGame(){ 
         const game_url = 'http://127.0.0.1:8080/game-from-id/' + this.props.game_id
         this.serverRequest = $.get(game_url, function (result) {
            this.setState({ game: result.game})
			this.setState({ shipyard: result.shipyard})
        }.bind(this))
    }
   
    handleData(data) {
        //receives messages from the connected websocket
		//updates respective states accordingly
        let result = JSON.parse(data)
		if (result.game != null) {
			this.setState( {game : result.game})
		}
		if (result.shipyard != null) {
			this.setState( {shipyard : result.shipyard})
		}
		if (result.cells != null) {
			this.setState( {cells : result.cells})
		}
		if (result.player_num != null) {
			this.setState( {player_num : result.player_num})
			if (result.player_num == 1) {
				this.setState( {player_ready : this.state.game.p1_ready} )
			} else if (result.player_num == 2) {
				this.setState( {player_ready : this.state.game.p2_ready} )
			}
		}
		// if instructed to update will request updated information
		if (result.instruction == 'update') {
			this.updateGame()
		}
    }
 
    sendSocketMessage(message){
        // sends message to channels back-end
       const socket = this.refs.socket;
       socket.state.ws.send(JSON.stringify(message))
    }
	
	// check if it's the users turn
    isPlayerTurn(){
        if (this.state.player_num == this.state.game.player_turn){
            return true
        }else{
            return false
        }
    }
	
	// flips the vertical state corresponding to ship orientation during placing
	shipRotate(){
		this.setState({ vertical : !this.state.vertical})
	}
 
	// confirm a ship position and move to next ship
	// if final ship set player to be ready and wait for game start
	shipConfirm(){
		if ((this.state.player_num == 1 && (this.state.game.p1_ship_count==this.state.cur_ship+1)) || (this.state.player_num == 2 && (this.state.game.p2_ship_count==this.state.cur_ship+1))) {
			this.setState({ cur_ship: this.state.cur_ship+1})
			this.sendSocketMessage({action: 'confirm', game_id: this.props.game_id})
			if (this.state.game != null){
				if (this.state.cur_ship==this.state.game.max_ships-1) {
					this.sendSocketMessage({action: "ready_to_start", game_id: this.state.game.id});
					this.setState({ player_ready: true, cur_ship: 0});
				}
			}
			this.getGame()
		}
	}
	
	//requests game + cell + player information from backend
	updateGame(){
		this.sendSocketMessage({action: "get_cells", game_id: this.props.game_id});
		this.sendSocketMessage({action: "get_player_num", game_id: this.props.game_id});
		this.getGame();
	}
    // ----  RENDER FUNCTIONS ---- //
    // --------------------------- //
 
	//renders instructions for the player
    instruction(){
		// check the game and shipyard exist and have an opponent
        if (this.state.game != null && this.state.shipyard != null && this.state.game.p2 != null){
            // check if game finished
			if (this.state.game.winner != 0){
				// display name of winner
				if (this.state.game.winner==1){
					return <h3><span className="text-primary">{(this.state.game.p1.username)}</span> is Victorious! </h3>
				}else {
					return <h3><span className="text-primary">{(this.state.game.p2.username)}</span> is Victorious! </h3>
				}
			// if game not over and has started
			}else if((this.state.game.p1_ready && this.state.game.p2_ready)){
				//display who's turn it is
				if(this.state.game.player_turn == 1){
					return <h3>Current Turn:&nbsp;
						<span className="text-primary">{(this.state.game.p1.username)}</span>
					 </h3>
				}else{
					return <h3>Current Turn:&nbsp;
						<span className="text-primary">{(this.state.game.p2.username)}</span>
					 </h3>
				}
			// if player is ready but opponent isn't
			}else if(this.state.player_ready) {
				return <h3> Awaiting opponent ship placement. </h3>
			// if none of the above then player in ship placing phase
			}else{
				//get information on current ship being placed (length, name, number of duplicates) and display relevant instruction
				var ship_dup = this.state.shipyard.filter(x => x.id==this.state.shipyard[this.state.cur_ship].id).length
				var first_ship_dup = this.state.shipyard.findIndex(x => x.id==this.state.shipyard[this.state.cur_ship].id)
				if (ship_dup == 1) {
					return <h3>Place your {(this.state.shipyard[this.state.cur_ship].name)} ({(this.state.shipyard[this.state.cur_ship].length)})</h3>
				} else {
					return <h3>Place your {(this.state.shipyard[this.state.cur_ship].name)} ({(this.state.shipyard[this.state.cur_ship].length)}) ({(this.state.cur_ship - first_ship_dup + 1)}/{(ship_dup)})</h3>
				}
			}
		} else {
			return <h3> Waiting for an Opponent </h3>
		}
	}
	
	//renders left element below board
	eleL() {
		// player has finished placing ships display number of their ships remaining
		if (this.state.player_ready) {
			if (this.state.player_num == 1){
				return <h3> Ships Remaining: {(this.state.game.p1_ship_count)} </h3>
			}else{
				return <h3> Ships Remaining: {(this.state.game.p2_ship_count)} </h3>
			}
		// if player placing ships display a button to allow the player to rotate ship orientation
		} else if(this.state.game != null && this.state.game.p2 != null){
			return <button onClick={() => { this.shipRotate() }}>Rotate Ship</button>
		} else {
			return (<h3></h3>)
		}
	}
	
	//render right element below board
	eleR() { 
		if (this.state.game != null && this.state.game.p2 != null) {
			if (this.state.player_ready) {
				// player has finished placing ships display number of opponents ships remaining
				if (this.state.player_num == 1){
					return <h3> Ships Remaining: {this.state.game.p2_ship_count} </h3>
				}else{
					return <h3> Ships Remaining: {this.state.game.p1_ship_count} </h3>
				}
			// if player placing ships display a button to allow the player to confirm ship location
			} else {
				return <button onClick={() => { this.shipConfirm() }}>Confirm Ship Location</button>
			} 
		} else {
			return (<h3></h3>)
		}
	}
	
	// render a game board. Side corresponds to whether the board is ally (0) or enemy (1)
	renderBoard(side){
		var boardarr = [];
		if (this.state.game != null && this.state.cells != null){ //check game and cells exist
			// construct a table with each element containing a GameCell instance
			for (var y = 0; y<this.state.game.num_rows; y++) {
				var rowarr = [];
				for (var x=0; x<this.state.game.num_cols; x++) {
					//Passes game information, specific cell state and ship information to GameCell instance
					rowarr.push(<GameCell game_id={this.state.game.id} game_started={(this.state.game.p1_ready && this.state.game.p2_ready)} player_ready={this.state.player_ready} x={x} y={y} cell_side={side} cell_state={this.state.cells[side.toString()][x.toString()][y.toString()]} ship_id={this.state.shipyard[this.state.cur_ship].id} vertical={this.state.vertical} sendSocketMessage={this.sendSocketMessage} isPlayerTurn={this.isPlayerTurn}/>);
				}				
				boardarr.push(<tr key={y}>{rowarr}</tr>)
			}
			return <table><tbody>{boardarr}</tbody></table>
		} else {
			
			return <h3> Loading </h3> 
		}	
	}
	
	// Main render function controlling where different elements appear
	render(){
        return (
            <div className="row">
                <div className="col-sm-6"> 
                    {this.instruction()}
                    <table className="game">
					<thead>
						<tr>
						  <th>Your Board:</th>
						  <th>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</th>
						  <th>Enemy Board:</th>
						</tr>
					</thead>
                        <tbody>
							<tr>
								<th id="0-">
								{this.renderBoard(0)}
								</th>
								<th></th>
								<th id="1-">
								{this.renderBoard(1)}
								</th>								
							</tr>
							<tr>
								<td> <h3> <center id="t1"> {this.eleL()} </center></h3> </td> 
								<td></td>
								<td> <h3> <center id="t2"> {this.eleR()} </center></h3> </td>
							</tr>
                        </tbody>
                    </table>
                </div>
				<Websocket ref="socket" url={this.props.socket} onMessage={this.handleData.bind(this)} reconnect={true}/>
            </div>
        );
    }
}

 
export default GameBoard
