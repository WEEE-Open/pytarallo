import tarallo
from tarallo import Tarallo, Item
from os import environ as env

try:
    t_url = env['TARALLO_URL']
    t_user = env['TARALLO_USER']
    t_pass = env['TARALLO_PASS']
except KeyError:
    exit(1)


def test_invalid_login():
    tarallo_session = Tarallo(t_url, 'invalid', 'invalid')
    assert tarallo_session.login() is False
    assert tarallo_session.last_request.status_code == 400


def test_logout_before_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    assert tarallo_session.logout() is False
    assert tarallo_session.last_request is None


def test_tarallo_login_and_logout():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    assert tarallo_session.login() is True
    assert tarallo_session.last_request.status_code == 204
    assert tarallo_session.logout() is True
    assert tarallo_session.last_request.status_code == 204


def test_tarallo_get_item_95():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    item = tarallo_session.get_item('95')
    assert item is not None
    assert type(item) == tarallo.Item
    assert item.code == '95'
    tarallo_session.logout()
