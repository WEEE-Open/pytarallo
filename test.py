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


def test_invalid_login():
    tarallo_session = Tarallo(t_url, 'invalid', 'invalid')
    assert tarallo_session.login() is False
    assert tarallo_session.response.status_code == 400


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
    tarallo_session.logout()


def test_retry_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    tarallo_session.logout()
    assert tarallo_session.status() == 403
    item = tarallo_session.get_item('1')
    assert item.code == '1'
    tarallo_session.logout()


def test_retry_login_without_previous_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    assert tarallo_session.status() == 403
    assert tarallo_session.get_item('1').code == '1'
    tarallo_session.logout()


def test_remove_item():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    assert tarallo_session.remove_item('1') is True
    tarallo_session.logout()


def test_remove_invalid_item():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    assert tarallo_session.remove_item('asd') is False
    tarallo_session.logout()
