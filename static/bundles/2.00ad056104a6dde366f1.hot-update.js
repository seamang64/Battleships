webpackHotUpdate(2,{

/***/ 28:
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
	value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(1);

var _react2 = _interopRequireDefault(_react);

var _reactDom = __webpack_require__(8);

var _reactDom2 = _interopRequireDefault(_reactDom);

var _jquery = __webpack_require__(7);

var _jquery2 = _interopRequireDefault(_jquery);

var _GameCell = __webpack_require__(31);

var _GameCell2 = _interopRequireDefault(_GameCell);

var _reactWebsocket = __webpack_require__(25);

var _reactWebsocket2 = _interopRequireDefault(_reactWebsocket);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var GameBoard = function (_Component) {
	_inherits(GameBoard, _Component);

	// lifecycle methods
	function GameBoard(props) {
		_classCallCheck(this, GameBoard);

		var _this = _possibleConstructorReturn(this, (GameBoard.__proto__ || Object.getPrototypeOf(GameBoard)).call(this, props));

		_this.state = {
			game: null,
			cells: null,
			shipyard: null,
			vertical: false,
			player_num: 0,
			cur_ship: 0,
			player_ready: false

			// bind button click
		};_this.sendSocketMessage = _this.sendSocketMessage.bind(_this);
		_this.isPlayerTurn = _this.isPlayerTurn.bind(_this);
		_this.shipRotate = _this.shipRotate.bind(_this);
		_this.shipConfirm = _this.shipConfirm.bind(_this);
		_this.getGame = _this.getGame.bind(_this);
		_this.updateGame = _this.updateGame.bind(_this);

		return _this;
	}

	_createClass(GameBoard, [{
		key: 'componentDidMount',
		value: function componentDidMount() {
			this.getGame();
			//this.updateGame()
		}
	}, {
		key: 'componentWillUnmount',
		value: function componentWillUnmount() {
			this.serverRequest.abort();
		}

		// custom methods

	}, {
		key: 'getGame',
		value: function getGame() {
			var game_url = 'http://127.0.0.1:8080/game-from-id/' + this.props.game_id;
			this.serverRequest = _jquery2.default.get(game_url, function (result) {
				this.setState({ game: result.game });
				this.setState({ shipyard: result.shipyard });
			}.bind(this));
		}
	}, {
		key: 'handleData',
		value: function handleData(data) {
			//receives messages from the connected websocket
			var result = JSON.parse(data);
			//alert(JSON.stringify(result))
			if (result.game != null) {
				this.setState({ game: result.game });
			}
			if (result.shipyard != null) {
				this.setState({ shipyard: result.shipyard });
			}
			if (result.cells != null) {
				this.setState({ cells: result.cells });
			}
			if (result.player_num != null) {
				this.setState({ player_num: result.player_num });
			}
			if (result.instruction == 'update') {
				this.updateGame();
			}
		}
	}, {
		key: 'sendSocketMessage',
		value: function sendSocketMessage(message) {
			// sends message to channels back-end
			var socket = this.refs.socket;
			socket.state.ws.send(JSON.stringify(message));
			//alert(JSON.stringify(message))
		}
	}, {
		key: 'isPlayerTurn',
		value: function isPlayerTurn() {
			if (this.state.player_num == this.state.game.player_turn) {
				return true;
			} else {
				return false;
			}
		}
	}, {
		key: 'shipRotate',
		value: function shipRotate() {
			this.setState({ vertical: !this.state.vertical });
		}
	}, {
		key: 'shipConfirm',
		value: function shipConfirm() {
			this.setState({ cur_ship: this.state.cur_ship + 1 });
			this.sendSocketMessage({ action: 'confirm', game_id: this.props.game_id });
			//alert(this.state.cur_ship)
			if (this.state.game != null) {
				if (this.state.cur_ship == this.state.game.max_ships - 1) {
					this.sendSocketMessage({ action: "ready_to_start", game_id: this.state.game.id });
					this.setState({ player_ready: true, cur_ship: this.state.cur_ship - 1 });
				}
			}
			this.getGame();
		}
	}, {
		key: 'updateGame',
		value: function updateGame() {
			this.sendSocketMessage({ action: "get_cells", game_id: this.props.game_id });
			this.sendSocketMessage({ action: "get_player_num", game_id: this.props.game_id });
			this.getGame();
		}
		// ----  RENDER FUNCTIONS ---- //
		// --------------------------- //

	}, {
		key: 'instruction',
		value: function instruction() {
			if (this.state.game != null && this.state.shipyard != null) {
				if (this.state.game.winner != 0) {
					// game is over
					if (this.state.game.winner == 1) {
						return _react2.default.createElement(
							'h3',
							null,
							_react2.default.createElement(
								'span',
								{ className: 'text-primary' },
								this.state.game.p1.username
							),
							' is Victorious! '
						);
					} else {
						return _react2.default.createElement(
							'h3',
							null,
							_react2.default.createElement(
								'span',
								{ className: 'text-primary' },
								this.state.game.p2.username
							),
							' is Victorious! '
						);
					}
				} else if (this.state.game.p1_ready && this.state.game.p2_ready) {
					if (this.state.game.player_turn == 1) {
						return _react2.default.createElement(
							'h3',
							null,
							'Current Turn:\xA0',
							_react2.default.createElement(
								'span',
								{ className: 'text-primary' },
								this.state.game.p1.username
							)
						);
					} else {
						return _react2.default.createElement(
							'h3',
							null,
							'Current Turn:\xA0',
							_react2.default.createElement(
								'span',
								{ className: 'text-primary' },
								this.state.game.p2.username
							)
						);
					}
				} else if (this.state.player_ready) {
					return _react2.default.createElement(
						'h3',
						null,
						' Awaiting opponent ship placement. '
					);
				} else {
					return _react2.default.createElement(
						'h3',
						null,
						'Place your ',
						this.state.shipyard[this.state.cur_ship].name,
						' (',
						this.state.shipyard[this.state.cur_ship].length,
						')'
					);
				}
			}
		}
	}, {
		key: 'eleL',
		value: function eleL() {
			var _this2 = this;

			//left element below board
			if (this.state.player_ready) {
				if (this.state.player_num == 1) {
					return _react2.default.createElement(
						'h3',
						null,
						' Ships Remaining: ',
						this.state.game.p1_ship_count,
						' '
					);
				} else {
					return _react2.default.createElement(
						'h3',
						null,
						' Ships Remaining: ',
						this.state.game.p2_ship_count,
						' '
					);
				}
			} else {
				return _react2.default.createElement(
					'button',
					{ onClick: function onClick() {
							_this2.shipRotate();
						} },
					'Rotate Ship'
				);
			}
		}
	}, {
		key: 'eleR',
		value: function eleR() {
			var _this3 = this;

			//right element below board
			if (this.state.player_ready) {
				if (this.state.player_num == 1) {
					return _react2.default.createElement(
						'h3',
						null,
						' Ships Remaining: ',
						this.state.game.p2_ship_count,
						' '
					);
				} else {
					return _react2.default.createElement(
						'h3',
						null,
						' Ships Remaining: ',
						this.state.game.p1_ship_count,
						' '
					);
				}
			} else {
				return _react2.default.createElement(
					'button',
					{ onClick: function onClick() {
							_this3.shipConfirm();
						} },
					'Confirm Ship Location'
				);
			}
		}
	}, {
		key: 'renderBoard',
		value: function renderBoard(side) {
			var boardarr = [];
			if (this.state.game != null && this.state.cells != null) {
				//check game and cells exist
				for (var y = 0; y < this.state.game.num_rows; y++) {
					var rowarr = [];
					for (var x = 0; x < this.state.game.num_cols; x++) {
						rowarr.push(_react2.default.createElement(_GameCell2.default, { game_id: this.state.game.id, game_started: this.state.game.p1_ready && this.state.game.p2_ready, player_ready: this.state.player_ready, x: x, y: y, cell_side: side, cell_state: this.state.cells[side.toString()][x.toString()][y.toString()], ship_id: this.state.shipyard[this.state.cur_ship].id, vertical: this.state.vertical, sendSocketMessage: this.sendSocketMessage, isPlayerTurn: this.isPlayerTurn, fix: this.tempFix }));
					}
					boardarr.push(_react2.default.createElement(
						'tr',
						{ key: y },
						rowarr
					));
				}
				return _react2.default.createElement(
					'table',
					null,
					_react2.default.createElement(
						'tbody',
						null,
						boardarr
					)
				);
			} else {

				return _react2.default.createElement(
					'h3',
					null,
					' Loading '
				);
			}
		}
	}, {
		key: 'render',
		value: function render() {
			return _react2.default.createElement(
				'div',
				{ className: 'row' },
				_react2.default.createElement(
					'div',
					{ className: 'col-sm-6' },
					this.instruction(),
					_react2.default.createElement(
						'table',
						null,
						_react2.default.createElement(
							'thead',
							null,
							_react2.default.createElement(
								'tr',
								null,
								_react2.default.createElement(
									'th',
									null,
									'Your Board:'
								),
								_react2.default.createElement(
									'th',
									null,
									'\xA0\xA0\xA0\xA0\xA0\xA0\xA0\xA0\xA0'
								),
								_react2.default.createElement(
									'th',
									null,
									'Enemy Board:'
								)
							)
						),
						_react2.default.createElement(
							'tbody',
							null,
							_react2.default.createElement(
								'tr',
								null,
								_react2.default.createElement(
									'th',
									{ id: '0-' },
									this.renderBoard(0)
								),
								_react2.default.createElement('th', null),
								_react2.default.createElement(
									'th',
									{ id: '1-' },
									this.renderBoard(1)
								)
							),
							_react2.default.createElement(
								'tr',
								null,
								_react2.default.createElement(
									'td',
									null,
									' ',
									_react2.default.createElement(
										'h3',
										null,
										' ',
										_react2.default.createElement(
											'center',
											{ id: 't1' },
											' ',
											this.eleL(),
											' '
										)
									),
									' '
								),
								_react2.default.createElement('td', null),
								_react2.default.createElement(
									'td',
									null,
									' ',
									_react2.default.createElement(
										'h3',
										null,
										' ',
										_react2.default.createElement(
											'center',
											{ id: 't2' },
											' ',
											this.eleR(),
											' '
										)
									),
									' '
								)
							)
						)
					)
				),
				_react2.default.createElement(_reactWebsocket2.default, { ref: 'socket', url: this.props.socket, onMessage: this.handleData.bind(this), reconnect: true })
			);
		}
	}]);

	return GameBoard;
}(_react.Component);

//GameBoard.propTypes = {
//game_id: PropTypes.number,
//socket: PropTypes.string,
//current_user: PropTypes.object

//}

exports.default = GameBoard;

/***/ })

})