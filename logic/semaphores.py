import RPi.GPIO as GPIO
import time

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


state = {
    "timestamp": time.time(),
    "zebra": False,
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


async def set_all_to_red(state):
    for light in state["lights"]:
        if light["state"] != "red":
            pass
    # return {"msg": f"{id}, {state}"}


# Turning both semaphores off
def turn_all_off():
    for semaphore in SEMAPHORE_PINS:
        for color in ["red", "green", "yellow"]:
            pin = semaphore["pins"][color]
            GPIO.output(pin, GPIO.LOW)
            state["lights"][semaphore["id"]]["state"] = "off"


async def set_semaphore(main_state):
    if main_state == "off":
        turn_all_off()
        state["timestamp"] = time.time()
    elif main_state == "red":
        turn_all_off()
        GPIO.output(TL1RED, GPIO.HIGH)
        GPIO.output(TL2GREEN, GPIO.HIGH)
        state["timestamp"] = time.time()
        state["lights"][0]["state"] = "red"
        state["lights"][1]["state"] = "green"
    elif main_state == "green":
        turn_all_off()
        GPIO.output(TL1GREEN, GPIO.HIGH)
        GPIO.output(TL2RED, GPIO.HIGH)
        state["timestamp"] = time.time()
        state["lights"][0]["state"] = "green"
        state["lights"][1]["state"] = "red"
