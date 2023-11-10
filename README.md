## Elevator simulation script
### How to start elevator simulation:
```shell script
python driver.py
```

### How to run tests
```shell script
python -m pytest elevator_tests.py
```

### Description
In **driver.py**, an elevator with 10 floors is created, from 1 to 10 passengers are generated,
who wait on randomly generated floors

The **elevator.py** contains the main logic for the elevator in the Elevator class. The elevator starts
calling the **.run()** method on the elevator instance. The elevator allows movement to one floor,
determining where the elevator call was made (inside or outside). The elevator lets you in and out
passengers depending on the condition of the doors and the floor required for the passenger.

The **passenger.py** contains the main logic for passenger behavior. The passenger can call the elevator,
enter it.
