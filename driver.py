from passenger import Passenger
from elevator import Elevator
import random


def generate_passengers(elevator_instance: Elevator) -> list:
    passengers = []
    for item in range(random.randint(1, 10)):
        current_floor = random.randint(1, max_floor)
        desired_floor = random.randint(1, max_floor)

        while current_floor == desired_floor:
            desired_floor = random.randint(1, max_floor)

        passengers.append(Passenger(current_floor, desired_floor, elevator_instance))
    return passengers


if __name__ == '__main__':
    max_floor = 10
    max_passengers = 4

    elevator = Elevator(max_floor, max_passengers, 0.01)
    passengers_pool = generate_passengers(elevator)

    for passenger in passengers_pool:
        passenger.call_elevator()

    elevator.stop_elevator()
    elevator.run()
