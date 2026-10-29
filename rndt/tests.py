import unittest
from collections import namedtuple
from unittest.mock import MagicMock, patch

from rndt.uuidhandler import UUIDHandler


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

        patcher = patch.object(UUIDHandler, "delete_old_metadata_links")  # needs the DB
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_return_an_uuid_if_the_instance_one_is_not_empty(self):
        self.sut.group.groupprofile.groupprofilerndt.pa.ipa = "ipa"
        self.sut.uuid = "ipa:123abc456"
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("ipa:123abc456", actual)

    @patch("uuid.uuid1")
    def test_return_the_instance_uuid_with_the_ipa_code_if_the_uuid_is_not_present(self, mocked_uuid):
        mocked_uuid.return_value = "123abc456"
        self.sut.uuid = ""
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("c_123:123abc456", actual)

    @patch("uuid.uuid1")
    def test_return_the_instance_uuid_if_the_uuid_and_ipa_are_not_present(self, mocked_uuid):
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
        actual = UUIDHandler(self.sut).extract_ipa_from_uuid(self.sut.uuid)
        self.assertEqual("c_123", actual)

    def test_uuidhandler_should_extract_the_correct_uuid_code_if_exists(self):
        self.sut.uuid = "c_123:uuid"
        actual = UUIDHandler(self.sut).extract_uuid(self.sut.uuid)
        self.assertEqual("uuid", actual)

    def test_uuidhandler_should_extract_none_ipa_code_if_not_exists(self):
        self.sut.uuid = "d1fbf97f-e44a-4c60-87e2-56dc"
        actual = UUIDHandler(self.sut).extract_ipa_from_uuid(self.sut.uuid)
        self.assertFalse(actual)

    def test_uuidhandler_update_the_ipa_code_if_is_changed(self):
        self.sut.uuid = "c123:abcdef"
        self.sut.group.groupprofile.groupprofilerndt.pa.ipa = "c_345"
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("c_345:abcdef", actual)

    def test_uuidhandler_does_not_mistake_a_longer_ipa_for_the_group_one(self):
        self.sut.uuid = "c_a12:abcdef"
        self.sut.group.groupprofile.groupprofilerndt.pa.ipa = "c_a1"
        actual = UUIDHandler(self.sut).create_uuid()
        self.assertEqual("c_a1:abcdef", actual)

    def test_replace_uuid_only_replaces_the_prefix(self):
        self.assertEqual("c_9:c_1abc", UUIDHandler.replace_uuid("c_9", "c_1", "c_1:c_1abc"))
        self.assertEqual("c_12:abc", UUIDHandler.replace_uuid("c_9", "c_1", "c_12:abc"))
        self.assertEqual("x:abc", UUIDHandler.replace_uuid("x", "c.1", "c.1:abc"))

    def test_uuid_for_ipa_has_no_side_effects(self):
        self.sut.uuid = "c_1:abc"
        self.assertEqual("c_9:abc", UUIDHandler(self.sut).uuid_for_ipa("c_9"))
        UUIDHandler.delete_old_metadata_links.assert_not_called()

    def test_uuid_for_ipa_creates_a_missing_uuid(self):
        self.sut.uuid = None
        self.assertRegex(UUIDHandler(self.sut).uuid_for_ipa("c_9"), r"^c_9:[0-9a-f-]{32}$")


