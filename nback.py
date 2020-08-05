"""
N-Back Game

The Game Flow

1. Input the 'N' number and 'T' number
    - Validate T > N.
2. Generate 'T' number of Random inteager values
3. Determine the time how long each number is on the screen.
    - Default 1sec
4. After the time, clean the terminal and show a next number.
5. When the number is on the screen, Get the input from user
    - User may type 'v' and enter.
    - Validate the input is 'v' or not.
    - If it is 'v', check the current number matches the number N's backed.
5. Do the number 4,5, until 'T'
6. After 5, print the score.
"""
import os
import time
import random
import sys
from select import select


ERR_TOTAL_SMALLER_NBACK = "Total should be greater than Nback"
ERR_INPUT_NOT_INT = "The Input should be inteagers"


class InputError(BaseException):
    pass


class NBack(object):
    def __init__(self, nback=2, total=10):
        """
        param
            @nback: N-Back number
            @total: the total numbers
        """

        try:
            if int(total) <= int(nback):
                raise InputError(ERR_TOTAL_SMALLER_NBACK)
        except InputError:
            raise
        except ValueError:
            raise ValueError(ERR_INPUT_NOT_INT)

        self.nback = nback
        self.total = total

    def ready_quests(self):
        print("Generating {}'s Random number".format(self.total))
        quests = []
        # Default range 1~9.
        for _ in range(0, self.total):
            quests.append(random.randint(1,10))

        print("Ready!")
        time.sleep(0.1)
        return quests

    def game_start(self):
        quests = self.ready_quests()
        self.clear_screen()

        answers = []
        for q in quests:
            print("{}".format(q))
            answers.append(self.input_from_user())
            self.clear_screen()
            time.sleep(0.1)

        print("Game Done!")
        time.sleep(0.1)
        self.game_result(quests, answers)

    def game_result(self, quests, answers):
        n = self.nback
        score_fmt = "{:>6} {:>7} {:>7}"
        print("quests answers correct")
        for i in range(self.total):
            q = quests[i]
            a = answers[i]

            if i < n:
                c = False
            elif quests[i-n] == quests[i]:
                c = True
            else:
                c = False

            print(score_fmt.format(q, a, c))

    def input_from_user(self, timeout=2.0):
        """
        If user input 'v', return the current number
        """
        sys.stdout.write("answer(Type 'v' if it matches): ")
        astring = None
        rlist, _, _ = select([sys.stdin], [], [], timeout)
        if rlist:
            astring = sys.stdin.readline()
        else:
            print "No input. Moving on..."

        if astring:
            return True
        else:
            return False

    def clear_screen(self):
        os.system("clear")
