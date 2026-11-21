"""Mistletoe Mail for CircuitPython on the RP2040 Pico H."""

"""VERY MOUCH WIP!!!!!"""

import random
import time

# The three columns run from the bakery on the left to the toy shop on the right.
NOTES = (1047, 1319, 1568)
LAST_ROUTE = 6
LIGHTS_OUT = (0, 0, 0)
TURN_LIGHT = (4400, 4400, 4400)
BRIGHT = 53000

# The opening of Jingle Bells. Each pair gives pitch and duration in beats.
CAROL = (
    (1319, 1), (1319, 1), (1319, 2),
    (1319, 1), (1319, 1), (1319, 2),
    (1319, 1), (1568, 1), (1047, 1.5), (1175, 0.5), (1319, 4),
)


class Doorbells:
    """Settle all three contacts together so a chord stays a chord."""

    def __init__(self, pins):
        self.pins = pins
        self.raw = self.stable = 0
        self.changed = 0

    def sample(self, now):
        mask = 0
        for index, pin in enumerate(self.pins):
            if not pin.value:
                mask |= 1 << index
        if mask != self.raw:
            self.raw = mask
            self.changed = now
        if now - self.changed >= 0.025:
            self.stable = mask
        return self.stable


class Village:
    def __init__(self):
        import board
        import digitalio
        import pwmio

        self.lamps = [pwmio.PWMOut(pin, frequency=500, duty_cycle=0)
                      for pin in (board.GP2, board.GP6, board.GP10)]
        pins = [digitalio.DigitalInOut(pin)
                for pin in (board.GP4, board.GP8, board.GP12)]
        for pin in pins:
            pin.switch_to_input(pull=digitalio.Pull.UP)
        self.keys = Doorbells(pins)
        self.piezo = pwmio.PWMOut(board.GP14, frequency=1047, duty_cycle=0,
                                  variable_frequency=True)
        self.muted = False

    def show(self, levels, hz=0):
        for lamp, level in zip(self.lamps, levels):
            lamp.duty_cycle = level
        if hz and not self.muted:
            self.piezo.frequency = hz
            self.piezo.duty_cycle = 24576
        else:
            self.piezo.duty_cycle = 0

    def released(self):
        while self.keys.sample(time.monotonic()):
            time.sleep(0.005)

    def ring(self, shop, duration, hz=None):
        levels = [0, 0, 0]
        levels[shop] = BRIGHT
        self.show(levels, NOTES[shop] if hz is None else hz)
        time.sleep(duration)
        self.show(LIGHTS_OUT)

    def welcome(self):
        self.released()
        down = 0
        while True:
            now = time.monotonic()
            mask = self.keys.sample(now)
            if mask:
                if not down:
                    started = now
                down |= mask
            if down and not mask:
                if down == 2 and now - started >= 0.8:
                    self.muted = not self.muted
                    self.show((BRIGHT,) * 3, NOTES[1])
                    time.sleep(0.35)
                    down = 0
                elif down in (1, 2, 4):
                    self.show(LIGHTS_OUT)
                    return
                else:
                    down = 0
            glow = [int(700 + 7100 * abs((now * 0.45 + phase) % 2 - 1) ** 2)
                    for phase in (0, 0.66, 1.33)]
            self.show(glow)
            time.sleep(0.01)

    def read_shop(self):
        self.show(TURN_LIGHT)
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            mask = self.keys.sample(time.monotonic())
            if mask in (1, 2, 4):
                shop = (1, 2, 4).index(mask)
                levels = list(TURN_LIGHT)
                levels[shop] = BRIGHT
                self.show(levels, NOTES[shop])
                start = time.monotonic()
                while self.keys.sample(time.monotonic()):
                    if time.monotonic() - start > 0.22:
                        self.show(levels)
                    time.sleep(0.005)
                self.show(TURN_LIGHT)
                return shop
            if mask:
                self.released()
            time.sleep(0.005)
        return None

    def play_route(self, route):
        self.show(LIGHTS_OUT)
        time.sleep(0.55)
        for shop in route:
            self.ring(shop, 0.38)
            time.sleep(0.18)
        self.keys.sample(time.monotonic())
        time.sleep(0.03)
        self.keys.sample(time.monotonic())
        self.released()

    def retry(self):
        for _ in range(2):
            self.show((16000,) * 3, 784)
            time.sleep(0.13)
            self.show(LIGHTS_OUT)
            time.sleep(0.15)

    def celebrate(self):
        for index, (hz, beats) in enumerate(CAROL):
            self.ring(index % 3, 0.17 * beats, hz)
            time.sleep(0.045)
        self.show((BRIGHT,) * 3)
        time.sleep(0.6)
        self.show(LIGHTS_OUT)

    def music_box(self):
        self.released()
        while True:
            self.read_shop()


def deliver(village, pick):
    route = [pick(3), pick(3)]
    while True:
        village.play_route(route)
        for expected in route:
            answer = village.read_shop()
            if answer is None:
                return
            if answer != expected:
                village.retry()
                break
        else:
            if len(route) == LAST_ROUTE:
                village.celebrate()
                return
            route.append(pick(3))


def main():
    village = Village()
    village.keys.sample(time.monotonic())
    time.sleep(0.04)
    if village.keys.sample(time.monotonic()) == 5:
        village.music_box()
    while True:
        village.welcome()
        deliver(village, random.randrange)


if __name__ == '__main__':
    main()