class PaChangeTestCase(unittest.TestCase):
    """UUIDs are updated when a group gets a PA, or the iPA of a PA changes"""

    def setUp(self):
        patcher = patch.object(UUIDHandler, "delete_old_metadata_links")  # needs the DB
        self.delete_links = patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def _resource(id, uuid):
        return MagicMock(id=id, uuid=uuid)

    def _run(self, receiver, resources, current_ipa, previous_ipa, raw=False):
        from rndt import models

        instance = MagicMock(ipa_has_changed=True, _rb_to_update=(current_ipa, previous_ipa))
        with patch.object(models, "Dataset") as dataset:
            dataset.objects.filter.return_value = resources
            receiver(sender=None, instance=instance, raw=raw)
        return dataset.objects.filter

    def test_first_pa_of_a_group_prefixes_its_datasets(self):
        from rndt.models import _group_post_save

        plain, other, same = self._resource(1, "abc"), self._resource(2, "c_1:def"), self._resource(3, "c_9:ghi")
        self._run(_group_post_save, [plain, other, same], "c_9", None)
        self.assertEqual(["c_9:abc", "c_9:def", "c_9:ghi"], [plain.uuid, other.uuid, same.uuid])
        plain.save.assert_called_once()
        other.save.assert_called_once()
        same.save.assert_not_called()
        self.assertEqual(2, self.delete_links.call_count)

    def test_ipa_change_updates_the_pa_datasets(self):
        from rndt.models import _pa_post_save

        resource = self._resource(1, "c_1:abc")
        dataset_filter = self._run(_pa_post_save, [resource], "c_9", "c_1")
        dataset_filter.assert_called_once_with(uuid__startswith="c_1:")
        self.assertEqual("c_9:abc", resource.uuid)

    def test_fixture_loading_is_ignored(self):
        from rndt.models import _group_post_save, _pa_post_save

        for receiver in (_group_post_save, _pa_post_save):
            self._run(receiver, [], "c_9", "c_1", raw=True).assert_not_called()


class UuidsCommandTestCase(unittest.TestCase):
    """rndt_uuids check/fix: the datasets of a group with a PA get the iPA prefix"""

    def setUp(self):
        patcher = patch.object(UUIDHandler, "delete_old_metadata_links")  # needs the DB
        patcher.start()
        self.addCleanup(patcher.stop)
        self.plain = MagicMock(id=1, uuid="abc", title="Rivers")
        self.other = MagicMock(id=2, uuid="c_1:def")
        self.ok = MagicMock(id=3, uuid="c_9:ghi")
        self.missing = MagicMock(id=4, uuid="", title="No uuid")

    def _call(self, action, *datasets, known=()):
        """Run the command: (log output, CommandError or None); known: the (id, uuid) of the selected datasets"""
        from django.core.management import CommandError, call_command

        from rndt.management.commands import rndt_uuids

        group_rndt = MagicMock()
        group_rndt.pa.ipa = "c_9"
        group_rndt.group_profile.group_id = 42
        with (
            patch.object(rndt_uuids, "GroupProfileRNDT") as model,
            patch.object(rndt_uuids, "Dataset") as dataset,
        ):
            model.objects.select_related.return_value = [group_rndt]
            queryset = dataset.objects.all.return_value
            queryset.values_list.return_value = list(known)
            queryset.filter.side_effect = lambda *q, **kw: (
                [self.plain, self.other, self.ok, self.missing] if kw else queryset
            )
            error = None
            with self.assertLogs(rndt_uuids.logger) as logs:
                try:
                    call_command("rndt_uuids", action, *datasets)
                except CommandError as e:
                    error = e
            queryset.filter.assert_called_with(group_id=42)
            self.selection = [c.args[0] for c in queryset.filter.call_args_list if c.args]
        return "\n".join(logs.output), error

    def test_check_reports_the_mismatches_without_saving(self):
        out, error = self._call("check")
        self.assertIn("Dataset 1 'Rivers': abc -> c_9:abc", out)
        self.assertRegex(out, r"Dataset 4 'No uuid':  -> c_9:")
        self.assertIn("3 dataset uuids without their group iPA prefix", out)
        self.assertIsNotNone(error)  # non-zero exit status
        self.assertEqual(("abc", "c_1:def", ""), (self.plain.uuid, self.other.uuid, self.missing.uuid))
        for dataset in (self.plain, self.other, self.ok, self.missing):
            dataset.save.assert_not_called()

    def test_check_passes_when_all_uuids_are_prefixed(self):
        self.plain.uuid, self.other.uuid, self.missing.uuid = "c_9:abc", "c_9:def", "c_9:jkl"
        out, error = self._call("check")
        self.assertIn("0 dataset uuids without their group iPA prefix", out)
        self.assertIsNone(error)

    def test_fix_prefixes_the_mismatching_uuids(self):
        out, error = self._call("fix")
        self.assertIsNone(error)
        self.assertIn("Dataset 1 'Rivers': abc -> c_9:abc", out)
        self.assertIn("3 dataset uuids fixed", out)
        self.assertEqual(["c_9:abc", "c_9:def", "c_9:ghi"], [d.uuid for d in (self.plain, self.other, self.ok)])
        self.assertRegex(self.missing.uuid, r"^c_9:[0-9a-f-]{32}$")
        for dataset in (self.plain, self.other, self.missing):
            dataset.save.assert_called_once()
        self.ok.save.assert_not_called()

    def test_all_datasets_by_default(self):
        self._call("check")
        self.assertEqual([], self.selection)

    def test_selected_datasets_by_id_or_uuid(self):
        from django.db.models import Q

        out, _ = self._call("fix", "1", "c_1:def", "99", known=[(1, "abc"), (2, "c_1:def")])
        self.assertEqual([Q(id__in={1, 99}) | Q(uuid__in={"c_1:def"})], self.selection)
        self.assertIn("Dataset not found: 99", out)
        self.assertNotIn("not found: 1", out)


