from classes import *


def test_person_get_origin():
    person = Person(1, 2, 10, 1)
    assert person.get_origin() == 1

def test_person_update_status():
    person = Person(1, 2, 10, 1)
    person.