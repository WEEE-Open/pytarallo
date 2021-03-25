import json
from datetime import datetime
from collections import Iterable
from os import environ as env
from nose.tools import *
from dotenv import load_dotenv

from pytarallo.AuditEntry import AuditEntry
from pytarallo.Item import Item
from pytarallo.ItemToUpload import ItemToUpload
from pytarallo.Product import Product
from pytarallo.ProductToUpload import ProductToUpload
from pytarallo.Tarallo import Tarallo
from pytarallo.Errors import ItemNotFoundError, LocationNotFoundError, ValidationError

load_dotenv()

try:
    t_url = env['TARALLO_URL']
    t_token = env['TARALLO_TOKEN']
except KeyError:
    raise EnvironmentError("Missing definitions of TARALLO_* environment variables (see README)")


def test_invalid_login():
    tarallo_session = Tarallo(t_url, 'invalid')
    assert tarallo_session.status() == 401


def test_login():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.status() == 200


@raises(ItemNotFoundError)
def test_get_invalid_item():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.get_item('asd')


def test_get_item():
    tarallo_session = Tarallo(t_url, t_token)
    item = tarallo_session.get_item('schifomacchina')
    assert item is not None
    assert type(item) == Item
    assert item.code == 'SCHIFOMACCHINA'
    assert isinstance(item.features, dict)
    assert isinstance(item.product, Product)
    assert item.product.features["type"] == "case"
    assert item.location == ["Polito", "Chernobyl", "Table"]


def test_get_item_history():
    tarallo_session = Tarallo(t_url, t_token)
    history = tarallo_session.get_history('schifomacchina')
    assert history is not None
    assert len(history) > 0
    for entry in history:
        assert isinstance(entry, AuditEntry)
        assert entry.user is not None
        assert entry.time is not None
        assert entry.time > 0


def test_remove_item():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.remove_item('R222')
    tarallo_session.restore_item('R222', 'schifomacchina')


def test_remove_item_twice():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.remove_item('R223')
    assert tarallo_session.remove_item('R223')
    tarallo_session.restore_item('R223', 'schifomacchina')


def test_remove_with_content():
    tarallo_session = Tarallo(t_url, t_token)
    # This fails because deleting items is like "rm", not "rm -r"
    assert not tarallo_session.remove_item('schifomacchina')


def test_remove_invalid_item():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.remove_item('invalid') is None


def test_restore_item():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.remove_item('R242')
    assert tarallo_session.restore_item('R242', 'schifomacchina')


def test_move_item():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.move("R111", 'schifomacchina')


def test_add_remove_products():
    tarallo_session = Tarallo(t_url, t_token)
    data = {
        "brand": "testBrand",
        "model": "testModel",
        "variant": "testVariant",
        "features": {"psu-volt": 19}
    }
    deleted = tarallo_session.delete_product(data.get("brand"), data.get("model"), data.get("variant"))
    assert deleted or deleted is None
    p = ProductToUpload(data)
    assert tarallo_session.add_product(p)


@raises(ValidationError)
def test_add_duplicate_products():
    tarallo_session = Tarallo(t_url, t_token)
    data = {
        "brand": "testBrand",
        "model": "testModel",
        "variant": "testVariant",
        "features": {"psu-volt": 12}
    }
    p = ProductToUpload(data)
    # Remove and add
    deleted = tarallo_session.delete_product(data.get("brand"), data.get("model"), data.get("variant"))
    assert deleted or deleted is None
    assert tarallo_session.add_product(p)
    # This one fails
    tarallo_session.add_product(p)


def test_get_product():
    tarallo_session = Tarallo(t_url, t_token)
    p = tarallo_session.get_product("testBrand", "testModel", "testVariant")
    assert type(p) == Product
    assert p.brand == "testBrand"
    assert p.model == "testModel"
    assert p.variant == "testVariant"
    assert isinstance(p.features, dict)


def test_get_product2():
    tarallo_session = Tarallo(t_url, t_token)
    p = tarallo_session.get_product("Samsung", "S667ABC1024", "v1")
    assert type(p) == Product
    assert p.brand == "Samsung"
    assert p.model == "S667ABC1024"
    assert p.variant == "v1"
    assert isinstance(p.features, dict)
    assert len(p.features) > 0


