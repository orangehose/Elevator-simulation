from uuid import uuid4
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from elevator import Elevator


class Passenger:
    def __init__(self, current_floor: int, desired_floor: int, elevator: "Elevator"):
        if current_floor < 1:
            raise ValueError("current_floor must be higher than 1")
        else:
            self.current_floor = current_floor

        if desired_floor < 1 or desired_floor > elevator.max_floor:
            raise ValueError("desired_floor must be higher than 1 and less than 'elevator.max_floor'")
        else:
            self.desired_floor = desired_floor

        if str(type(elevator)) == "<class 'elevator.Elevator'>":
            self.elevator = elevator
        else:
            raise ValueError("elevator must be Elevator class instance")
        self.uuid = uuid4()

    def call_elevator(self):
        self.elevator.call_elevator(self)

    def enter_elevator(self):
        if self.elevator.can_enter_elevator(self.current_floor):
            self.elevator.enter_elevator(self.uuid, self.desired_floor)
