import React from 'react'

class PlayerGames extends React.Component{
	
  constructor(props) {
      super(props)
      this.state = {
        game_list: this.props.game_list
      }

      // bind button click
     this.onCreateGameClick = this.onCreateGameClick.bind(this);
     this.renderButton = this.renderButton.bind(this);
     this.renderOpponent = this.renderOpponent.bind(this)
    }

    onCreateGameClick(event) {
		//alert("clicked");
        this.props.sendSocketMessage({action: "create_game", player: this.props.player.username});
    }


    componentWillReceiveProps(newProp){
        this.setState({game_list: newProp.game_list})
    }

    renderButton(game){
         if (game.completed){
            return "View"
         } else if (game.p2 == null && game.p1.id == this.props.player.id){
             return "Waiting..."
         } else{
             return "Play"
         }
                                     
    }

    renderOpponent(game){
        console.log(game)
        if (game.p2 != null){
            return game.p2.username
        } else {
            return "???"
        }
    }

    renderGameList(){
        if (this.props.game_list.length > 0){
            return this.props.game_list.map(function(game){
                    return <li key={game.id} className="list-group-item">
                                <span className="badge pull-left">{game.id}</span>&nbsp;&nbsp;
                                <span>{game.p1.username}</span> vs <span>{this.renderOpponent(game)}</span>

                                <a className="btn btn-sm btn-primary pull-right" href={"/game/"+game.id+"/"}>{this.renderButton(game)}</a>
                            </li>
                    }, this)

        }else{
            return ("No Games")
        }
    }

    render() {
      return (
        <div>
          <div className="panel panel-primary">
                <div className="panel-heading">
                    <span>Your Games</span>
                    <a href="#" className="pull-right badge" onClick={this.onCreateGameClick} id="create_game">Start New Game</a>
                </div>
                <div className="panel-body">
                    <div>
                        <ul className="list-group games-list">
                            {this.renderGameList()}
                        </ul>
                    </div>
                </div>
            </div>

        </div>
      )
    }
}

PlayerGames.defaultProps = {

};

PlayerGames.propTypes = {
    //game_list: React.PropTypes.array,
    //player: React.PropTypes.object
};


export default PlayerGames
