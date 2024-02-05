import random
import pprint


def last_used(player, color, number):
    """find right most used number in row for given player, color"""

    # adjust by 2 because of 0 indexing and 2-12 game
    # separate by ascending, descending
    if color in ["red", "orange"]:
        for i in range(12, 1, -1):
            if player.scoresheet.rows[color].checks[i] == 1:
                return i
            else:
                return 2
    else:
        for i in range(2, 13, 1):
            if player.scoresheet.rows[color].checks[i] == 1:
                return i
            else:
                return 12


def distance(player, color, number):
    """distance from last used cell from left end of the row"""

    last_num = last_used(player, color, number)

    # separate by ascending, descending
    if color in ["red", "orange"]:
        return number - last_num
    else:
        return last_num - number


def best_move_color_step2(player, color, option1, option2):
    """find the best move for a color, returns number and distance"""

    # get distance for each move
    dist1 = distance(player, color, option1)
    dist2 = distance(player, color, option2)

    # need to adjust by 2 here because of 0 indexing and 2-12 game
    # if (
    #     player.scoresheet.rows[color].checks[option1 - 2] == 1
    #     and player.scoresheet.rows[color].checks[option2 - 2] == 1
    # ):
    #     return None
    # # max option is to left of rightmost checked number
    # elif omax <= last_num and color in ["red", "orange"]:
    #     return None
    # elif omax < last_num and color in ["red", "orange"] and option1 > option2:
    #     # larger of 2 numbers works
    #     # return larger number and its dist
    #     return {option1, dist1}
    # elif omax < last_num and color in ["red", "orange"] and option1 <= option2:
    #     # larger of 2 numbers works
    #     # return larger number and its dist
    #     return {option2, dist2}
    # elif omin => last_num and color in ["blue", "green"]:
    #     return None
    # elif omin > last_num and color in ["blue", "green"] and option1 > option2:
    #     # smaller of 2 numbers works
    #     # return smaller number and its dist
    #     return {option2, dist2}
    # elif omin > last_num and color in ["red", "orange"] and option1 <= option2:
    #     # smaller of 2 numbers works
    #     # return smaller number and its dist
    #     return {option1, dist1}
    if dist1 <= 0 and dist2 <= 0:
        return None
    # interesting case when there are 2 options -- best one has shortest distance
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
        self.turn += 1
        print("\n*** Turn " + str(self.turn) + " ***")

        if self.turn % 2 == 1:
            tt = Turn(self.player1, self.player2, self.finished_rows)
        else:
            tt = Turn(self.player2, self.player1, self.finished_rows)
        self.check_done()
        tt.step1()
        self.check_done()
        if self.gameover == 0:
            tt.step2()
        else:
            self.over()
        # turn = Turn(self.player1, self.player2, self.finished_color)
        # # turn.print_dice()
        # turn.step1()
        # self.finish()
        # turn.step2()

    def play(self, max):
        while self.turn < max and self.gameover == 0:
            self.t()

    def over(self):
        for pl in (self.player1, self.player2):
            pl.scoresheet.get_score()
        if self.player1.scoresheet.score > self.player2.scoresheet.score:
            self.winner = self.player1.name.title()
        elif self.player1.scoresheet.score < self.player2.scoresheet.score:
            self.winner = self.player2.name.title()
        else:
            self.winner = "tie"
        print("\nGame over! " + self.winner + " wins!")
        for p in (self.player1, self.player2):
            p.print_scoresheet()
        for p in (self.player1, self.player2):
            print(p.scoresheet.print_score())
        exit()

    def check_done(self):
        for pl in (self.player1, self.player2):
            for row in pl.scoresheet.rows.values():
                if row.color not in self.finished_rows:
                    if (row.ascending and row.checks[12] == 1) or (
                        row.ascending is False and row.checks[2] == 1
                    ):
                        self.finished_rows.append(row.color)
            if pl.scoresheet.penalty == 4:
                self.gameover = 1
        if len(self.finished_rows) == 2:
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
        """both players can take sum of white dice"""
        white_sum = self.dice["white1"].value + self.dice["white2"].value

        for pl in (self.player1, self.player2):
            # dist is dictionary of color, dist pairs
            dist = {}
            for color in self.colors:
                # check that white_sum is not checked in player, color
                if pl.scoresheet.rows[color].checks[white_sum] == 0:
                    if (white_sum == 12 and color in ["red", "orange"]) or (
                        white_sum == 2 and color in ["blue", "green"]
                    ):
                        # can't pick 2/12 unless you already have 5
                        marks = list(pl.scoresheet.rows[color].checks.values())
                        print("list: " + str(marks))
                        print("sum of list: " + str(sum(marks)))
                        ct = sum(marks)
                        if ct >= 5:
                            # print("more than 5")
                            dist[color] = distance(pl, color, white_sum)
                    else:
                        dist[color] = distance(pl, color, white_sum)
            best_color = ""
            if len(list(dist.values())) == 0:
                self.p1_penalty += 1
            else:
                mindist = min(list(dist.values()))
                for color, d in dist.items():
                    if d == mindist:
                        # best_dist = dist
                        best_color = color
                choice = {best_color: white_sum}
                # if best_color != "None":
                pl.move(choice)

    def step2(self):
        """step2: player1 can take another X"""
        self.make_combos()

        options = {}
        for color in self.colors:
            options[color] = best_move_color_step2(
                self.player1, color, self.combos[color][0], self.combos[color][1]
            )
        # pprint.pprint(options)
        # options is dictionary where value is another dictionary
        # pl chooses move with shortest distance
        # best_dist = 0
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
            self.player1.move(choice)
        else:
            self.p1_penalty += 1

        # if we satify both penalty conditions, p1 get a penalty
        if self.p1_penalty == 2:
            self.player1.scoresheet.take_penalty()


class Player:
    def __init__(self, name):
        self.name = name
        self.scoresheet = Scoresheet()
        self.turn = False

    def print_scoresheet(self):
        print("Scoresheet for " + self.name + ":")
        self.scoresheet.print()

    def move(self, choice):
        color = list(choice.keys())[0]
        number = list(choice.values())[0]
        self.scoresheet.rows[color].mark(number - 1)


class Scoresheet:
    def __init__(self):
        self.score = 0
        self.penalty = 0
        self.penalty_show = ""
        self.rows = {}
        for color in ["red", "orange", "green", "blue"]:
            self.rows[color] = Scoresheet_row(color)

    def take_penalty(self):
        self.penalty += 1
        self.penalty_show += "X"

    def print(self):
        for row in self.rows.values():
            print(row.color.title() + ": ")
            # pprint.pprint(row.checks)
            for num in row.checks.keys():
                print(str(num) + " ", end="")
            print("")
            for value in row.checks.values():
                print(str(value) + " ", end="")
            print("")
        print(" " + self.penalty_show, end="")
        print("")

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
