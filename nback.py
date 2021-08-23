"""
N-Back Game

Writer: Lim Jae Hwan
"""

import os
import time
import random
import sys
import termios
import contextlib
import signal
from select import select

from error import (
    ERR_INPUT_NBACK_OVERMAX, ERR_INPUT_NBACK_NO_INPUT, ERR_INPUT_NBACK_NOT_INT,
    ERR_INPUT_NBACK_INVALID, ERR_INPUT_NBACK_LESS_THEN_NBACK,
    InputError, SignalAlarmTimeOut,
)


TICK = 1
DEFAULT_RANGE = 4
DEFAULT_TIME = 2
DEFAULT_NBACK = 3

MSG_CHOOSE_N = "Choose 'N' to step back (default: {}): "
MSG_CHOOSE_T = "Choose 'T' to the total number of requests (default: {}): "
MSG_CONFIRM = "If it's matched, Press 'y' otherwise, Press 'n': "

MAX_NBACK = 100
MAX_TOTAL = MAX_NBACK + 1


class NBack(object):
    def __init__(self):
        """
        param
            @nback: N-Back number
            @total: the total numbers
        """

        self.nback = None
        self.total = None

    def validate_nback(self, data):
        if data is None:
            raise InputError(ERR_INPUT_NBACK_NO_INPUT)

        try:
            ret = int(data)
        except:
            raise InputError(ERR_INPUT_NBACK_NOT_INT)

        if ret > MAX_NBACK:
            raise InputError(ERR_INPUT_NBACK_OVERMAX)

        return ret

    def validate_total(self, data):
        if data is None:
            raise InputError(ERR_INPUT_NBACK_NO_INPUT)

        try:
            ret = int(data)
        except:
            raise InputError(ERR_INPUT_NBACK_NOT_INT)

        # 'T' should be greater than N.
        if ret > MAX_TOTAL:
            raise InputError(ERR_INPUT_NBACK_OVERMAX)

        if ret <= self.nback:
            raise InputError(ERR_INPUT_NBACK_LESS_THEN_NBACK)

        return ret

    def setup(self):
        ''' Setup the Nback game. '''

        setup_done = False
        while setup_done is False:
            self.clear_screen()
            answer = self.quest_and_answer(
                MSG_CHOOSE_N.format(DEFAULT_NBACK), timeout=10)
            try:
                self.nback = self.validate_nback(answer)
                setup_done = True
            except BaseException as e:
                self.print_message(e.message)
                setup_done = False

        setup_done = False
        while setup_done is False:
            self.clear_screen()
            answer = self.quest_and_answer(
                MSG_CHOOSE_T.format(self.nback + 1), timeout=10)
            try:
                self.total = self.validate_total(answer)
                setup_done = True
            except BaseException as e:
                self.print_message(e.message)
                setup_done = False

        self.ready_quests()
        self.calculate_correct()

    def ready_quests(self):
        print("Generating {}'s Random number".format(self.total))
        self.quests = []
        # Default range 1~9.
        for _ in range(0, self.total):
            self.quests.append(random.randint(1,DEFAULT_RANGE))

        print("Ready!")
        time.sleep(0.7)

    def before_nback(self, answers, i, q):
        ''' Show the numbers before 'N'th. '''

        self.ready_screen(i)
        print("{} Ready.".format(q))
        answers.append(None)
        time.sleep(DEFAULT_TIME)

    def after_nback(self, answers, i, q):
        ''' Show the numbers from N'th to total. '''

        answer = None
        user_answered = False
        self.signal_alarm_set()
        while not self.is_timeout():
            prompt = "{} (ans:{:>4}) (time: {})".format(q, answer, self.timer)
            self.ready_screen(i)

            try:
                if user_answered is True:
                    self.print_message(prompt)
                    # Blocked until waken up by signal.
                    self.wait_alarm()

                else:
                    # Blocked until valid keys are pressed
                    # (ex: left arrow, right arrow)
                    # Or signal alarm timeout
                    # (ex: 1 second)
                    answer = self.input_side_arrows(prompt=prompt)
                    user_answered = True
            except SignalAlarmTimeOut:
                self.signal_alarm_tick_down()
                self.signal_alarm_resume()

        if answer is None:
            answers.append(None)
        elif answer == 'yes':
            answers.append("True")
        else:
            answers.append("False")

        self.signal_alarm_done()

    def ready_screen(self, i):
        self.clear_screen()
        for n in range(i):
            print("")

    def game_start(self):
        answers = []
        for i, q in enumerate(self.quests):
            # Show N-1 numbers.
            if i < self.nback:
                self.before_nback(answers, i, q)
            else:
                self.after_nback(answers, i, q)

        time.sleep(0.1)
        self.clear_screen()
        self.game_result(self.quests, answers, self.corrects)

    def game_result(self, quests, answers, corrects):
        n = self.nback
        score_fmt = "{:>6} {:>7} {:>7} {:>7}"
        print("")
        print("quests answers correct matched")
        for i in range(self.total):
            if corrects[i] is None:
                result = "None"
            elif answers[i] == corrects[i]:
                result = "OK"
            else:
                result = "FAIL"
            print(score_fmt.format(quests[i], answers[i], corrects[i], result))

    def print_message(self, msg):
        ''' Print a message on console. '''

        sys.stdout.write("{}".format(msg))
        sys.stdout.flush()

    def quest_and_answer(self, quest, timeout=None):
        ''' Print a quest message on console and Get user's answer.

        return None if no answer returns from user during timeout.
        '''

        self.print_message(quest)

        if timeout is not None:
            rlist, _, _ = select([sys.stdin], [], [], timeout)
        else:
            rlist, _, _ = select([sys.stdin], [], [])

        # rlist: wait until ready for reading
        if rlist:
            string = sys.stdin.readline()
        else:
            string = None

        return string

    def calculate_correct(self):
        self.corrects = [None] * self.nback
        after_n_quests = self.quests[self.nback:]
        for i, q in enumerate(after_n_quests):
            if self.quests[i] == q:
                self.corrects.append("True")
            else:
                self.corrects.append("False")

    def clear_screen(self):
        os.system("clear")

    @contextlib.contextmanager
    def _raw_mode(self, file):
        """ Make terminal raw mode for getting an event pressing a key. """
        old_attrs = termios.tcgetattr(file.fileno())
        new_attrs = old_attrs[:]
        new_attrs[3] = new_attrs[3] & ~(termios.ECHO | termios.ICANON)
        try:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, new_attrs)
            yield
        finally:
            termios.tcsetattr(file.fileno(), termios.TCSADRAIN, old_attrs)

    def input_side_arrows(self, prompt=''):
        ''' Catch the side arrows (left, right).

        left arrow keys 3-bytes  [27, 91, 68]
        right arrow keys 3-bytes [27, 91, 67]
        '''
        sys.stdout.write(prompt)
        sys.stdout.flush()

        with self._raw_mode(sys.stdin):
            while True:
                # Read 3bytes
                chars = sys.stdin.read(3)
                if len(chars) != 3:
                    continue

                if (ord(chars[0]) == 27
                        and ord(chars[1]) == 91
                        and ord(chars[2]) == 68):
                    # Left arrow means yes.
                    return 'yes'
                if (ord(chars[0]) == 27
                        and ord(chars[1]) == 91
                        and ord(chars[2]) == 67):
                    # Right arrow means no.
                    return 'no'

                # Otherwise blocked.
                continue

    def interrupted(self, signum, frame):
        raise SignalAlarmTimeOut("Timeout")

    def signal_alarm_set(self):
        self.timer = DEFAULT_TIME
        signal.signal(signal.SIGALRM, self.interrupted)
        signal.alarm(TICK)

    def signal_alarm_resume(self):
        signal.alarm(TICK)

    def signal_alarm_tick_down(self):
        self.timer -= TICK

    def signal_alarm_done(self):
        signal.alarm(0)

    def is_timeout(self):
        return (self.timer == 0)

    def wait_alarm(self):
        while True: pass
