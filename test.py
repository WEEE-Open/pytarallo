import tarallo
from tarallo import Tarallo, Item
from os import environ as env

try:
    t_url = env['TARALLO_URL']
    t_user = env['TARALLO_USER']
    t_pass = env['TARALLO_PASS']
except KeyError:
    exit(1)

tarallo.tsession = Tarallo(t_url, t_user, t_pass)
def test_create_session():
    assert tarallo.tsession

def test_equal_tsession():
    assert tarallo.tsession == tarallo.get_tsession()

status = tarallo.tsession.status()
def test_status_before_login():
    assert status == False

def test_logout_before_login():
    assert tarallo.tsession.logout() == False

login = tarallo.tsession.login()
def test_tarallo_request():
    assert tarallo.tsession.request

def test_tarallo_cookie():
    assert tarallo.tsession.cookie

def test_tarallo_login():
    assert tarallo.tsession.request.status_code == 204
    assert login == True

def test_status_after_login():
    assert tarallo.tsession.status() == True

def test_tarallo_logout():
    assert tarallo.tsession.logout() == True

def test_tarallo_cookie_after_logout():
    assert tarallo.tsession.cookie == None

