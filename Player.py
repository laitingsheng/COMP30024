import numpy as np
from random import choice

from Board import Board
from Evaluation import Evaluation

inf = float("inf")


class Player:
    __slots__ = "board", "depth", "model"

    def __init__(self, colour=None):
        self.board = Board()
        self.model = Evaluation()

    def _move(self):
        vm = self.board.valid_move
        if vm.sum() < 1:
            return None

        pi = self.model.predict(self.board)[0]
        pi[vm == 0] = -inf
        a = np.argmax(pi)
        y = a // 64
        x = a % 64 // 8
        i = a % 64 % 8
        dx, dy = self.board.dirs[i // 2]
        i = i % 2 + 1
        nx = x + dx * i
        ny = y + dy * i
        return (x, y), (nx, ny)

    def _place(self):
        pi = self.model.predict(self.board)[0]
        pi[self.board.valid_place == 0] = -inf
        a = np.argmax(pi)
        return a % 8, a // 8

    def _execute(self, board, la):
        hist = []

        while not board.end:
            if board.placing:
                vp = board.valid_place
                a = np.random.choice(64, p=vp / vp.sum())
                vvp = self.model.predict(board)
                v = vvp[0, a]
                b = board.copy
                board.place(a % 8, a // 8)
                hist.append((v, a, b, vvp.copy()))
            else:
                vm = board.valid_move
                if vm.sum() < 1:
                    board.forfeit_move()
                else:
                    a = np.random.choice(512, p=vm / vm.sum())
                    vvm = self.model.predict(board)
                    v = vvm[0, a]
                    y = a // 64
                    x = a % 64 // 8
                    i = a % 64 % 8
                    dx, dy = board.dirs[i // 2]
                    i = i % 2 + 1
                    nx = x + dx * i
                    ny = y + dy * i
                    b = board.copy
                    board.move(x, y, nx, ny)
                    hist.append((v, a, b, vvm.copy()))

        r = board.reward
        s = 0
        pv, pa, pb, pvv = hist[0]
        for v, a, b, vv in hist[1:]:
            s += la * (v - pv)
            la *= la
            pvv[0, pa] = r + s * pv
            self.model.train(pb, pvv)
            pv, pa, pb, pvv = v, a, b, vv

        s += la * (r - pv)
        pvv[0, pa] = r + s * pv
        self.model.train(pb, pvv)

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

    def save(self, key):
        self.model.save(key)

    def train(self, episode, la=0.7):
        print('-' * 8, "Episode", episode, '-' * 8)
        for _ in range(1000):
            self._execute(Board(), la)

    def update(self, action):
        if self.board.placing:
            self.board.place(*action)
        elif action is None:
            self.board.forfeit_move()
        else:
            src, dest = action
            self.board.move(*src, *dest)
