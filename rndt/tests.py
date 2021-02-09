from collections import namedtuple
from rndt.uuidhandler import UUIDHandler
from unittest.mock import patch
import unittest


class TestUUIDHandlerTestCase(unittest.TestCase):
    def setUp(self):
        group = namedtuple("Group", ("grouprofile"))
        groupprofile = namedtuple("GroupProfile", ("groupprofilerndt"))
        groupprofilerndt = namedtuple("GroupProfileRNDT", ("pa"))
        pa = namedtuple("PubblicaAmministrazione", ("ipa"))
        pa.ipa = "c_123"
        groupprofilerndt.pa = pa
        groupprofile.groupprofilerndt = groupprofilerndt
        group.groupprofile = groupprofile
        self.sut = namedtuple("Instance", ("uuid", "group"))
        self.sut.group = group

    def test_return_an_uuid_if_the_instance_one_is_not_empty(self):
        self.sut.group.groupprofile.groupprofilerndt.pa.ipa = "ipa"
        self.sut.uuid = "ipa:123abc456"
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("ipa:123abc456", actual)

    @patch("uuid.uuid1")
    def test_return_the_instance_uuid_with_the_ipa_code_if_the_uuid_is_not_present(
        self, mocked_uuid
    ):
        mocked_uuid.return_value = "123abc456"
        self.sut.uuid = ""
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("c_123:123abc456", actual)

    @patch("uuid.uuid1")
    def test_return_the_instance_uuid_if_the_uuid_and_ipa_are_not_present(
        self, mocked_uuid
    ):
        mocked_uuid.return_value = "123abc456"
        self.sut.uuid = ""
        self.sut.group = None
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("123abc456", actual)

    def test_return_the_instance_uuid_with_the_ipa_code_if_ipa_code_is_present(self):
        self.sut.group.groupprofile.groupprofilerndt.pa.ipa = "c_345"
        self.sut.uuid = "c_345:123abc456"
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("c_345:123abc456", actual)

    def test_return_the_instance_uuid_if_the_ipa_code_is_not_found(self):
        self.sut.group.groupprofile.groupprofilerndt = None
        self.sut.uuid = "123abc456"
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("123abc456", actual)

    def test_the_max_length_of_a_uuid_with_ipa_must_be_36_char(self):
        self.sut.uuid = "d1fbf97f-e44a-4c60-87e2-56dc424b29b5-e44a-87e2"
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("c_123:d1fbf97f-e44a-4c60-87e2-56dc42", actual)
        self.assertEqual(36, len(actual))

    def test_uuidhandler_should_extract_the_correct_ipa_code_if_exists(self):
        self.sut.uuid = "c_123:uuid"
        actual = UUIDHandler(self.sut)._extract_ipa()
        self.assertEqual("c_123", actual)

    def test_uuidhandler_should_extract_the_correct_uuid_code_if_exists(self):
        self.sut.uuid = "c_123:uuid"
        actual = UUIDHandler(self.sut)._extract_uuid()
        self.assertEqual("uuid", actual)

    def test_uuidhandler_should_extract_none_ipa_code_if_not_exists(self):
        self.sut.uuid = "d1fbf97f-e44a-4c60-87e2-56dc"
        actual = UUIDHandler(self.sut)._extract_ipa()
        self.assertFalse(actual)

    def test_uuidhandler_update_the_ipa_code_if_is_changed(self):
        self.sut.uuid = "123abc456"
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertFalse(actual)
