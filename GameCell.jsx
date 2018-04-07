import React, {Component, PropTypes} from 'react'
 
const sea_img = <img src="/static/img/sea.png" />
const unknown_img = <img src="/static/img/unknown.png" />
const ship_img = <img src="/static/img/ship.png" />
const ship_hit_img = <img src="/static/img/ship_hit.png" />
const ship_sunk_img = <img src="/static/img/ship_sunk.png" />
 
class GameCell extends Component {
    constructor(props) {
        super(props)
        this.state = {
			game_id: props.game_id,
			game_started: props.game_started,
			player_ready: props.player_ready,
            cell_side: props.cell_side,
			cell_state: props.cell_state,
			cell_x: props.x,
			cell_y: props.y,
			ship_id: props.ship_id,
			vertical: props.vertical,
        }
        this.cellClicked = this.cellClicked.bind(this)
    }

    componentWillReceiveProps(newProps){
        this.setState({
			vertical: newProps.vertical,
			cell_state: newProps.cell_state,
			ship_id: newProps.ship_id,
			game_started: newProps.game_started,
			player_ready: newProps.player_ready,
            })
    }
 
    getStatus(){ //add ship sunk
		if (this.state.cell_side == 0){ //ally board  
			if (this.state.cell_state == 'sea') {
				return sea_img
			}else if(this.state.cell_state == 'sea-fired_at') {
				return unknown_img //change this undecided how to represent
			}else if(this.state.cell_state.includes('fired_at')) {
				return ship_hit_img
			}else{
				return ship_img
			}
		}else{ //enemy board
			if (this.state.game_startedd) {alert(this.state.cell_state)}
			if (this.state.cell_state == 'unknown') {
				return unknown_img
			}else if(this.state.cell_state == 'hit') {
				return ship_hit_img
			}else {
				return sea_img
			}
		}
    }
 
    cellClicked(square){ //GAME LOGIC HERE
		if (this.state.game_started) { //if game started and cell belongs to enemy board then fire at this cell
			if (this.state.cell_side == 1) {
				if (this.props.isPlayerTurn()){
					this.props.sendSocketMessage({action: "fire", game_id: this.state.game_id, row: this.state.cell_y, col: this.state.cell_x});
				}
			}
		}else{
			if (!this.state.player_ready) {
				if (this.state.cell_side == 0) { //if player not ready then placeship at this cell (if its ally)
					this.props.sendSocketMessage({action: "remove_ship", game_id: this.state.game_id, ship_id: this.state.ship_id})
					this.props.sendSocketMessage({action: "placeship", game_id: this.state.game_id, start_row: this.state.cell_y, start_col: this.state.cell_x, ship_id: this.state.ship_id, vertical: this.state.vertical.toString()});
				}
			}
		}
		this.props.sendSocketMessage({action: "update", game_id: this.state.game_id})
    }

   
    render() {
        return (
            <td key={this.state.cell_x.toString()+'_'+this.state.cell_y.toString} onClick={this.cellClicked} height="60" width="60">
                {this.getStatus()}
            </td>
        )
    }
}
 
//GameCell.propTypes = {
    //loc_x: PropTypes.number,
    //loc_y: PropTypes.number,
    //square_id: PropTypes.number,
    //owner: PropTypes.number,
    //possession_type: PropTypes.string,
    //game_creator: PropTypes.number,
    //sendSocketMessage: PropTypes.func,
    //isPlayerTurn: PropTypes.func
//}
 
export default GameCell
