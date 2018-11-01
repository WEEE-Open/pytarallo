from tarallo import Tarallo
from os import environ as env

try:
    t_url = env['TARALLO_URL']
    t_user = env['TARALLO_USER']
    t_pass = env['TARALLO_PASS']
except KeyError:
    exit(1)

tsession = Tarallo(t_url, t_user, t_pass)

def test_create_session():
    assert tsession

tsession.login()

def test_request():
    assert tsession.request

def test_cookies():
    assert tsession.cookie

def test_tarallo_login():
    assert tsession.request.status_code == 204

