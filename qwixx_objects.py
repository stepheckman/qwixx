import random
import pprint


def last_used(player, color, number):
    """find right most used number in row for given player, color"""

    # separate by ascending, descending
    if color in ["red", "orange"]:
        # ascending but work from right side (so descending)
        for i in range(12, 1, -1):
            if player.rows[color].checks[i] == 1:
                return i
        return 1
    else:
        for i in range(2, 13, 1):
            if player.rows[color].checks[i] == 1:
                return i
        return 13


def distance(player, color, number):
    """distance from last used cell from left end of the row"""

    last_num = last_used(player, color, number)

    # cannot choose last spot in row unless player already has 5
    if (number == 12 and color in ["red", "orange"]) or (
        number == 2 and color in ["blue", "green"]
    ):
        # can't pick 2/12 unless you already have 5
        marks = list(player.rows[color].checks.values())
        # print("list: " + str(marks))
        # print("sum of list: " + str(sum(marks)))
        ct = sum(marks)
        if ct < 5:
            # cannot use number, less than 5
            return -1
        # else just continue

    # separate by ascending, descending
    if color in ["red", "orange"] and number > last_num:
        return number - last_num
    elif color not in ["red", "orange"] and number < last_num:
        return last_num - number
    else:
        return -1


def best_move_color_step2(player, color, option1, option2):
    """find the best move for a color, returns number and distance"""

    # get distance for each move
    dist1 = distance(player, color, option1)
    dist2 = distance(player, color, option2)

    if dist1 <= 0 and dist2 <= 0:
        return None
    elif dist1 <= 0 and dist2 > 0:
        return {option2: dist2}
    elif dist1 > 0 and dist2 <= 0:
        return {option1: dist1}
    # when there are 2 options -- best one has shortest distance
    elif dist1 < dist2:
        return {option1: dist1}
    elif dist1 >= dist2:
        return {option2: dist2}
    else:
        return None


class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.turn = 0
        self.gameover = 0
        # set of colors that are filled up for both players
        self.finished_rows = []
        self.winner = None

    def t(self):
        self.check_done()
        self.turn += 1
        print("\n*** Turn " + str(self.turn) + " ***")

        if self.turn % 10 == 0:
            for pl in (self.player1, self.player2):
                pl.print_scoresheet()
                # print(pl.print_score())
                pl.print_score()

        if self.turn % 2 == 1:
            tt = Turn(self.player1, self.player2, self.finished_rows)
        else:
            tt = Turn(self.player2, self.player1, self.finished_rows)
        tt.step1()
        self.check_done()
        if self.gameover == 0:
            tt.step2()
        else:
            self.over()

    def play(self, max):
        while self.turn < max and self.gameover == 0:
            self.t()

    def over(self):
        for pl in (self.player1, self.player2):
            pl.get_score()
        if self.player1.score > self.player2.score:
            self.winner = self.player1.name.title()
        elif self.player1.score < self.player2.score:
            self.winner = self.player2.name.title()
        else:
            self.winner = "tie"
        print("\nGame over! " + self.winner + " wins!\n")
        for p in (self.player1, self.player2):
            p.print_scoresheet()
            # print(p.print_score())
            p.print_score()
        exit()

    def check_done(self):
        for pl in (self.player1, self.player2):
            for row in pl.rows.values():
                if row.color not in self.finished_rows:
                    if (row.ascending and row.checks[12] == 1) or (
                        row.ascending is False and row.checks[2] == 1
                    ):
                        self.finished_rows.append(row.color)
                        # print("finished row: " + row.color)
            if pl.penalty == 4:
                self.gameover = 1
        if len(self.finished_rows) == 2:
            print("finished 2 rows: ", end="")
            pprint.pprint(self.finished_rows)
            self.gameover = 1
        if self.gameover == 1:
            self.over()


class Die:
    """
    Represents a die with a specific number of sides and a color.

    Attributes:
        sides (int): The number of sides on the die.
        color (str): The color of the die.
        value (int): The current value shown on the die.

    Methods:
        roll(): Rolls the die and updates the value.
    """

    def __init__(self, color, sides=6):
        self.sides = sides
        self.color = color
        self.value = 0
        self.roll()

    def roll(self):
        """
        Rolls the die and updates the value to a random number between 1 and the number of sides.
        """
        self.value = random.randint(1, self.sides)

    # def __str__(self):
    #     return str(self.value)


