from collections import Counter
from random import choice

from Board import Board
from referee import _Game, _InvalidActionException


class Player:
    def __init__(self, colour=None, board=None):
        if board is None:
            self.board = Board()
        else:
            self.board = board

    def _move(self):
        moves = [
            (src, dest) for src, dests in self.board.valid_move
            for dest in dests
        ]
        if not moves:
            return None
        return choice(moves)

    def _place(self):
        return choice(list(self.board.valid_place))

    def action(self, turns):
        if self.board.placing:
            action = self._place()
            self.board.place(*action)
            return action
        action = self._move()
        if action is None:
            self.board.forfeit_move()
            return
        src, dest = action
        self.board.move(*src, *dest)
        return action

    def test(self, other):
        w_counter = Counter()
        print("White test")
        for i in range(100):
            game = _Game()
            self.board.__init__()
            other.board.__init__()
            mine, oppo = other, self
            print(f"Game {i} started")
            print(game)
            while game.playing():
                turns = game.turns
                action = mine.action(turns)
                try:
                    game.update(action)
                except _InvalidActionException as e:
                    print(f"invalid action ({game.loser}):", e)
                    raise RuntimeError()
                print(game)
                oppo.update(action)
                mine, oppo = oppo, mine
            if game.winner == 'B':
                reward = -1
            elif game.winner == 'W':
                reward = 1
            else:
                reward = 0
            w_counter.update([reward])

        b_counter = Counter()
        print("Black test")
        for i in range(100):
            game = _Game()
            self.board.__init__()
            other.board.__init__()
            mine, oppo = self, other
            print(f"Game {i} started")
            print(game)
            while game.playing():
                turns = game.turns
                action = mine.action(turns)
                try:
                    game.update(action)
                except _InvalidActionException as e:
                    print(f"invalid action ({game.loser}):", e)
                    raise RuntimeError()
                print(game)
                oppo.update(action)
                mine, oppo = oppo, mine
            if game.winner == 'W':
                reward = -1
            elif game.winner == 'B':
                reward = 1
            else:
                reward = 0
            b_counter.update([reward])

        results = [w_counter[1], w_counter[0], w_counter[-1],
                   b_counter[-1], b_counter[0], b_counter[1]]

        return results

    def update(self, action):
        if self.board.placing:
            self.board.place(*action)
        elif action is None:
            self.board.forfeit_move()
        else:
            src, dest = action
            self.board.move(*src, *dest)
