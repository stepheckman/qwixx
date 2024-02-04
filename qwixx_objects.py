import random
import pprint


def last_used(player, color, number):
    """find right most used number in row for given player, color"""

    # adjust by 2 because of 0 indexing and 2-12 game
    # separate by ascending, descending
    if color in ["red", "orange"]:
        for i in range(10, -1, -1):
            if player.scoresheet.rows[color].checks[i] == 1:
                return i + 2
            else:
                return 2
    else:
        for i in range(10, -1, -1):
            if player.scoresheet.rows[color].checks[i] == 1:
                return 12 - i
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

    # put options in order
    omin = min(option1, option2)
    omax = max(option1, option2)

    # get distance for each move
    dist1 = distance(player, color, option1)
    dist2 = distance(player, color, option2)

    # get rightmost checked number
    last_num = last_used(player, color, option1)

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
        self.finished_rows = 0
        self.finished_color = ""
        self.winner = None

    def t(self):
        self.turn += 1
        print("\n*** Turn " + str(self.turn) + " ***")

        if self.turn % 2 == 1:
            tt = Turn(self.player1, self.player2, self.finished_color)
        else:
            tt = Turn(self.player2, self.player1, self.finished_color)
        self.finish()
        tt.step1()
        self.finish()
        tt.step2()
        # turn = Turn(self.player1, self.player2, self.finished_color)
        # # turn.print_dice()
        # turn.step1()
        # self.finish()
        # turn.step2()

    def play(self, max):
        # while self.gameover == 0 & self.turn < max:
        self.t()
        # self.gameover()

    def gameover(self):
        for pl in (self.player1, self.player2):
            pl.scoresheet.get_score()
        if self.player1.scoresheet.score > self.player2.scoresheet.score:
            self.winner = self.player1.name.title()
        elif self.player1.scoresheet.score < self.player2.scoresheet.score:
            self.winner = self.player2.name.title()
        else:
            self.winner = "tie"
        print("Game over! " + self.winner + " wins!")

    def finish(self):
        finished_rows = 0
        for pl in (self.player1, self.player2):
            for row in pl.scoresheet.rows.values():
                if row.checks[10] == 1:
                    finished_rows += 1
                    self.finished_color = row.color
            if finished_rows == 2:
                self.gameover = 1
            elif pl.scoresheet.penalty == 4:
                self.gameover = 1
        if self.gameover == 1:
            self.gameover()


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
    def __init__(self, player1, player2, finished_color):
        self.colors = ["red", "orange", "green", "blue"]
        if finished_color != "" and finished_color in self.colors:
            self.colors.remove(finished_color)
        # else:
        #     print("Something went wrong with finished_color")
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
        self.penalty = 0  # if counter gets to 2, player1 gets a penalty

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
        pprint.pprint(self.combos)

    def step1(self):
        """both players can take sum of white dice"""
        sum = self.dice["white1"].value + self.dice["white2"].value

        for pl in (self.player1, self.player2):
            # dist is dictionary of color, dist pairs
            dist = {}
            for color in self.colors:
                if pl.scoresheet.rows[color].checks[sum - 2] == 0:
                    dist[color] = distance(pl, color, sum)
            best_color = ""
            mindist = min(list(dist.values()))
            for color, d in dist.items():
                if d == mindist:
                    # best_dist = dist
                    best_color = color
            choice = {best_color: sum}
            print(choice)
            if best_color != "None":
                pl.move(choice)
            elif pl == self.player1:
                self.penalty += 1

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
        print(choice)
        if best_num is not None and best_color != "None":
            self.player1.move(choice)
        else:
            self.penalty += 1
        # if we satify both penalty conditions, take an penalty
        if self.penalty == 2:
            self.player1.scoresheet.penalty += 1


class Player:
    def __init__(self, name):
        self.name = name
        self.scoresheet = Scoresheet()
        self.turn = False

    def print_scoresheet(self):
        print("Scoresheet for " + self.name + ":")
        for row in self.scoresheet.rows.values():
            print(row.color.title() + ": ")
            if row.ascending:
                # +2 needed here just like -2 needed above
                for i in range(0, 11):
                    print(str(i + 2) + " ", end="")
                print("")
                for i in range(0, 11):
                    print(str(row.checks[i]) + " ", end="")
            else:
                for i in range(10, -1, -1):
                    print(str(i + 2) + " ", end="")
                print("")
                for i in range(10, -1, -1):
                    print(str(row.checks[i]) + " ", end="")
            print("")

    def move(self, choice):
        color = list(choice.keys())[0]
        number = list(choice.values())[0]
        self.scoresheet.rows[color].mark(number - 1)


class Scoresheet:
    def __init__(self):
        self.score = 0
        self.penalty = 0
        self.rows = {}
        for color in ["red", "orange", "green", "blue"]:
            self.rows[color] = Scoresheet_row(color)

    def get_score(self):
        scores = {}
        self.score = 0
        for row in self.rows.values():
            scores[row.color] = get_score_row(row)
        for s in scores.values():
            self.score += s
        self.score -= self.penalty * 5

    def get_score_row(self, row):
        match row.checks.sum():
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


class Scoresheet_row:
    def __init__(self, color):
        self.color = color
        self.ascending = self.color in ["red", "orange"]
        self.checks = {}
        for i in range(0, 11):
            self.checks[i] = 0

    def mark(self, number):
        self.checks[number - 2] = 1