ISO_HEAD = """<gmd:MD_Metadata xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gco="http://www.isotc211.org/2005/gco"
 xmlns:gmx="http://www.isotc211.org/2005/gmx" xmlns:xlink="http://www.w3.org/1999/xlink">"""


def iso(identification="", quality=""):
    return f"""{ISO_HEAD}
 <gmd:identificationInfo><gmd:MD_DataIdentification>{identification}</gmd:MD_DataIdentification></gmd:identificationInfo>
 <gmd:dataQualityInfo><gmd:DQ_DataQuality>{quality}</gmd:DQ_DataQuality></gmd:dataQualityInfo>
</gmd:MD_Metadata>"""


def constraint(kind, code, other=""):
    return f"""<gmd:resourceConstraints><gmd:MD_LegalConstraints>
 <gmd:{kind}><gmd:MD_RestrictionCode codeListValue="{code}"/></gmd:{kind}>{other}
</gmd:MD_LegalConstraints></gmd:resourceConstraints>"""


def resolution(value):
    return f"""<gmd:spatialResolution><gmd:MD_Resolution><gmd:distance>
 <gco:Distance uom="m">{value}</gco:Distance></gmd:distance></gmd:MD_Resolution></gmd:spatialResolution>"""


class RNDTParserTestCase(unittest.TestCase):
    def setUp(self):
        from rndt.metadata import parser

        # no DB: no thesaurus is known
        for model in ("ThesaurusKeyword", "Thesaurus"):
            patcher = patch.object(parser, model)
            patcher.start().objects.filter.return_value.filter.return_value.first.return_value = None
            self.addCleanup(patcher.stop)
        self.parser = parser

    def test_defaults_are_not_shared_between_calls(self):
        first = self.parser.rndt_parser(iso(resolution("10")))
        second = self.parser.rndt_parser(iso())
        self.assertEqual(10.0, first[4]["jsoninstance"]["rndt_resolution"])
        self.assertNotIn("rndt_resolution", second[4]["jsoninstance"])

    def test_passed_custom_is_not_edited_in_place(self):
        custom = {"jsoninstance": {"other": 1}}
        ret = self.parser.rndt_parser(iso(resolution("10")), custom=custom)
        self.assertEqual({"jsoninstance": {"other": 1}}, custom)
        self.assertEqual({"other": 1, "rndt_resolution": 10.0}, ret[4]["jsoninstance"])

    def test_constraint_without_other_constraints_is_skipped(self):
        xml = iso(constraint("accessConstraints", "copyright"))
        ret = self.parser.RNDTMetadataParser(self.parser.dlxml.fromstring(xml.encode())).parse_constraints()
        self.assertEqual([], ret)

    def test_freetext_constraint(self):
        other = "<gmd:otherConstraints><gco:CharacterString>free use</gco:CharacterString></gmd:otherConstraints>"
        ret = self.parser.rndt_parser(iso(constraint("useConstraints", "otherRestrictions", other)))
        self.assertEqual(
            {"inspire_url": False, "freetext": "free use"},
            ret[4]["jsoninstance"]["rndt_ConditionsApplyingToAccessAndUse"],
        )

    def test_unparsable_numbers_are_ignored(self):
        for value in ("10 m", "", "abc"):
            with self.subTest(value=value):
                ret = self.parser.rndt_parser(iso(resolution(value)))
                self.assertNotIn("rndt_resolution", ret[4]["jsoninstance"])

    def test_anchor_keyword_without_thesaurus(self):
        kw = """<gmd:descriptiveKeywords><gmd:MD_Keywords><gmd:keyword>
 <gmx:Anchor xlink:href="http://example.org/k1">k1</gmx:Anchor></gmd:keyword>
 </gmd:MD_Keywords></gmd:descriptiveKeywords>"""
        self.parser.ThesaurusKeyword.objects.filter.return_value.exists.return_value = True
        self.parser.ThesaurusKeyword.objects.filter.return_value.first.return_value.alt_label = "k1"
        _, _, _, keywords, _ = self.parser.rndt_parser(iso(kw))
        self.assertEqual(1, len(keywords))
        self.assertIsNone(keywords[0]["thesaurus"]["title"])

    def test_discarded_keywords_are_collected_from_all_blocks(self):
        def block(n):
            return f"""<gmd:descriptiveKeywords><gmd:MD_Keywords><gmd:keyword>
 <gmx:Anchor xlink:href="http://example.org/{n}">{n}</gmx:Anchor></gmd:keyword>
 <gmd:thesaurusName><gmd:CI_Citation><gmd:title><gco:CharacterString>T{n}</gco:CharacterString></gmd:title>
 </gmd:CI_Citation></gmd:thesaurusName></gmd:MD_Keywords></gmd:descriptiveKeywords>"""

        self.parser.ThesaurusKeyword.objects.filter.return_value.exists.return_value = False
        _, _, _, _, custom = self.parser.rndt_parser(iso(block("a") + block("b")))
        self.assertEqual(["a", "b"], custom["rejected_keywords"])