def test_get_product_list():
    tarallo_session = Tarallo(t_url, t_token)
    pl = tarallo_session.get_product_list("Samsung", "S667ABC1024")
    assert isinstance(pl, list)
    assert len(pl) == 2
    assert type(pl[0]) == Product
    assert type(pl[1]) == Product


@raises(ItemNotFoundError)
def test_move_item_not_existing():
    tarallo_session = Tarallo(t_url, t_token)
    assert tarallo_session.move("INVALID", 'schifomaccchina')


@raises(LocationNotFoundError)
def test_move_item_not_existing_location():
    tarallo_session = Tarallo(t_url, t_token)
    assert not tarallo_session.move("R200", "INVALID")


@raises(ValidationError)
def test_move_item_impossible():
    tarallo_session = Tarallo(t_url, t_token)
    # Invalid nesting, cannot place a RAM inside a CPU
    assert tarallo_session.move("R200", "C1")


def test_update_product_feature():
    tarallo_session = Tarallo(t_url, t_token)
    p = tarallo_session.get_product('AMD', 'Opteron 3300', 'AJEJE')
    assert p.features['type'] == 'cpu'
    if 'color' in p.features and p.features['color'] == 'red':
        new_features = {"color": "grey"}
    else:
        new_features = {"color": "red"}

    tarallo_session.update_product_features('AMD', 'Opteron 3300', 'AJEJE', new_features)

    p = tarallo_session.get_product('AMD', 'Opteron 3300', 'AJEJE')
    assert p.features["type"] == 'cpu'
    assert p.features["color"] == new_features["color"]


def test_delete_product_feature():
    tarallo_session = Tarallo(t_url, t_token)
    p = tarallo_session.get_product('AMD', 'Opteron 3300', 'AJEJE')
    assert p.features['type'] == 'cpu'
    # Add feature if missing
    if 'color' not in p.features and p.features['color'] == 'red':
        new_features = {"color": "grey"}
        tarallo_session.update_product_features('AMD', 'Opteron 3300', 'AJEJE', new_features)
        p = tarallo_session.get_product('AMD', 'Opteron 3300', 'AJEJE')
    assert "color" in p.features

    new_features = {"color": None}
    tarallo_session.update_product_features('AMD', 'Opteron 3300', 'AJEJE', new_features)
    p = tarallo_session.get_product('AMD', 'Opteron 3300', 'AJEJE')
    assert p.features["type"] == 'cpu'
    assert "color" not in p.features


def test_update_one_feature():
    tarallo_session = Tarallo(t_url, t_token)
    work = tarallo_session.get_item('R777').features['working']

    new_feat = 'yes' if work != 'yes' else 'no'

    # If operation succeeds, return True
    assert tarallo_session.update_item_features('R777', {'working': new_feat})
    freq_updated = tarallo_session.get_item('R777').features['working']
    assert freq_updated == new_feat


def test_delete_one_feature():
    tarallo_session = Tarallo(t_url, t_token)
    # Insert a frequency
    assert tarallo_session.update_item_features('R70', {'frequency-hertz': 800000000})

    # Remove it
    assert tarallo_session.update_item_features('R70', {'frequency-hertz': None})

    # Check that it's gone
    assert 'frequency-hertz' not in tarallo_session.get_item('R70').features

    # Add it again
    assert tarallo_session.update_item_features('R70', {'frequency-hertz': 800000000})


@raises(ValidationError)
def test_impossible_update():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_item_features('R198', {'color': 'impossible'})


@raises(ValidationError)
def test_impossible_update_no_such_feature():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_item_features('R198', {'nonexistent': 'foo'})


@raises(ValidationError)
def test_empty_update():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_item_features('R189', {})


@raises(ItemNotFoundError)
def test_update_item_not_found():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_item_features('NONEXISTENT', {'color': 'red'})


@raises(ItemNotFoundError)
def test_update_item_not_found_2():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.update_item_features('NONEXISTANT', {'color': None})


