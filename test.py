import tarallo
from tarallo import Tarallo, Item
from os import environ as env
from nose.tools import *
from dotenv import load_dotenv
load_dotenv()

try:
    t_url = env['TARALLO_URL']
    t_token = env['TARALLO_TOKEN']
except KeyError:
    exit(1)


def test_invalid_login():
    tarallo_session = Tarallo(t_url, 'invalid')
    assert tarallo_session.status() == 401


def test_login():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.status() is 200


@raises(tarallo.ItemNotFoundError)
def test_get_invalid_item():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.get_item('asd')


def test_get_item():
    tarallo_session = Tarallo(t_url, t_token)
    item = tarallo_session.get_item('1')
    assert item is not None
    assert type(item) == tarallo.Item
    assert item.code == '1'
    assert isinstance(item.features, dict)
    assert item.features["type"] == "case"


def test_remove_item():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.remove_item('R222') is True
    tarallo_session.restore_item('R222', 'B115')


def test_remove_item_twice():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.remove_item('R223') is True
    assert tarallo_session.remove_item('R223') is True
    tarallo_session.restore_item('R223', 'B115')


def test_remove_with_content():
    tarallo_session = Tarallo(t_url, t_token)
    # This fails because deleting items is like "rm", not "rm -r"
    assert tarallo_session.remove_item('1') is False


def test_remove_invalid_item():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.remove_item('invalid') is None


def test_restore_item():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.remove_item('R242')
    assert tarallo_session.restore_item('R242', 'B115') is True


def test_move_item():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.move("R111", "B30") is True


@raises(tarallo.ItemNotFoundError)
def test_move_item_not_existing():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.move("INVALID", "B103")


@raises(tarallo.LocationNotFoundError)
def test_move_item_not_existing_location():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.move("R200", "INVALID") is False


@raises(tarallo.ValidationError)
def test_move_item_impossible():
    tarallo_session = Tarallo(t_url, t_token)
    # Invalid nesting, cannot place a RAM inside a CPU
    assert tarallo_session.move("R200", "C106")


def test_update_one_feature():
    tarallo_session = Tarallo(t_url, t_token)
    freq = tarallo_session.get_item('R46').features['frequency-hertz']

    if freq % 2 == 0:
        new_freq = freq + 1
    else:
        new_freq = freq - 1
    # If operation succeeds, return True
    assert tarallo_session.update_features('R46', {'frequency-hertz': new_freq})
    freq_updated = tarallo_session.get_item('R46').features['frequency-hertz']
    assert freq_updated == new_freq


def test_delete_one_feature():
    tarallo_session = Tarallo(t_url, t_token)
    # Insert a frequency
    assert tarallo_session.update_features('R44', {'frequency-hertz': 266000000})

    # Remove it
    assert tarallo_session.update_features('R44', {'frequency-hertz': None})

    # Check that it's gone
    assert 'frequency-hertz' not in tarallo_session.get_item('R44').features

    # Add it again
    assert tarallo_session.update_features('R44', {'frequency-hertz': 266000000})


@raises(tarallo.ValidationError)
def test_impossible_update():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_features('R43', {'color': 'impossible'})


@raises(tarallo.ValidationError)
def test_impossible_update_no_such_feature():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_features('R43', {'nonexistent': 'foo'})


@raises(tarallo.ValidationError)
def test_empty_update():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_features('R43', {})


@raises(tarallo.ItemNotFoundError)
def test_update_item_not_found():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_features('NONEXISTENT', {'color': 'red'})


@raises(tarallo.ItemNotFoundError)
def test_update_item_not_found_2():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_features('NONEXISTANT', {'color': None})


def test_add_item():
    tarallo_session = Tarallo(t_url, t_token)
    ram = Item()
    ram.features["type"] = "ram"
    ram.features["color"] = "red"
    ram.features["capacity-byte"] = 1024 * 1024 * 512  # 512 MiB
    ram.location = "LabFis4"

    assert tarallo_session.add_item(ram) is True

    # set the code to the one received from the server
    assert ram.code is not None
    assert isinstance(ram.code, str)

    # Let's get it again and check...
    ram = tarallo_session.get_item(ram.code)
    assert ram.path[-1:] == ['LabFis4']
    assert ram.location == 'LabFis4'
    assert ram.features["type"] == "ram"
    assert ram.features["color"] == "red"
    assert ram.features["capacity-byte"] == 1024 * 1024 * 512


def test_add_item_cloned():
    tarallo_session = Tarallo(t_url, t_token)
    cpu = tarallo_session.get_item("C123")
    assert cpu is not None
    # it comes from a computer, path will still contain that, I don't care: I want it in LabFis4.
    # Send this location to the server, not the path.
    cpu.location = "LabFis4"
    # Let the server generate another code (since there's no way to delete items permanently we
    # can't test manually assigned codes... or rather we can, but just once)
    cpu.code = None
    # Add it: should succeed
    assert tarallo_session.add_item(cpu) is True

    # This stuff should be updated
    assert cpu.code is not None
    assert not cpu.code == "C123"
    # Just set path to none after inserting an item. The server doesn't return the full path so you have no way to
    # assign the correct value to this variable.
    # This assert checks just that:
    assert cpu.path is None

    # Let's get the entire item again and check...
    cpu = tarallo_session.get_item(cpu.code)
    assert cpu.path[-1:] == ['LabFis4']
    assert cpu.location == 'LabFis4'

    # This may seem redundant, but these are different feature types...
    assert cpu.features["brand"] == "Intel"
    assert cpu.features["type"] == "cpu"
    assert cpu.features["cpu-socket"] == "socket478"
    assert cpu.features["frequency-hertz"] == 3060000000


@raises(tarallo.ValidationError)
def test_add_item():
    tarallo_session = Tarallo(t_url, t_token)
    ram = Item()
    ram.code = "!N\\/@L!D"
    ram.features["type"] = "ram"
    ram.location = "LabFis4"

    tarallo_session.add_item(ram)


def test_travaso():
    tarallo_session = Tarallo(t_url, t_token)
    test_item = tarallo_session.travaso("1", "LabFis4")
    assert test_item is True

    item_a2 = tarallo_session.get_item("A2")
    assert item_a2 is not None
    assert type(item_a2) == tarallo.Item
    assert item_a2.code == 'A2'
    assert isinstance(item_a2.features, dict)
    assert item_a2.location == 'LabFis4'

    item_b1 = tarallo_session.get_item("B1")
    assert item_b1 is not None
    assert type(item_b1) == tarallo.Item
    assert item_b1.code == 'B1'
    assert isinstance(item_b1.features, dict)
    assert item_b1.location == 'LabFis4'

    tarallo_session.move("A2", "1")
    tarallo_session.move("B1", "1")


@raises(tarallo.ItemNotFoundError)
def test_travaso_invalid_item():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.travaso("BIGASD", "LabFis4")


@raises(tarallo.LocationNotFoundError)
def test_travaso_not_existing_location():
    tarallo_session = Tarallo(t_url, t_token)
    # TODO: "Cannot move A2 into BIGASD", returns 400... WHY?
    tarallo_session.travaso("1", "BIGASD")


@raises(tarallo.ValidationError)
def test_travaso_invalid_location():
    tarallo_session = Tarallo(t_url, t_token)
    # Cannot place the insides of a computer in a CPU
    tarallo_session.travaso("1", "C123")
