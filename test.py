import tarallo
from tarallo import Tarallo, Item
from os import environ as env

try:
    t_url = env['TARALLO_URL']
    t_user = env['TARALLO_USER']
    t_pass = env['TARALLO_PASS']
except KeyError:
    exit(1)


def test_create_session_and_tsession_var():
    tarallo.tsession = Tarallo(t_url, t_user, t_pass)
    assert tarallo.tsession is not None
    assert tarallo.tsession == tarallo.get_tsession()
    tarallo.tsession = None


def test_status_before_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    status = tarallo_session.status()
    assert status is False


def test_status_after_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.login()
    status = tarallo_session.status()
    assert status is True


def test_logout_before_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    tarallo_session.logout()
    status = tarallo_session.status()
    assert status is False


def test_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    result = tarallo_session.login()
    assert result is True


def test_invalid_login():
    tarallo_session = Tarallo(t_url, 'invalid', 'invalid')
    result = tarallo_session.login()
    assert result is False
    status = tarallo_session.status()
    assert status is False


def test_tarallo_login_and_logut():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    assert tarallo_session.status() is False
    assert tarallo_session.login() is True
    assert tarallo_session.status() is True
    assert tarallo_session.logout() is True
    assert tarallo_session.status() is False


def test_tarallo_request_after_status():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    assert tarallo_session.request is None
    tarallo_session.login()
    tarallo_session.status()
    assert tarallo_session.request is not None


def test_tarallo_request_after_login():
    tarallo_session = Tarallo(t_url, t_user, t_pass)
    assert tarallo_session.request is None
    tarallo_session.login()
    assert tarallo_session.request is not None


def test_tarallo_request_after_invalid_login():
    tarallo_session = Tarallo(t_url, 'invalid', 'invalid')
    assert tarallo_session.request is None
    tarallo_session.login()
    assert tarallo_session.request is not None


#def test_tarallo_cookie():
#    tarallo_session = Tarallo(t_url, t_user, t_pass)
#    assert tarallo_session.cookie is None
#    tarallo_session.login()
#    assert tarallo_session.cookie is not None
#    tarallo_session.logout()
#    assert tarallo_session.cookie is None
