from terec.model.util import model_to_dict
from terec.model.structure import Org


def test_model_to_dict():
    org = Org(name="my_org", full_name="My Organisation", url="http://my.org")
    d = model_to_dict(org)
    assert d is not None
    assert d["name"] == org.name
    assert d["full_name"] == org.full_name
    assert d["url"] == org.url