class Turn:
    def __init__(self, player1, player2, finished_rows):
        self.colors = ["red", "orange", "green", "blue"]
        self.p1_penalty = 0  # if counter gets to 2, player1 gets a penalty

        # finished-rows should only have one entry -- if there are 2, game is over
        if len(finished_rows) == 1:
            # finished_color = finished_rows{0}
            self.colors.remove(finished_rows[0])
        elif len(finished_rows) > 1:
            print("Game over! -- something is wrong")
        self.colors_all = self.colors[:]
        # add 2 white dice
        self.colors_all.append("white1")
        self.colors_all.append("white2")

        # it is always player 1's turn
        self.player1 = player1
        self.player2 = player2
        # dictionary of 6 dice
        dice = {}
        for color in self.colors_all:
            dice[color] = Die(color)
            self.dice = dice
            for die in self.dice.values():
                die.roll()
        self.print_dice()
        self.combos = {}

    def print_dice(self):
        print("Dice:")
        for die in self.dice.values():
            print(die.color + ": " + str(die.value))

    def make_combos(self):
        # make all possible combinations of dice
        for color in self.colors:
            self.combos[color] = []
            self.combos[color].append(
                self.dice[color].value + self.dice["white1"].value
            )
            self.combos[color].append(
                self.dice[color].value + self.dice["white2"].value
            )
        # pprint.pprint(self.combos)

    def step1(self):
        """both players can take sum of white dice in any color"""
        white_sum = self.dice["white1"].value + self.dice["white2"].value

        for pl in (self.player1, self.player2):
            # dist is dictionary of color, dist pairs
            dist = {}
            for color in self.colors:
                # -1 indicates an illegal end move
                color_dist = distance(pl, color, white_sum)
                if color_dist != -1:
                    dist[color] = color_dist
            best_color = ""
            if len(list(dist.values())) == 0:
                if pl == self.player1:
                    # print("player 1 getting a penalty in step 1")
                    self.p1_penalty += 1
                # if not player 1, make no move and just continue
            else:
                # pprint.pprint(dist)
                # print(len(list(dist.values())))
                mindist = min(list(dist.values()))
                for color, d in dist.items():
                    if d == mindist:
                        # best_dist = dist
                        best_color = color
                choice = {best_color: white_sum}
                # if best_color != "None":
                print(pl.name + " making move: " + best_color + " " + str(white_sum))
                pl.move(choice)

    def step2(self):
        """step2: player1 can take another X"""
        self.make_combos()

        # find best move for each color
        options = {}
        for color in self.colors:
            options[color] = best_move_color_step2(
                self.player1, color, self.combos[color][0], self.combos[color][1]
            )

        best_num = None
        best_color = ""
        for color, dict in options.items():
            # dict is dictionary of num, dist pairs
            if dict is not None:
                mindist = min(dict.values())
                for num, dist in dict.items():
                    if dist == mindist:
                        # best_dist = dist
                        best_num = num
                        best_color = color
        choice = {best_color: best_num}
        # print("Choice in Step 2 is: " + str(choice))
        if best_num is not None and best_color != "None":
            print(
                self.player1.name + " making move: " + best_color + " " + str(best_num)
            )
            self.player1.move(choice)
        else:
            # print("player 1 getting a penalty in step 2")
            self.p1_penalty += 1

        # if we satify both penalty conditions, p1 get a penalty
        if self.p1_penalty == 2:
            print("Penalty for " + self.player1.name)
            self.player1.take_penalty()


class Player:
    def __init__(self, name):
        self.name = name
        self.turn = False
        self.score = 0
        self.penalty = 0
        self.penalty_show = ""
        self.rows = {}
        for color in ["red", "orange", "green", "blue"]:
            self.rows[color] = Scoresheet_row(color)
            # print("row: " + color)
            # pprint.pprint(self.rows[color].checks)

    def print_scoresheet(self):
        print("Scoresheet for " + self.name + ":")

        # self.rows is a dictionary of color, row object pairs
        for row in self.rows.values():
            print(row.color.title() + ": ", end="")
            # pprint.pprint(row.checks)
            # row.checks is a dictionary of num (2-12), value (0,1) pairs
            for num, value in row.checks.items():
                if value == 1:
                    print(str(num) + " ", end="")
            print("")
        print(" " + self.penalty_show, end="")
        print("")

    def move(self, choice):
        color = list(choice.keys())[0]
        number = list(choice.values())[0]
        self.rows[color].mark(number)

    def take_penalty(self):
        self.penalty += 1
        self.penalty_show += "X"

    def get_score(self):
        scores = {}
        self.score = 0
        for row in self.rows.values():
            scores[row.color] = row.score()
        # pprint.pprint(scores)
        for s in scores.values():
            self.score += s
        self.score -= self.penalty * 5

    def print_score(self):
        # abe_start
        # print("in print_score()")
        # abe_stop
        self.get_score()
        print("Score: " + str(self.score))


class Scoresheet_row:
    def __init__(self, color):
        self.color = color
        self.ascending = self.color in ["red", "orange"]
        self.checks = {}
        if self.ascending:
            for i in range(2, 13):
                self.checks[i] = 0
        else:
            for i in range(12, 1, -1):
                self.checks[i] = 0

    def mark(self, number):
        self.checks[number] = 1

    def score(self):
        row_score = sum(list(self.checks.values()))
        # print(row_score)
        match row_score:
            case 0:
                return 0
            case 1:
                return 1
            case 2:
                return 3
            case 3:
                return 6
            case 4:
                return 10
            case 5:
                return 15
            case 6:
                return 21
            case 7:
                return 28
            case 8:
                return 36
            case 9:
                return 45
            case 10:
                return 55
            case 11:
                return 66
            case 12:
                return 78
            case _:
                return 999
