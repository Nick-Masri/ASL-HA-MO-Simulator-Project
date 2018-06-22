from classes import *


# Persons
def test_person_get_origin():
    person = Person(1, 2, 10, 1)
    assert person.get_origin() == 1


def test_person_update_status():
    person = Person(1, 2, 10, 1)
    request = [3, 2, 1]
    car = 4
    person.update_status(request, car)
    assert Person(3, 2, 1, 4) == person


def test_employee_update_status():
    employee = Employee(1, 2, 10, 3, 23)
    request = [3, 2, 1]
    car = 5
    employee.update_status(request, car)
    assert Employee(3, 2, 1, 3, 23)


def test_employee_reset():
    origin = 1
    destination = 2
    origin_time = 10
    current_position = 3
    employee_id = 23
    employee = Employee(origin, destination, origin_time, employee_id)
    employee.reset()
    employee.change_current_position(None)
    new_employee = Employee(None, None, None, employee_id)
    assert new_employee.get_origin() == employee.get_origin()
    assert new_employee.get_destination() == employee.get_destination()
    assert new_employee.get_origin_time() == employee.get_origin_time()
    assert new_employee.get_destination_time() == employee.get_destination_time()
    assert new_employee.get_employee_id() == employee.get_employee_id()


# Stations
def test_update_station_list():
    stations = {1: Station(1, [], []), 3: Station(3, [], [])}
    person = Person(1, 2, 3)
    stations[3].append_en_route_list(person)
    assert person in stations[3].get_en_route_list()


def test_get_waiting_customers():
    a = Person(1, 2, 10)
    b = Person(1, 5, 3)
    c = Person(1, 2, 8)
    station = Station(1, [], [], [a, b, c])
    # Not sorted
    assert [a, b, c] == station.get_waiting_customers()

    # Sorted
    assert [b, c, a] == station.get_waiting_customers(True)

def test_get_en_route_list():
    a = Employee(1, 2, 10, 1)
    b = Employee(1, 5, 3, 2)
    c = Employee(1, 2, 8, 3)
    station = Station(1, [], [], [], [a, b, c])

    # Not sorted
    assert [a, b, c] == station.get_en_route_list()

    # Sorted
    assert [b, c, a] == station.get_en_route_list(True)