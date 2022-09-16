from sleeper import snooze, list_walks, do_complicated_thing, fundamentally_broken, csv_reader
from unittest.mock import patch, create_autospec, MagicMock
from unittest import TestCase
import pytest

@patch("time.sleep")
def test_snoozes(mocked_sleep=None):
  """Very basic mocking of a painful-to-really-run function, setting its return value
  and checking that the value of the actual function is as expected."""
  mocked_sleep.return_value = 4
  assert snooze(True) == 4


@patch("sleeper.time.sleep", return_value=4)  # seems more reliable?
def test_snoozes_local(mocked_sleep):
  """
  We can check what parameters it was called with -- keyword arguments look like keyword arguments
  so assert_called_with(1, 2, c=3, d=4)
  """
  assert snooze(True) == 4
  mocked_sleep.assert_called_with(60)

# @patch("sleeper.our_client")

@patch("client.Client")
@pytest.mark.xfail
def test_get_walks_failure(mocked_client):
  """
  This fails: the client has already been instantiated when the module was imported on line 1;
  so whilst we'll patch 'client' (we can import client and it'll be patched), our_client is already
  a real instance of client.Client

  From the documentation:
  "With patch() it matters that you patch objects in the namespace where they are looked up."
  https://docs.python.org/3/library/unittest.mock.html#where-to-patch
  """
  list_walks()
  # requests.exceptions.ConnectionError

@patch("sleeper.our_client")
def test_get_walks_success(mocked_client):
  """setting the return value of the item we've patched"""
  mocked_client.get.return_value = '[{"name": "unsilly", "silliness":0}, {"name": "very silly", "silliness": 9}]'
  assert "very silly" in str(list_walks())
  assert "unsilly" not in str(list_walks())

@patch("sleeper.our_client")
def test_do_the_thing_zhu_li(mocked_client):
  """Demonstrate chaining mocked items"""
  mocked_client.do.return_value.zhu.return_value = 4
  assert do_complicated_thing() == 4
  # It's very tempting to write 'assert ... called_with' but
  # that's just referring to a non-existent property on the mock.
  # Likewise, 'called_once' isn't a thing in python either
  mocked_client.do.assert_called_with(the='thing')
  mocked_client.do.return_value.zhu.assert_called_with('li')
  # Note also this example would fail with 'autospec=True' (see below)
  # because none of these methods actually exist on the client...


# it isn't clear to me if autospec or just plain spec are better...
@patch("sleeper.time.sleep", autospec=True) # has only the methods of the genuine article
@pytest.mark.xfail
def test_catch_missing_methods(mocked_sleep):
  """Strong recommend for using autospec to ensure that the arguments exist to catch
  problems where """
  snooze(True)
  assert mocked_sleep.called_with("not a real parameter") # True without autospec!
  # raises AttributeError: Mock object has no attribute 'called_with'
  # it's not clear to me if we should prefer


@patch("sleeper.our_client")
@patch("time.sleep")
def test_reverse_order(mocked_sleep, mocked_client):
  """If you need multiple patches, note that the parameters are in the reverse order!"""
  snooze(True)
  assert mocked_sleep.called
  assert not mocked_client.called

def test_crashes_correctly():
  """How to test exceptions are correctly raised"""
  with pytest.raises(RuntimeError):
    fundamentally_broken()

class Test_Stuff(TestCase):
  def test_crashes_correctly_unittest(self):
    """
    the unittest version wants classes which is a whole additional level of faff
    and not recommended, but you might see it.
    """
    with self.assertRaises(RuntimeError):
      fundamentally_broken()

####

@pytest.fixture
def walks_dictionary():
    return '[{"name": "unsilly", "silliness":0}, {"name": "very silly", "silliness": 9}]'


@patch("sleeper.our_client")
def test_get_walks_success_with_fixture(mocked_client, walks_dictionary):
  """We pass a dictionary to the mocked_client in a pretty standard way like above"""
  mocked_client.get.return_value = walks_dictionary
  assert "very silly" in str(list_walks())
  assert "unsilly" not in str(list_walks())

######

# Note how this one uses a fixture without @patch...
@pytest.fixture
def walks(monkeypatch):  # this is a special name of an existing fixture in pytest
  mocked_client = MagicMock()
  mocked_client.get.return_value = '[{"name": "unsilly", "silliness":0}, {"name": "very silly", "silliness": 9}]'
  monkeypatch.setattr("sleeper.our_client", mocked_client)

def test_get_walks_via_fixture(walks):
  result = list_walks()
  assert "very silly" in str(result)
  assert "unsilly" not in str(result)

############

@pytest.fixture(autouse=True) # use this fixture automatically for everything
def always_on(monkeypatch):
  csv_reader = MagicMock()
  csv_reader.return_value = "it,is,a,csv,file"
  monkeypatch.setattr("csv.reader", csv_reader)

def test_csv_reader():
  """Note how this test doesn't specify a fixture because the fixture 'always_on' has autouse=True"""
  assert csv_reader() == "it,is,a,csv,file"
