from terec.model import model_to_dict, structure


def test_model_to_dict():
    org = structure.Org(name="my_org", full_name="My Organisation", url="http://my.org")
    d = model_to_dict(org)
    assert d is not None
    assert d["name"] == org.name
    assert d["full_name"] == org.full_name
    assert d["url"] == org.url
