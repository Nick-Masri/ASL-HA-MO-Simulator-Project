from classes import *


def test_person_get_origin():
    person = Person(1, 2, 10, 1)
    assert person.get_origin() == 1


def test_person_update_status():
    person = Person(1, 2, 10, 1)
    request = [3, 2, 1]
    person.update_status(request)
    assert Person(3, 2, 1, 1) == person


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
    employee = Employee(origin, destination, origin_time, current_position, employee_id)
    employee.reset()
    employee.change_current_position(None)
    new_employee = Employee(None, None, None, destination, employee_id, None)
    assert new_employee == employee
