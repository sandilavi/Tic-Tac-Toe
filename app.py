from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Use environment variable for the database URL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
db = SQLAlchemy(app)

# Check database connection status
def check_db_connection():
    with app.app_context():
        try:
            connection = db.engine.connect()
            connection.execute(text('SELECT 1'))
            connection.close()  # Close the connection
            print('Database connection successful.')
        except Exception as e:
            print('Error connecting to database:', str(e))

# Print database connection status on application startup
check_db_connection()

class GameState(db.Model):
    __tablename__ = 'game_state'
    id = db.Column(db.Integer, primary_key=True)
    player1_wins = db.Column(db.Integer, default=0)
    player2_wins = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()

def check_winner(board):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for combo in winning_combinations:
        if board[combo[0]] and board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]]
    return None

@app.route('/game', methods=['GET'])
def get_game_state():
    state = GameState.query.first()
    if not state:
        state = GameState(player1_wins=0, player2_wins=0, draws=0)
        db.session.add(state)
        db.session.commit()
    return jsonify(player1_wins=state.player1_wins, player2_wins=state.player2_wins, draws=state.draws)

@app.route('/move', methods=['POST'])
def make_move():
    data = request.get_json()
    board = data['board']
    current_player = data['current_player']
    index = data['index']

    board[index] = "O" if current_player == 1 else "X"
    current_player = 2 if current_player == 1 else 1
    winner = check_winner(board)
    game_state = GameState.query.first()
    if not game_state:
        game_state = GameState(player1_wins=0, player2_wins=0, draws=0)
        db.session.add(game_state)
    if winner:
        if winner == "O":
            game_state.player1_wins += 1
        else:
            game_state.player2_wins += 1
    elif "" not in board:
        game_state.draws += 1
    db.session.commit()
    return jsonify({
        "board": board,
        "current_player": current_player,
        "winner": winner,
        "player1_wins": game_state.player1_wins,
        "player2_wins": game_state.player2_wins,
        "draws": game_state.draws
    })

@app.route('/reset', methods=['POST'])
def reset_game():
    return jsonify({"board": [""]*9, "current_player": 1, "winner": None})

if __name__ == '__main__':
    app.run(debug=True)