def test_add_item():
    tarallo_session = Tarallo(t_url, t_token)
    ram = ItemToUpload()
    ram.features["type"] = "ram"
    ram.features["color"] = "red"
    ram.features["capacity-byte"] = 1024 * 1024 * 512  # 512 MiB
    ram.parent = "Table"

    assert tarallo_session.add_item(ram)

    # set the code to the one received from the server
    assert ram.code is not None
    assert isinstance(ram.code, str)

    # Let's get it again and check...
    ram = tarallo_session.get_item(ram.code)
    assert ram.location == 'Table'
    assert ram.features["type"] == "ram"
    assert ram.features["color"] == "red"
    assert ram.features["capacity-byte"] == 1024 * 1024 * 512


def test_add_item_cloned():
    tarallo_session = Tarallo(t_url, t_token)
    cpu = tarallo_session.get_item("C100TEST")
    assert cpu is not None

    cpu_to_upload = ItemToUpload(cpu)
    assert cpu.code == cpu_to_upload.code
    assert cpu.location[-1] == cpu_to_upload.parent
    assert len(cpu.features) == len(cpu_to_upload.features)

    # It comes from a computer, path will still contain that, I don't care: I want it on the Table.
    # Send this location to the server, not the path.
    cpu_to_upload.set_parent("Table")
    assert cpu.location[-1] != cpu_to_upload.parent

    # Let the server generate another code (since there's no way to delete items permanently we
    # can't test manually assigned codes... or rather we can, but just once)
    cpu_to_upload.set_code(None)
    assert cpu.code != cpu_to_upload.code

    # Add it: should succeed
    assert tarallo_session.add_item(cpu_to_upload)

    # Let's get the entire item again and check...
    # The generated code was added to the original dict
    cpu_cloned = tarallo_session.get_item(cpu_to_upload.code)

    assert cpu_cloned.code != cpu.code
    assert cpu_cloned.location[-1] == cpu_to_upload.parent
    assert len(cpu_cloned.features) == len(cpu_to_upload.features)


@raises(ValidationError)
def test_add_item():
    tarallo_session = Tarallo(t_url, t_token)

    ram = ItemToUpload()
    ram.set_code("!N\\/@L!D")
    ram.set_parent("Table")
    ram.features = {'type': 'ram'}
    tarallo_session.add_item(ram)


# TODO: why is this so slow?
def test_travaso():
    tarallo_session = Tarallo(t_url, t_token)
    test_item = tarallo_session.travaso("schifomacchina", "RamBox")
    assert test_item

    item_r69 = tarallo_session.get_item("R69")
    assert item_r69 is not None
    assert type(item_r69) == Item
    assert item_r69.code == 'R69'
    assert isinstance(item_r69.features, dict)
    assert item_r69.location[-1] == 'RamBox'

    item_r188 = tarallo_session.get_item("R188")
    assert item_r188 is not None
    assert type(item_r188) == Item
    assert item_r188.code == 'R188'
    assert isinstance(item_r188.features, dict)
    assert item_r188.location[-1] == 'RamBox'

    tarallo_session.move("R69", "schifomacchina")
    tarallo_session.move("R188", "schifomacchina")


@raises(ItemNotFoundError)
def test_travaso_invalid_item():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.travaso("BIGASD", "Table")


@raises(LocationNotFoundError)
def test_travaso_not_existing_location():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.travaso("schifomacchina", "BIGASD")


@raises(ValidationError)
def test_travaso_invalid_location():
    tarallo_session = Tarallo(t_url, t_token)
    # Cannot place a computer in a RAM
    tarallo_session.travaso("schifomacchina", "R180")


def test_codes_by_feature():
    tarallo_session = Tarallo(t_url, t_token)
    codes = tarallo_session.get_codes_by_feature("model", "S667ABC256")
    assert isinstance(codes, Iterable)
    # noinspection PyTypeChecker
    assert len(codes) > 0
    # These are all motherboards
    for code in codes:
        assert isinstance(code, str)
        assert code.startswith('R')
        assert code[1:].isdigit()


def test_codes_by_feature_none():
    tarallo_session = Tarallo(t_url, t_token)
    codes = tarallo_session.get_codes_by_feature("sn", "invalid-serial-number-doesnt-exist")
    assert len(codes) == 0


