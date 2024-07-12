from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

game_state = {
    'board': [None] * 9,
    'currentPlayer': 'O',
    'winner': None,
}

@app.route('/game', methods=['GET'])
def get_game_state():
    return jsonify(game_state)

@app.route('/move', methods=['POST'])
def make_move():
    index = request.json.get('index')
    if game_state['board'][index] is None and game_state['winner'] is None:
        game_state['board'][index] = game_state['currentPlayer']
        game_state['currentPlayer'] = 'X' if game_state['currentPlayer'] == 'O' else 'O'
        
        # Check for a winner
        winning_combinations = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [0, 4, 8],
            [2, 4, 6],
        ]

        for combo in winning_combinations:
            a, b, c = combo
            if game_state['board'][a] and game_state['board'][a] == game_state['board'][b] == game_state['board'][c]:
                game_state['winner'] = game_state['board'][a]
                break

        if not any(cell is None for cell in game_state['board']) and game_state['winner'] is None:
            game_state['winner'] = 'Draw'
    
    return jsonify(game_state)

@app.route('/reset', methods=['POST'])
def reset_game():
    global game_state
    game_state = {
        'board': [None] * 9,
        'currentPlayer': 'O',
        'winner': None,
    }
    return jsonify(game_state)

if __name__ == '__main__':
    app.run(debug=True)