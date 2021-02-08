from collections import namedtuple
from rndt.uuidhandler import UUIDHandler
from unittest.mock import patch
import unittest


class TestUUIDHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.sut = namedtuple("Instance", ("uuid"))

    def test_should_return_an_uuid_if_the_instance_one_is_empty(self):
        self.sut.uuid = 'ipa:123abc456'
        actual = UUIDHandler.create_uuid(self.sut)
        self.assertEqual("ipa:123abc456", actual)
    
    @patch("uuid.uuid1")
    def test_should_return_the_instance_uuid_with_the_ipa_code_if_is_not_present(self, mocked_uuid):
        mocked_uuid.return_value = "123abc456"
        self.sut.uuid = ''
        actual = UUIDHandler.create_uuid(self.sut)
        self.assertEqual("ipa:123abc456", actual)

    def test_should_return_the_instance_uuid_with_the_ipa_code_if_ipa_code_is_present(self):
        self.sut.uuid = 'ipa:123abc456'
        actual = UUIDHandler.create_uuid(self.sut)
        self.assertEqual("ipa:123abc456", actual)

    def test_should_return_the_instance_uuid_with_the_ipa_code_if_ipa_code_is_present(self):
        self.sut.uuid = 'ipa:123abc456'
        actual = UUIDHandler.create_uuid(self.sut)
        self.assertEqual("ipa:123abc456", actual)

    def test_the_max_length_of_a_uuid_with_ipa_must_be_36_char(self):
        self.sut.uuid = 'd1fbf97f-e44a-4c60-87e2-56dc424b29b5-e44a-87e2'
        actual = UUIDHandler.create_uuid(self.sut)
        self.assertEqual("ipa:d1fbf97f-e44a-4c60-87e2-56dc424b", actual)
        self.assertEqual(36, len(actual))
