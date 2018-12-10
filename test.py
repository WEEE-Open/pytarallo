import tarallo
from tarallo import Tarallo, Item
from os import environ as env
from nose.tools import *

try:
    t_url = env['TARALLO_URL']
    t_user = env['TARALLO_USER']
    t_pass = env['TARALLO_PASS']
except KeyError:
    exit(1)


@raises(tarallo.AuthenticationError)
def test_invalid_login():
    tarallo_session = Tarallo(t_url, 'invalid', 'invalid')
    tarallo_session.login()
    # Once an exception is raised, the test terminates...
    # Any assert after that is simply ignored, place a breakpoint there if you don't believe me...
    # assert tarallo_session.response.status_code == 400


def test_logout_before_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    assert tarallo_session.logout() is False
    assert tarallo_session.response is None


def test_login_and_logout():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    assert tarallo_session.login() is True
    assert tarallo_session.response.status_code == 204
    assert tarallo_session.logout() is True
    assert tarallo_session.response.status_code == 204


@raises(tarallo.ItemNotFoundError)
def test_get_invalid_item():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    tarallo_session.get_item('asd')
    tarallo_session.logout()


def test_get_item():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    item = tarallo_session.get_item('1')
    assert item is not None
    assert type(item) == tarallo.Item
    assert item.code == '1'
    assert isinstance(item.features, dict)
    assert item.features["type"] == "case"
    tarallo_session.logout()


def test_retry_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    tarallo_session.logout()
    assert tarallo_session.status(False) == 401
    item = tarallo_session.get_item('1')
    assert item.code == '1'
    tarallo_session.logout()


def test_retry_login_without_previous_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    assert tarallo_session.status(False) == 401
    assert tarallo_session.get_item('1').code == '1'
    tarallo_session.logout()


def test_remove_item():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    assert tarallo_session.remove_item('R222') is True
    tarallo_session.restore_item('R222', 'B115')
    tarallo_session.logout()


def test_remove_item_twice():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    assert tarallo_session.remove_item('R223') is True
    assert tarallo_session.remove_item('R223') is True
    tarallo_session.restore_item('R223', 'B115')
    tarallo_session.logout()


def test_remove_with_content():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    # This fails because deleting items is like "rm", not "rm -r"
    assert tarallo_session.remove_item('1') is False
    tarallo_session.logout()


def test_remove_invalid_item():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    assert tarallo_session.remove_item('invalid') is None
    tarallo_session.logout()


def test_restore_item():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    tarallo_session.remove_item('R242')
    assert tarallo_session.restore_item('R242', 'B115') is True
    tarallo_session.logout()


def test_move_item():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    assert tarallo_session.move("R111", "B30") is True
    tarallo_session.logout()


def test_move_item_invalid():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    assert tarallo_session.move("INVALID", "B103") is False
    assert tarallo_session.move("R200", "INVALID") is False
    tarallo_session.logout()


def test_move_item_impossible():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    # Invalid nesting, cannot place a RAM inside a CPU
    assert tarallo_session.move("R200", "C106") is False
    tarallo_session.logout()


def test_add_item():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    ram = Item()
    ram.features["type"] = "ram"
    ram.features["color"] = "red"
    ram.features["capacity"] = 1024*1024*512  # 512 MiB
    ram.location = "LabFis4"

    assert tarallo_session.add_item(ram) is True

    # set the code to the one received from the server
    assert ram.code is not None
    assert isinstance(ram.code, str)

    # Let's get it again and check...
    cpu = tarallo_session.get_item(ram.code)
    assert cpu.path[-1:] == "LabFis4"
    assert cpu.location == "LabFis4"
    assert ram.features["type"] == "ram"
    assert ram.features["color"] == "red"
    assert ram.features["capacity"] == 1024 * 1024 * 512


def test_add_item_cloned():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    cpu = tarallo_session.get_item("C123")
    assert cpu is not None
    # it comes from a computer, path will still contain that, I don't care: I want it in LabFis4.
    # Send this location to the server, not the path.
    cpu.location = "LabFis4"
    # Let the server generate another code (since there's no way to delete items permanently we
    # can't test manually assigned codes... or rather we can, but just once)
    cpu.code = None
    assert tarallo_session.add_item(cpu) is True
    assert cpu.code is not None
    assert not cpu.code == "C123"

    # Let's get it again and check...
    cpu = tarallo_session.get_item(cpu.code)
    assert cpu.path[-1:] == "LabFis4"
    assert cpu.location == "LabFis4"

    # This may seem redundant, but these are different feature types...
    assert cpu.features["brand"] == "Intel"
    assert cpu.features["type"] == "cpu"
    assert cpu.features["cpu-socket"] == "socket478"
    assert cpu.features["frequency"] == 3060000000

    tarallo_session.logout()
