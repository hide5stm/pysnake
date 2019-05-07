#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from random import randint
from logging import getLogger, FileHandler, Formatter, DEBUG, INFO

logger = getLogger(__name__)
handler_format = Formatter('%(asctime)s : %(name)s : %(levelname)s : %(message)s')
handler = FileHandler('snake.log', 'w')
handler.setFormatter(handler_format)
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False


direct_x = {KEY_DOWN: 1, KEY_UP: -1}
direct_y = {KEY_LEFT: -1, KEY_RIGHT: 1}
valid_key = {KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, 27}
boundaries_hight = {0: 18, 19: 1}
boundaries_width = {0: 58, 59: 1}


class Snake():
    def __init__(self):
        # ヘビの初期座標
        self._body = [(4,10), (4,9), (4,8)]

    def __len__(self):
        return len(self._body)

    def __contains__(self, xy):
        return xy in self._body

    def move(self, key):
        ''' 移動先のヘビの頭の座標を計算
            ヘビの長さは一時的に1増えることに注意
        '''
        x, y = self._body[0]
        x += direct_x.get(key, 0)
        y += direct_y.get(key, 0)
        self._body = [(x, y)] + self._body
        logger.info("snake:{}".format(self._body))

    def cross_boundaries(self):
        ''' へびが境界を越えたら逆側に移動 '''
        x, y = self._body[0]
        x = boundaries_hight.get(x, x)
        y = boundaries_width.get(y, y)
        self._body[0] = (x, y)

    def is_run_over(self):
        ''' ヘビの頭が胴体に重なっていたらTrueを返す '''
        return self._body[0] in self._body[1:]

    def eaten(self, food):
        x, y = food.get()
        return self._body[0] == (x, y)

    def pop(self):
        return self._body.pop()

    def head(self):
        return self._body[0]

class Food():
    def __init__(self, rand=False):
        if rand:
            self.x, self.y = randint(1, 18), randint(1, 58)
        else:
            self.x, self.y = 10, 20

    def get(self):
        return self.x, self.y


def create_window(h, w):
    curses.initscr()
    win = curses.newwin(h, w, 0, 0)

    win.keypad(1)
    curses.noecho()
    curses.curs_set(0)
    win.border(0)
    win.nodelay(1)

    return win


class Window():
    def __init__(self):
        self.win = create_window(20, 60)
        self.key = KEY_RIGHT    # 初期値

    def close(self, score):
        curses.endwin()
        print("\nScore - {}".format(score))

    def draw_food(self, x, y):
        self.win.addch(x, y, '*')

    def is_quit(self):
        return self.key == 27

    def draw(self, score, speed):
        self.win.border(0)
        status = "Score : {} Speed: {} ".format(score, speed)
        self.win.addstr(0, 2, status)
        self.win.addstr(0, 27, ' SNAKE ')

    def timeout(self, val):
        self.win.timeout(val)

    def wait_key(self):
        # Previous key pressed
        self.prev = self.key
        event = self.win.getch()
        logger.info("event={}".format(event))
        if event != -1:
            self.key = event

    def pause(self):
        ''' スペースが押されたら停止する。
            再度スペースが押されたら再開する。
        '''
        if self.key == ord(' '):
            self.key = -1
            while self.key != ord(' '):
                self.key = self.win.getch()
                logger.info("pause(): key={}".format(self.key))

            self.key = self.prev
            return True

        return False

    def update_key(self):
        ''' 無意味なキーが押されたら無視する '''
        if self.key not in valid_key:
            self.key = self.prev

    def move_tail(self, snake):
        ''' 最後尾の表示を削除 '''
        x, y = snake.pop()
        self.win.addch(x, y, ' ')

    def draw_head(self, snake):
        ''' ヘビの頭を表示 '''
        x, y = snake.head()
        self.win.addch(x, y, '#')


def increase_speed(snake):
    ''' ヘビが長くなるほど、移動速度を上げる
    '''
    return 150 - (len(snake)//5 + len(snake)//10) % 120


def make_food(snake):
    ''' ヘビに重ならないようにエサを配置できたらfoodを返す.
    '''
    while True:
        food = Food(rand=True)
        if food.get() not in snake:
            return food

def main_loop(win):
    food = Food()
    snake = Snake()
    score = 0

    win.draw_food(*food.get())

    while not win.is_quit():
        speed = increase_speed(snake)
        logger.info("score={} speed={}".format(score, speed))
        win.timeout(speed)
        win.draw(score, speed)

        win.wait_key()
        if win.pause():
            continue

        win.update_key()
        snake.move(win.key)
        snake.cross_boundaries()

        if snake.is_run_over():
            # game over
            break

        if snake.eaten(food):
            score += 1
            food = make_food(snake)
            win.draw_food(*food.get())
        else:
            win.move_tail(snake)

        win.draw_head(snake)

    return score

def main():
    win = Window()
    score = main_loop(win)
    win.close(score)


if __name__ == '__main__':
    main()
