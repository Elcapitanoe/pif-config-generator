import pytest
from pif_generator.builder import Extractor, ProfileBuilder, PropParser
from pif_generator.models import ExtendedPIFProfile, LegacyPIFProfile


SAMPLE_PROP = """
ro.product.manufacturer=Google
ro.product.model=Pixel 9 Pro XL
ro.product.brand=google
ro.product.device=komodo
ro.product.system_ext.name=komodo_beta
ro.system_ext.build.id=CP41.260814.003.B1
ro.system_ext.build.fingerprint=google/komodo_beta/komodo:17/CP41.260814.003.B1/16166531:user/release-keys
ro.system_ext.build.type=user
ro.system_ext.build.tags=release-keys
ro.system_ext.build.version.release=17
ro.product.first_api_level=34
ro.debuggable=0
"""


def test_prop_parser():
    props = PropParser.parse(SAMPLE_PROP)
    assert props["ro.product.model"] == "Pixel 9 Pro XL"
    assert props["ro.system_ext.build.id"] == "CP41.260814.003.B1"
    assert props["ro.product.device"] == "komodo"


def test_build_extended_profile():
    props = PropParser.parse(SAMPLE_PROP)
    profile = ProfileBuilder.build_extended(props)
    assert isinstance(profile, ExtendedPIFProfile)
    assert profile.ID == "CP41.260814.003.B1"
    assert profile.BRAND == "google"
    assert profile.DEVICE == "komodo"
    assert profile.MANUFACTURER == "Google"
    assert profile.MODEL == "Pixel 9 Pro XL"
    assert profile.PRODUCT == "komodo_beta"
    assert profile.SECURITY_PATCH == "2026-08-14"
    assert profile.DEVICE_INITIAL_SDK_INT == "34"
    assert profile.TYPE == "user"
    assert profile.TAG == "release-keys"
    assert profile.RELEASE == "17"
    assert profile.DEBUG is False
    assert profile.spoofBuild == "1"


def test_build_legacy_profile():
    props = PropParser.parse(SAMPLE_PROP)
    profile = ProfileBuilder.build_legacy(props)
    assert isinstance(profile, LegacyPIFProfile)
    assert profile.MODEL == "Pixel 9 Pro XL"
    assert profile.FIRST_API_LEVEL == "34"
    assert profile.SECURITY_PATCH == "2026-08-14"


def test_invalid_sdk_validation():
    props = PropParser.parse(SAMPLE_PROP)
    props["ro.product.first_api_level"] = "10"
    with pytest.raises(Exception):
        ProfileBuilder.build_extended(props)


if __name__ == "__main__":
    test_prop_parser()
    test_build_extended_profile()
    test_build_legacy_profile()
    print("Self-test completed successfully.")