@raises(ValidationError)
def test_codes_by_feature_invalid_feature():
    tarallo_session = Tarallo(t_url, t_token)
    tarallo_session.get_codes_by_feature("invalid-feature", "test")


@raises(ValidationError)
def test_codes_by_feature_invalid_feature():
    tarallo_session = Tarallo(t_url, t_token)
    # Cannot do an exact match on float/double values
    tarallo_session.get_codes_by_feature("psu-vol", "17.3")


def test_bulk_add():
    tarallo_session = Tarallo(t_url, t_token)
    # Cannot do an exact match on float/double values
    upload = """[
  {
    "type": "I",
    "features": {
      "brand": "OilData",
      "model": "Grand Junction 62000",
      "variant": "default",
      "type": "case",
      "working": "yes"
    },
    "contents": [
      {
        "features": {
          "brand": "USAStek computer inc.",
          "model": "P5KPL-VM",
          "variant": "default",
          "mac": "00:1b:33:42:42:42",
          "sn": "MT707BK05828930",
          "type": "motherboard",
          "working": "yes"
        },
        "contents": [
          {
            "code": "C251",
            "features": {
              "brand": "Intel",
              "model": "Core 2 Duo E8200",
              "variant": "default",
              "type": "cpu",
              "working": "yes"
            }
          },
          {
            "features": {
              "brand": "Samsung",
              "model": "M3 78T2863DZS-CF7",
              "sn": "589442786",
              "variant": "default",
              "type": "ram",
              "working": "yes"
            }
          },
          {
            "code": "R597",
            "features": {
              "brand": "Samsung",
              "model": "M3 78T2953EZ3-CF7",
              "sn": "1231847313",
              "variant": "default",
              "type": "ram",
              "working": "yes"
            }
          }
        ]
      }
    ]
  },
  {
    "type": "P",
    "brand": "Samsung",
    "model": "M3 78T2953EZ3-CF7",
    "variant": "default",
    "features": {
      "capacity-byte": 1073741824,
      "color": "green",
      "frequency-hertz": 800000000,
      "ram-ecc": "no",
      "ram-form-factor": "dimm",
      "ram-timings": "6-6-6-18 as DDR2-800",
      "ram-type": "ddr2",
      "type": "ram"
    }
  },
  {
    "type": "P",
    "brand": "Intel",
    "model": "Core 2 Duo E8200",
    "variant": "default",
    "features": {
      "core-n": 2,
      "cpu-socket": "lga775",
      "frequency-hertz": 2660000000,
      "isa": "x86-64",
      "thread-n": 2,
      "type": "cpu"
    }
  },
  {
    "type": "P",
    "brand": "USAStek computer inc.",
    "model": "P5KPL-VM",
    "variant": "default",
    "features": {
      "color": "golden",
      "cpu-socket": "lga775",
      "ethernet-ports-1000m-n": 1,
      "ide-ports-n": 1,
      "integrated-graphics-brand": "Intel",
      "integrated-graphics-model": "82G33/G31 Express",
      "key-bios-setup": "Del",
      "mini-jack-ports-n": 3,
      "motherboard-form-factor": "microatx",
      "parallel-ports-n": 1,
      "pci-sockets-n": 2,
      "pcie-sockets-n": 2,
      "ps2-ports-n": 2,
      "psu-connector-cpu": "4pin",
      "psu-connector-motherboard": "atx-24pin",
      "ram-form-factor": "dimm",
      "ram-type": "ddr2",
      "sata-ports-n": 4,
      "serial-ports-n": 1,
      "type": "motherboard",
      "usb-ports-n": 4,
      "vga-ports-n": 1
    }
  }
]"""

    # Upload succeeds
    assert tarallo_session.bulk_add(json.loads(upload))

    identifier = f"pytarallo test {datetime.now().strftime('%H:%M:%S.%f')}"
    # Upload succeeds again
    assert tarallo_session.bulk_add(json.loads(upload), identifier)
    # Upload fails, duplicate
    assert not tarallo_session.bulk_add(json.loads(upload), identifier)
    # Upload succeeds with overwrite
    assert tarallo_session.bulk_add(json.loads(upload), identifier, True)
