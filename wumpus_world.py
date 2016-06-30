from __future__ import print_function
from resolutor import *
from random import random
import numpy as np
import cProfile

def get_coordinates_next_to(x, y, width, height):
    res = []
    if x > 0:
        res.append(((x-1), y))
    if x < width-1:
        res.append(((x+1), y))
    if y > 0:
        res.append((x, (y-1)))
    if y < height-1:
        res.append((x, (y+1)))
    return res

class Game_Field:
    def __init__(self, field, x, y, wumpus=False, gold=False, hole=False):
        self.field = field
        self.x = x
        self.y = y
        self.wumpus = wumpus
        self.gold = gold
        self.hole = hole

    def smells(self):
        for x, y in get_coordinates_next_to(self.x, self.y, self.field.shape[0], self.field.shape[1]):
            if self.field[x, y].wumpus: return True
        return False

    def wind(self):
        for x, y in get_coordinates_next_to(self.x, self.y, self.field.shape[0], self.field.shape[1]):
            if self.field[x, y].hole: return True
        return False

class GoldHunterController:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        kb = KnowledgeBase()
        hole_symbols = np.empty((width, height), dtype=object)
        wind_symbols = np.empty((width, height), dtype=object)
        wumpus_symbols = np.empty((width, height), dtype=object)
        smell_symbols = np.empty((width, height), dtype=object)
        for y in range(height):
            for x in range(width):
                hole_symbols[x, y] = Symbol("F_{}_{}".format(y+1, x+1))
                wind_symbols[x, y] = Symbol("L_{}_{}".format(y+1, x+1))
                wumpus_symbols[x, y] = Symbol("W_{}_{}".format(y+1, x+1))
                smell_symbols[x, y] = Symbol("S_{}_{}".format(y+1, x+1))
        for y in range(height):
            for x in range(width):
                coords_next = get_coordinates_next_to(x, y, width, height)
                kb.add_sentence(Equivalence(wind_symbols[x, y], Disjunction(*[hole_symbols[x_, y_] for x_, y_ in coords_next])))
                #kb.add_sentence(Equivalence(smell_symbols[x, y], Disjunction(*[wumpus_symbols[x_, y_] for x_, y_ in coords_next])))
        kb.add_sentence(Negation(hole_symbols[0, 0]))
        kb.add_sentence(Negation(wind_symbols[0, 0]))
        print (kb)
        print ()
        #to_derive = Negation(hole_symbols[1, 0])
        to_derive = hole_symbols[1, 0]
        print ("Trying to derive", to_derive)
        res = kb.try_derive(to_derive)
        print ("Deriving", to_derive, "success" if res else "unsuccessful")

class Wumpus_World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.game_plain = np.empty(shape=(width, height), dtype=object)
        for y in range(height):
            for x in range(width):
                self.game_plain[x, y] = Game_Field(self.game_plain, x, y)
                if not (x == 0 and y == 0):
                    if random() < 0.2:
                        self.game_plain[x, y].hole = True
        wumpus_cnt = int(random()*(width*height-1))+1
        self.game_plain[wumpus_cnt // height, wumpus_cnt % height].wumpus = True
        gold_cnt = int(random()*(width*height-1))+1
        self.game_plain[gold_cnt // height, gold_cnt % height].gold = True

    def print(self):
        for y in reversed(range(self.height)):
            for x in range(self.width):
                field = self.game_plain[x, y]
                print (" {}{}{} ".format(
                    "W" if field.wumpus else " ",
                    "H" if field.hole else "-",
                    "G" if field.gold else " "), end='')
            print ()

if __name__ == "__main__":
    L11 = Symbol("L_1_1")
    F11 = Symbol("F_1_1")
    F21 = Symbol("F_2_1")
    F12 = Symbol("F_1_2")
    sentence1 = Negation(F11)
    sentence2 = Equivalence(L11, Disjunction(F21, F12))
    sentence3 = Negation(L11)
    kb = KnowledgeBase()
    kb.add_sentence(sentence1)
    kb.add_sentence(sentence2)
    kb.add_sentence(sentence3)

    to_derive = Negation(F21)
    print (kb)
    print ()
    print ("Trying to derive", to_derive)
    res = kb.try_derive(to_derive)
    print ("Deriving", to_derive, "success" if res else "unsuccessful")
    print ()
    print (kb)
    print ()
    to_derive = F21
    print ("Trying to derive", to_derive)
    res = kb.try_derive(to_derive)
    print ("Deriving", to_derive, "success" if res else "unsuccessful")
    print ()

    world = Wumpus_World(2, 2)
    world.print()
    print ()

    GoldHunterController(2, 3)
