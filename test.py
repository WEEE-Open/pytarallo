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

tarallo.tsession.login()
def test_request():
    assert tarallo.tsession.request

def test_cookies():
    assert tarallo.tsession.cookie

def test_tarallo_login():
    assert tarallo.tsession.request.status_code == 204