class RNDTSchemaHandlerTestCase(unittest.TestCase):
    def setUp(self):
        from rndt.metadata.handler import RNDTSchemaHandler

        self.handler = RNDTSchemaHandler()
        self.handler.otherRestrictions = "otherRestrictions"  # skip the DB lookup

    def _pre_save(self, conditions):
        resource = namedtuple("Resource", ("constraints_other", "restriction_code_type"))
        context = {}
        self.handler.pre_save(resource, {"rndt_ConditionsApplyingToAccessAndUse": conditions}, context, {})
        return context["base"]["constraints_other"]

    def test_constraints_other_from_url(self):
        self.assertEqual("http://u", self._pre_save({"inspire_url": True, "url": "http://u", "freetext": "x"}))

    def test_constraints_other_from_freetext(self):
        self.assertEqual("free", self._pre_save({"inspire_url": False, "freetext": "free"}))

    def test_constraints_other_missing(self):
        self.assertEqual("Missing value", self._pre_save(None))

    def test_update_schema(self):
        schema = {
            "properties": {
                "data_quality_statement": {"type": ["string", "null"]},
                "constraints_other": {},
                "restriction_code_type": {},
            }
        }
        props = self.handler.update_schema(schema, {})["properties"]
        self.assertEqual(["data_quality_statement"], list(props))
        self.assertEqual("string", props["data_quality_statement"]["type"])
        self.assertTrue(props["data_quality_statement"]["geonode:required"])


