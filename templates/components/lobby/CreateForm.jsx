import React from 'react'

class CreateForm extends React.Component{
	
  constructor(props) {
      super(props)
      this.state = {
			height: 10,
			width: 10,
			size1: 1,
			size2: 1,
			size3: 1,
			size4: 1,
			size5: 1
        }

      // bind button click
     this.onCreateGameClick = this.onCreateGameClick.bind(this);
    }

    onCreateGameClick(event) {
		var ships = [this.state.size1, this.state.size2, this.state.size3, this.state.size4, this.state.size5];
		
		var message = {action: "create_game", player: this.props.player.username, height: this.state.height, width: this.state.width, shipyard: ships};
		
        this.props.sendSocketMessage({action: "create_game", player: this.props.player.username, height: this.state.height, width: this.state.width, shipyard: ships});
    }

	render() {
		return (
			<div>
				Height: <input type="number" value={this.state.height} onChange={evt => this.updateHeight(evt)}></input>
				<br></br>
				Width: <input type="number" value={this.state.width} onChange={evt => this.updateWidth(evt)}></input>
				<br></br>
				Ships of size 1: <input type="number" value={this.state.size1} onChange={evt => this.updateSize1(evt)}></input>
				<br></br>
				Ships of size 2: <input type="number" value={this.state.size2} onChange={evt => this.updateSize2(evt)}></input>
				<br></br>
				Ships of size 3: <input type="number" value={this.state.size3} onChange={evt => this.updateSize3(evt)}></input>
				<br></br>
				Ships of size 4: <input type="number" value={this.state.size4} onChange={evt => this.updateSize4(evt)}></input>
				<br></br>
				Ships of size 5: <input type="number" value={this.state.size5} onChange={evt => this.updateSize5(evt)}></input>
				<br></br>
				<a href="#" className="pull-right badge" onClick={this.onCreateGameClick} id="create_game">Start New Game</a>
			</div>
		)
    }
	
	updateHeight(evt) {
		this.setState({
			height: evt.target.value
		});
	}
	
	updateWidth(evt) {
		this.setState({
			width: evt.target.value
		});
	}
	
	updateSize1(evt) {
		this.setState({
			size1: evt.target.value
		});
	}
	
	updateSize2(evt) {
		this.setState({
			size2: evt.target.value
		});
	}
	
	updateSize3(evt) {
		this.setState({
			size3: evt.target.value
		});
	}
	
	updateSize4(evt) {
		this.setState({
			size4: evt.target.value
		});
	}
	
	updateSize5(evt) {
		this.setState({
			size5: evt.target.value
		});
	}
}

CreateForm.defaultProps = {

};

CreateForm.propTypes = {
    //game_list: React.PropTypes.array,
    //player: React.PropTypes.object
};


export default CreateForm
