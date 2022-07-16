import RPi.GPIO as GPIO
import time
import asyncio

timestamp = time.time()
zebra = False

SEMAPHORE_PINS = [
    {
        "id": 0,
        "pins": {"red": 15, "yellow": 13, "green": 11},
    },
    {
        "id": 1,
        "pins": {"red": 12, "yellow": 3, "green": 5},
    },
]

TL1RED = 15
TL1YELLOW = 13
TL1GREEN = 11

TL2RED = 12
TL2YELLOW = 3
TL2GREEN = 5

BUTTON = 10

# Initial setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
for semaphore in SEMAPHORE_PINS:
    for color in ["red", "green", "yellow"]:
        pin = semaphore["pins"][color]
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
GPIO.output(SEMAPHORE_PINS[0]["pins"]["green"], GPIO.HIGH)
GPIO.output(SEMAPHORE_PINS[1]["pins"]["red"], GPIO.HIGH)


def button_callback(channel):
    global timestamp, zebra
    timestamp = time.time()
    zebra = True
    print("...")


GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(BUTTON, GPIO.RISING, callback=button_callback)


def get_semaphore_state(id):
    if GPIO.input(SEMAPHORE_PINS[id]["pins"]["green"]):
        return "green"
    elif GPIO.input(SEMAPHORE_PINS[id]["pins"]["yellow"]):
        if GPIO.input(SEMAPHORE_PINS[id]["pins"]["red"]):
            return "redyellow"
        return "yellow"
    elif GPIO.input(SEMAPHORE_PINS[id]["pins"]["red"]):
        return "red"
    else:
        return "off"


def get_state():
    global timestamp, zebra

    return {
        "timestamp": timestamp,
        "zebra": zebra,
        "lights": [
            {
                "id": 0,
                "state": get_semaphore_state(0),
            },
            {
                "id": 1,
                "state": get_semaphore_state(1),
                "hasCar": False,
            },
        ],
    }


# Turning both semaphores off
def turn_all_off():
    global timestamp
    for semaphore in SEMAPHORE_PINS:
        for color in ["red", "green", "yellow"]:
            pin = semaphore["pins"][color]
            GPIO.output(pin, GPIO.LOW)

    timestamp = time.time()


def turn_one_off(id):
    if id == 0:
        GPIO.output(TL1RED, GPIO.LOW)
        GPIO.output(TL1YELLOW, GPIO.LOW)
        GPIO.output(TL1GREEN, GPIO.LOW)
    elif id == 1:
        GPIO.output(TL2RED, GPIO.LOW)
        GPIO.output(TL2YELLOW, GPIO.LOW)
        GPIO.output(TL2GREEN, GPIO.LOW)


def turn_one_green(id):
    if id == 0:
        GPIO.output(TL1RED, GPIO.LOW)
        GPIO.output(TL1YELLOW, GPIO.LOW)
        GPIO.output(TL1GREEN, GPIO.HIGH)
    elif id == 1:
        GPIO.output(TL2RED, GPIO.LOW)
        GPIO.output(TL2YELLOW, GPIO.LOW)
        GPIO.output(TL2GREEN, GPIO.HIGH)


def turn_one_redyellow(id):
    if id == 0:
        GPIO.output(TL1RED, GPIO.HIGH)
        GPIO.output(TL1YELLOW, GPIO.HIGH)
        GPIO.output(TL1GREEN, GPIO.LOW)
    elif id == 1:
        GPIO.output(TL2RED, GPIO.HIGH)
        GPIO.output(TL2YELLOW, GPIO.HIGH)
        GPIO.output(TL2GREEN, GPIO.LOW)


def turn_one_red(id):
    if id == 0:
        GPIO.output(TL1RED, GPIO.HIGH)
        GPIO.output(TL1YELLOW, GPIO.LOW)
        GPIO.output(TL1GREEN, GPIO.LOW)
    elif id == 1:
        GPIO.output(TL2RED, GPIO.HIGH)
        GPIO.output(TL2YELLOW, GPIO.LOW)
        GPIO.output(TL2GREEN, GPIO.LOW)


def turn_one_yellow(id):
    if id == 0:
        GPIO.output(TL1RED, GPIO.LOW)
        GPIO.output(TL1YELLOW, GPIO.HIGH)
        GPIO.output(TL1GREEN, GPIO.LOW)
    elif id == 1:
        GPIO.output(TL2RED, GPIO.LOW)
        GPIO.output(TL2YELLOW, GPIO.HIGH)
        GPIO.output(TL2GREEN, GPIO.LOW)


async def animate(id, end_state):
    global timestamp

    semaphore_state = get_semaphore_state(id)
    if semaphore_state == end_state:
        return

    await asyncio.sleep(3 if semaphore_state == "yellow" else 1)
    if semaphore_state == "green":
        turn_one_yellow(id)
    elif semaphore_state == "yellow":
        turn_one_red(id)
    elif semaphore_state == "redyellow":
        turn_one_green(id)
    elif semaphore_state == "red":
        turn_one_redyellow(id)
    elif semaphore_state == "off":
        turn_one_green(id)

    timestamp = time.time()
    await animate(id, end_state)


async def set_semaphore(main_state):
    global timestamp
    if main_state == "off":
        turn_all_off()
    elif main_state == "red":
        await animate(0, "red")
        await animate(1, "green")
    elif main_state == "green":
        await animate(1, "red")
        await animate(0, "green")


class BackgroundRunner:
    async def run_main(self):
        global timestamp, zebra
        while True:
            time_dif = time.time() - timestamp
            if (
                time_dif >= 10
                and get_semaphore_state(0) == "red"
                and get_semaphore_state(1) == "green"
            ):
                await set_semaphore("green")
            elif time_dif >= 2 and zebra == True:
                zebra = False
                await set_semaphore("red")
            await asyncio.sleep(1)
