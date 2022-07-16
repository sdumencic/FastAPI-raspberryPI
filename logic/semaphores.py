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


async def set_all_to_red(id, state):
    for light in state["lights"]:
        if light["state"] != "red":
            pass
    # return {"msg": f"{id}, {state}"}


async def set_semaphore(id, light_state):
    if light_state == "off":
        # Turning both semaphores off
        for semaphore in SEMAPHORE_PINS:
            for color in ["red", "green", "yellow"]:
                pin = semaphore["pins"][color]
                GPIO.output(pin, GPIO.LOW)
                state["lights"][semaphore["id"]]["state"] = "off"
                state["timestamp"] = time.time()
    return {"msg": f"{id}, {state}"}