class CswFilterTestCase(unittest.TestCase):
    def test_pa_filter_matches_the_whole_ipa(self):
        from rndt.catalogue.views import LayerFilters

        qs = MagicMock()
        self.assertIs(qs.filter.return_value, LayerFilters("c_a1").filter_layers(qs))
        qs.filter.assert_called_once_with(uuid__startswith="c_a1:")


class FakeResources(list):
    """The QuerySet.filter lookup used by the PA CSW filter, on a plain list"""

    def filter(self, uuid__startswith):
        return FakeResources(r for r in self if r.uuid.startswith(uuid__startswith))


class CswUrlsTestCase(unittest.TestCase):
    """Requests go through the URLconf to the view, down to the args passed to GeoNode's CSW dispatch"""

    def _dispatch(self, path):
        from django.test import RequestFactory
        from django.urls import resolve

        from rndt.catalogue import views

        match = resolve(path)
        with patch.object(views, "csw_global_dispatch") as dispatch:
            match.func(RequestFactory().get(path, {"request": "GetRecords"}), *match.args, **match.kwargs)
        return match, dispatch.call_args.kwargs

    def test_pa_endpoint_only_returns_the_pa_resources(self):
        match, kwargs = self._dispatch("/catalogue/csw/c_a1")
        self.assertEqual("rndt_csw_dispatcher", match.url_name)

        resource = namedtuple("Resource", ("uuid",))
        resources = FakeResources(resource(uuid) for uuid in ("c_a1:1", "c_a1:2", "c_a12:3", "c_b2:4", "5"))
        self.assertEqual(["c_a1:1", "c_a1:2"], [r.uuid for r in kwargs["dataset_filter"](resources)])

        config = kwargs["config_updater"]({"server": {"url": "http://localhost/catalogue/csw"}})
        self.assertEqual("http://localhost/catalogue/csw/c_a1", config["server"]["url"])

    def test_global_endpoint_is_geonode_one(self):
        from django.urls import resolve
        from geonode.catalogue.views import csw_global_dispatch

        self.assertIs(csw_global_dispatch, resolve("/catalogue/csw").func)

    def test_pa_endpoint_url(self):
        from django.urls import reverse

        self.assertEqual("/catalogue/csw/c_a1", reverse("rndt_csw_dispatcher", kwargs={"pa_code": "c_a1"}))


class UrlsTestCase(unittest.TestCase):
    @staticmethod
    def _urlconf(with_rndt):
        """A URLconf with the GeoNode urls, followed by rndt.urls if with_rndt"""
        import types

        from django.urls import include, re_path
        from geonode.urls import urlpatterns as geonode_urlpatterns

        from rndt.apps import is_rndt_urls

        patterns = [p for p in geonode_urlpatterns if not is_rndt_urls(p)]
        if with_rndt:
            patterns.append(re_path(r"", include("rndt.urls")))
        urlconf = types.ModuleType("test_urls")
        urlconf.urlpatterns = patterns
        return urlconf

    def _check(self, with_rndt):
        from django.test import override_settings

        from rndt.checks import check_rndt_urls

        with override_settings(ROOT_URLCONF=self._urlconf(with_rndt)):
            return check_rndt_urls(None)

    def test_rndt_urls_are_injected_once(self):
        from geonode.urls import urlpatterns

        from rndt.apps import inject_urls, is_rndt_urls

        inject_urls()  # already run by ready(): must not add them twice
        self.assertEqual(1, sum(is_rndt_urls(p) for p in urlpatterns))

    def test_no_warning_when_rndt_urls_are_included(self):
        from rndt.checks import check_rndt_urls

        self.assertEqual([], check_rndt_urls(None))
        self.assertEqual([], self._check(True))

    def test_warns_when_rndt_urls_are_missing(self):
        self.assertEqual(["rndt.W001"], [w.id for w in self._check(False)])


class TemplatesTestCase(unittest.TestCase):
    def test_rndt_metadata_template_compiles(self):
        from django.template.loader import get_template

        # fails on unknown tag libraries or filters
        get_template("xml/template-rndt.xml")
