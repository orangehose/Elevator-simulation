import pytest
from elevator import Elevator, ElevatorDirection
from passenger import Passenger
from collections import deque


def test_elevator_max_floor_zero():
    with pytest.raises(ValueError):
        Elevator(0, 4, 0.1)


def test_elevator_max_floor_less_zero():
    with pytest.raises(ValueError):
        Elevator(-7, 4, 0.1)


def test_elevator_max_floor_string():
    with pytest.raises(TypeError):
        Elevator("ffv", 4, 0.1)


def test_elevator_max_floor_list():
    with pytest.raises(TypeError):
        Elevator([1, "2", [3]], 4, 0.1)


def test_elevator_max_floor_dict():
    with pytest.raises(TypeError):
        Elevator({"1": 1, "2": 2}, 4, 0.1)


def test_elevator_max_passengers_zero():
    with pytest.raises(ValueError):
        Elevator(10, 0, 0.1)


def test_elevator_max_passengers_less_zero():
    with pytest.raises(ValueError):
        Elevator(10, -100, 0.1)


def test_elevator_max_passengers_string():
    with pytest.raises(TypeError):
        Elevator(10, "temp", 0.1)


def test_elevator_max_passengers_list():
    with pytest.raises(TypeError):
        Elevator(10, ["temp", 2], 0.1)


def test_elevator_max_passengers_dict():
    with pytest.raises(TypeError):
        Elevator(10, {"1": 1, "2": 2}, 0.1)


def test_elevator_tick_rate_less_zero():
    with pytest.raises(ValueError):
        Elevator(10, 4, -1)


def test_elevator_tick_rate_string():
    with pytest.raises(TypeError):
        Elevator(10, 4, "8")


def test_elevator_tick_rate_list():
    with pytest.raises(TypeError):
        Elevator(10, 4, ["8", 9, "b"])


def test_elevator_tick_rate_dict():
    with pytest.raises(TypeError):
        Elevator(10, 4, {"8": 9, "b": 4})


def test_elevator_print_status(capsys):
    elevator = Elevator(10, 4, 0.1)
    elevator.print_status()
    captured = capsys.readouterr()

    assert captured.out == "Elevator status is: ElevatorStatus.IDLE\n------------------\n"


def test_elevator_move_without_direction():
    elevator = Elevator(10, 4, 0.1)
    elevator.move()
    assert elevator.current_floor == 1


def test_elevator_move_up_direction():
    elevator = Elevator(10, 4, 0.1)
    elevator.floor_to_reach = 2
    elevator.set_direction()
    elevator.move()
    assert elevator.current_floor == 2


def test_elevator_move_down_direction():
    elevator = Elevator(10, 4, 0.1)
    elevator.current_floor = 10
    elevator.floor_to_reach = 9
    elevator.set_direction()
    elevator.move()
    assert elevator.current_floor == 9


def test_elevator_set_direction_up():
    elevator = Elevator(10, 4, 0.1)
    elevator.current_floor = 1
    elevator.floor_to_reach = 5
    elevator.set_direction()
    assert elevator.direction == ElevatorDirection.UP


def test_elevator_set_direction_down():
    elevator = Elevator(10, 4, 0.1)
    elevator.current_floor = 7
    elevator.floor_to_reach = 5
    elevator.set_direction()
    assert elevator.direction == ElevatorDirection.DOWN


def test_can_enter_elevator_true():
    elevator = Elevator(10, 4, 0.1)

    elevator.current_floor = 3
    elevator.can_enter_elevator(3)

    assert elevator.can_enter_elevator(3) is True


def test_can_enter_elevator_different_floors():
    elevator = Elevator(10, 4, 0.1)

    elevator.current_floor = 1
    elevator.can_enter_elevator(3)

    assert elevator.can_enter_elevator(3) is False


def test_can_enter_elevator_if_he_is_full():
    elevator = Elevator(10, 1, 0.1)
    passenger = Passenger(3, 6, elevator)

    elevator.passengers[passenger.uuid] = passenger
    elevator.current_floor = 3
    elevator.can_enter_elevator(3)

    assert elevator.can_enter_elevator(3) is False


