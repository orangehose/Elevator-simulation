from enum import Enum
from time import sleep
from collections import deque
from itertools import islice
from uuid import UUID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from passenger import Passenger


class DoorStatus(Enum):
    CLOSED = 1
    OPENED = 2


class ElevatorStatus(Enum):
    IDLE = 1
    MOVING = 2


class ElevatorDirection(Enum):
    UP = 1
    DOWN = 2


class Door:
    status = DoorStatus.CLOSED

    def __init__(self, tick_rate=1.0):
        self.tick_rate = tick_rate

    def open(self) -> None:
        if not self.is_opened():
            self.status = DoorStatus.OPENED
            print("Door opened")

    def close(self) -> None:
        print("Door closing...")
        sleep(self.tick_rate)
        if self.is_opened():
            self.status = DoorStatus.CLOSED
            print("Door closed")

    def is_opened(self) -> bool:
        if self.status is DoorStatus.OPENED:
            return True
        else:
            return False


class Elevator:
    status = ElevatorStatus.IDLE
    direction = ElevatorDirection.UP

    pending_passengers = {}  # passengers waiting for the elevator
    passengers = {}  # passengers in the elevator

    current_floor = 1
    min_floor = 1
    need_to_stop = False

    floor_to_reach = current_floor
    call_queue = deque([])  # queue of floors which elevator have to visit

    def __init__(self, max_floor: int, max_passengers: int, tick_rate=1.0):
        if max_floor < 1:
            raise ValueError("max_floor must be higher than 1")
        else:
            self.max_floor = max_floor

        if max_passengers < 1:
            raise ValueError("max_passengers must be higher than 1")
        else:
            self.max_passengers = max_passengers

        if tick_rate < 0:
            raise ValueError("tick_rate must be higher than 1")
        else:
            self.tick_rate = tick_rate  # Delay in performing actions (opening a door, moving one floor)
        self.door = Door(tick_rate)

    def print_status(self) -> None:
        """
        Status output about whether the elevator is moving or stationary

        :return: None
        """
        print(f'Elevator status is: {self.status}')
        print('------------------')

    def move(self) -> None:
        """
        Move the elevator one floor

        :return: None
        """
        if self.status is ElevatorStatus.MOVING:
            if self.direction is ElevatorDirection.UP and self.current_floor < self.max_floor:
                self.current_floor += 1
            if self.direction is ElevatorDirection.DOWN and self.current_floor > self.min_floor:
                self.current_floor -= 1
            sleep(self.tick_rate)
            print(f'Im on {self.current_floor} floor')

    def call_elevator(self, passenger_instance: "Passenger") -> None:
        """
        Passenger calling the elevator
        This method determines whether the call was made from inside or outside

        :param passenger_instance: Passenger instance
        :return: None
        """
        self.pending_passengers[passenger_instance.uuid] = passenger_instance
        if passenger_instance.uuid not in self.passengers.keys():
            self.call_outside_elevator(passenger_instance.current_floor, passenger_instance.desired_floor)
        else:
            self.call_inside_elevator(passenger_instance.desired_floor)

    def can_enter_elevator(self, current_passenger_floor: int) -> bool:
        """
        Checking whether a passenger can enter the elevator

        :param current_passenger_floor:
        :return: bool
        """
        if len(self.passengers) < self.max_passengers and current_passenger_floor == self.current_floor:
            return True
        return False

    def enter_elevator(self, passenger_uuid: UUID, desired_floor: int) -> None:
        """
        Method of entry of one passenger into the elevator

        :param passenger_uuid: Passenger ID
        :param desired_floor: The floor needs to go to
        :return: None
        """
        self.passengers[passenger_uuid] = desired_floor
        self.pending_passengers.pop(passenger_uuid)
        print(f'Passenger with uuid = {passenger_uuid} entered elevator')

    def call_inside_elevator(self, desired_floor: int) -> None:
        """
        Simulation of a call from inside an elevator

        :param desired_floor: The floor needs to go to
        :return: None
        """
        if desired_floor not in self.call_queue:
            self.call_queue.append(desired_floor)

    def call_outside_elevator(self, current_floor: int, desired_floor: int) -> None:
        """
        Simulation of a call outside the elevator

        :param current_floor: Current floor
        :param desired_floor: The floor needs to go to
        :return: None
        """
        if current_floor not in self.call_queue:
            self.call_queue.append(current_floor)
        if desired_floor not in self.call_queue:
            self.call_queue.append(desired_floor)

        # The case when the queue already contains desired_floor with a zero element, i.e. the elevator is already
        # heading there, but the passenger did not enter the elevator due to overcrowding
        if desired_floor not in list(
                islice(self.call_queue, 1, len(self.call_queue))):
            self.call_queue.append(desired_floor)

    def release_passengers(self) -> None:
        """
        Release passengers

        :return: None
        """
        for key, desired_floor in list(self.passengers.items()):
            if desired_floor == self.current_floor:
                self.passengers.pop(key)
                print(f'Passenger with uuid = {key} exited from elevator')

    def stop_elevator(self) -> None:
        """
        Set a flag that will cause the run() method to abort

        :return: None
        """
        self.need_to_stop = True

    def enter_pending_passengers(self) -> None:
        """
        Let waiting passengers in

        :return: None
        """
        for key, passenger_instance in list(self.pending_passengers.items()):
            if passenger_instance.current_floor == self.current_floor:
                passenger_instance.enter_elevator()

        # Passengers who do not have time to enter are put back in queue
        for key, passenger_instance in list(self.pending_passengers.items()):
            if passenger_instance.current_floor == self.current_floor:
                passenger_instance.call_elevator()

    def get_pending_floors(self) -> list:
        """
        Returns a list of floors where they are waiting for an elevator

        :return: list of floors where elevators are expected
        """
        return [passenger_instance.current_floor for key, passenger_instance in list(self.pending_passengers.items())]

    def get_desired_floors(self) -> list:
        """
        Returns a list on which waiting users should stop

        :return: list of floors where waiting passengers need to go
        """
        return [passenger_instance.desired_floor for key, passenger_instance in list(self.pending_passengers.items())]

    def open_release_enter_close(self) -> None:
        """
        Simulate the opening of the elevator doors -> passengers exit -> passengers enter -> close the door

        :return: None
        """
        self.door.open()
        self.release_passengers()
        self.enter_pending_passengers()
        self.door.close()

    def set_direction(self) -> None:
        """
        Set the direction of movement of the elevator

        :return: None
        """
        if self.current_floor < self.floor_to_reach:
            self.direction = ElevatorDirection.UP
        else:
            self.direction = ElevatorDirection.DOWN
        self.status = ElevatorStatus.MOVING

    def get_floors_to_open(self) -> list:
        """
        Retrieve from queue list of floors that the elevator should visit on its way to the desired floor

        :return: list of floors to visit
        """
        pending_floors = self.get_pending_floors()
        desired_floors = self.get_desired_floors()
        floors_door_will_open = []

        if self.direction is ElevatorDirection.UP:
            possible_floors = [x for x in self.call_queue if self.current_floor <= x <= self.floor_to_reach]
            for floor in possible_floors:
                # Check that the floor in the queue is expected by either internal elevator passengers or
                # waiting passengers
                if floor in self.passengers.values() or floor in pending_floors:
                    floors_door_will_open.append(floor)

                    # Do not remove from the queue floors that are in the next queue, but which are needed
                    # by waiting passengers
                    if floor not in pending_floors and floor not in desired_floors:
                        self.call_queue = deque([x for x in self.call_queue if x != floor])
        else:
            possible_floors = [x for x in self.call_queue if self.current_floor >= x >= self.floor_to_reach]
            for floor in possible_floors:
                if floor in self.passengers.values() or floor in pending_floors:
                    floors_door_will_open.append(floor)

                    if floor not in pending_floors and floor not in desired_floors:
                        self.call_queue = deque([x for x in self.call_queue if x != floor])

        return floors_door_will_open

    def run(self) -> None:
        """
        Starting the elevator

        :return: None
        """
        while True:
            self.print_status()

            # Stopping elevator when passengers do not need it and when it is not moving anywhere
            if self.need_to_stop and len(self.passengers) == 0 and \
                    len(self.pending_passengers) == 0 and self.status is ElevatorStatus.IDLE:
                break

            if self.status is ElevatorStatus.IDLE:
                if self.call_queue:
                    self.floor_to_reach = self.call_queue.popleft()

                    # If floor where elevator is currently going is still awaited by passengers
                    # outside the elevator, add it to the queue
                    if self.floor_to_reach in self.get_desired_floors():
                        self.call_queue.append(self.floor_to_reach)

                    # If passengers inside the elevator do not need to go to that floor
                    if self.floor_to_reach not in self.passengers.values():
                        # if floor_to_reach for none of the waiting passengers matches their current floor
                        pending_floors = self.get_pending_floors()
                        if self.floor_to_reach not in pending_floors:
                            continue  # move to the next floor in the queue

                    self.set_direction()
            else:
                floors_door_will_open = []
                while self.current_floor != self.floor_to_reach:
                    floors_door_will_open.extend(self.get_floors_to_open())

                    # Opening doors on all floors along the route
                    if self.current_floor in floors_door_will_open:
                        self.open_release_enter_close()
                    self.move()

                self.open_release_enter_close()
                self.status = ElevatorStatus.IDLE
            sleep(self.tick_rate)
