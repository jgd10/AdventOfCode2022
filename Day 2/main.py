from enum import Enum
import csv


class Player(Enum):
    ROCK = 1
    PAPER = 2
    SCISSORS = 3


class Result(Enum):
    LOSE = 0
    DRAW = 3
    WIN = 6


ME_MAP = {'X': Result.LOSE, 'Y': Result.DRAW, 'Z': Result.WIN}
YE_MAP = {'A': Player.ROCK, 'B': Player.PAPER, 'C': Player.SCISSORS}
LOSING_THROWS = {Player.ROCK.name: Player.SCISSORS,
                 Player.PAPER.name: Player.ROCK,
                 Player.SCISSORS.name: Player.PAPER}

WINNING_THROWS = {Player.ROCK.name: Player.PAPER,
                  Player.PAPER.name: Player.SCISSORS,
                  Player.SCISSORS.name: Player.ROCK}


def calculate_score_for_row(row):
    game = row[0].split(' ')
    ye_choice, result = YE_MAP[game[0]], ME_MAP[game[1]]

    if result == Result.DRAW:
        my_choice = ye_choice
    elif result == Result.LOSE:
        my_choice = LOSING_THROWS[ye_choice.name]
    else:
        my_choice = WINNING_THROWS[ye_choice.name]

    return result.value + my_choice.value


with open('input.txt', 'r') as f:
    reader = csv.reader(f)
    data = [row for row in reader]

score = [calculate_score_for_row(row) for row in data]
print(sum(score))