def test_enter_elevator_true():
    elevator = Elevator(10, 4, 0.1)
    passenger = Passenger(3, 6, elevator)

    elevator.current_floor = 3
    elevator.passengers = {}
    elevator.pending_passengers[passenger.uuid] = passenger.desired_floor
    elevator.enter_elevator(passenger.uuid, passenger.desired_floor)

    assert len(elevator.pending_passengers) == 0
    assert len(elevator.passengers) == 1


def test_elevator_call_elevator():
    elevator = Elevator(10, 4, 0.1)
    passenger = Passenger(3, 6, elevator)
    passenger.call_elevator()
    assert passenger.uuid in elevator.pending_passengers.keys()


def test_elevator_call_inside_elevator():
    elevator = Elevator(10, 4, 0.1)
    elevator.call_queue = deque([])
    elevator.call_inside_elevator(6)

    assert elevator.call_queue == deque([6])


def test_elevator_call_outside_elevator():
    elevator = Elevator(10, 4, 0.1)
    elevator.call_outside_elevator(3, 6)

    assert elevator.call_queue == deque([3, 6])


def test_elevator_release_passengers():
    """
    Passenger inside elevator goes out to this floor

    :return: None
    """
    elevator = Elevator(10, 4, 0.1)
    passenger = Passenger(3, 6, elevator)

    elevator.passengers = {}
    elevator.current_floor = 6
    elevator.passengers[passenger.uuid] = 6

    elevator.release_passengers()
    assert len(elevator.passengers) == 0


def test_elevator_enter_pending_passengers():
    elevator = Elevator(10, 4, 0.1)
    passenger = Passenger(3, 6, elevator)

    elevator.passengers = {}
    elevator.current_floor = 3
    elevator.pending_passengers[passenger.uuid] = passenger

    elevator.enter_pending_passengers()
    assert len(elevator.passengers) == 1


def test_elevator_get_pending_floors():
    elevator = Elevator(10, 4, 0.1)
    elevator.pending_passengers = {}

    passenger1 = Passenger(3, 6, elevator)
    passenger2 = Passenger(4, 6, elevator)

    elevator.pending_passengers[passenger1.uuid] = passenger1
    elevator.pending_passengers[passenger2.uuid] = passenger2

    assert elevator.get_pending_floors() == [3, 4]


def test_elevator_get_floors_to_open():
    elevator = Elevator(10, 4, 0.1)
    passenger1 = Passenger(4, 6, elevator)
    passenger2 = Passenger(5, 6, elevator)
    passenger3 = Passenger(1, 8, elevator)

    elevator.pending_passengers[passenger1.uuid] = passenger1
    elevator.pending_passengers[passenger2.uuid] = passenger2
    elevator.pending_passengers[passenger3.uuid] = passenger3

    # Elevator travels from the 3rd to the 7th floor, on the way stopping at 4th, 5th, 6th floors, ignoring 1st
    elevator.call_queue = [4, 5, 6, 1]
    elevator.current_floor = 3
    elevator.floor_to_reach = 7
    elevator.direction = ElevatorDirection.UP

    assert elevator.get_floors_to_open() == [4, 5]


def test_passenger_current_floor_zero():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(ValueError):
        Passenger(0, 8, elevator)


def test_passenger_current_floor_string():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(TypeError):
        Passenger("", 8, elevator)


def test_passenger_current_floor_list():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(TypeError):
        Passenger(["1", 1, "2", 2], 8, elevator)


def test_passenger_current_floor_dict():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(TypeError):
        Passenger({"1": 1, "2": 2}, 8, elevator)


def test_passenger_desired_floor_zero():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(ValueError):
        Passenger(1, 0, elevator)


def test_passenger_desired_floor_string():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(TypeError):
        Passenger(1, "temp", elevator)


def test_passenger_desired_floor_list():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(TypeError):
        Passenger(1, [4,7], elevator)


def test_passenger_desired_floor_dict():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(TypeError):
        Passenger(1, {"8": 16}, elevator)


def test_passenger_elevator_int():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(AttributeError):
        Passenger(1, 6, 5)


def test_passenger_elevator_string():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(AttributeError):
        Passenger(1, 6, "elevator")


def test_passenger_elevator_list():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(AttributeError):
        Passenger(1, 6, ["elevator", 15])


def test_passenger_elevator_dict():
    elevator = Elevator(10, 4, 0.1)
    with pytest.raises(AttributeError):
        Passenger(1, 6, {"8": 16})
