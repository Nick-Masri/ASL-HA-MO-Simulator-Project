from classes import *


def test_person_get_origin():
    person = Person(1, 2, 10, 1)
    assert person.get_origin() == 1


def test_person_update_status():
    person = Person(1, 2, 10, 1)
    request = [3, 2, 1]
    person.update_status(request)
    assert Person(3, 2, 1, 1) == person