import ast
import logging

from defusedxml import ElementTree as dlxml

# Geonode functionality
from geonode import GeoNodeException
from geonode.base.models import Thesaurus, ThesaurusKeyword
from geonode.layers.metadata import convert_keyword, get_tagname
from owslib import util
from owslib.iso import get_namespaces

logger = logging.getLogger(__name__)


def rndt_parser(xml, uuid="", vals={}, regions=[], keywords=[], custom={}):
    # check if document is XML
    try:
        exml = dlxml.fromstring(xml.encode())
    except Exception as err:
        raise GeoNodeException(f"Uploaded XML document is not XML: {str(err)}")

    # check if document is an accepted XML metadata format
    if get_tagname(exml) == "GetRecordByIdResponse":  # strip CSW element
        exml = list(exml)[0]

    rndt_parser = RNDTMetadataParser(exml)
    rndt_parser.get_freq(vals)
    keywords, discarded = rndt_parser.resolve_keywords()
    custom["rejected_keywords"] = discarded

    # Next calls parse and store metadata in a jsonschema compliant way (geonode5)
    jsoninstance = custom.setdefault("jsoninstance", {})
    resolver = RNDTMetadataResolver(jsoninstance)
    resolver.resolve_constraints(rndt_parser.parse_constraints())
    resolver.resolve_resolution(rndt_parser.parse_resolution())
    resolver.resolve_accuracy(rndt_parser.parse_accuracy())

    return uuid, vals, regions, keywords, custom


class RNDTMetadataResolver:
    def __init__(self, jsoninstance:dict):
        self.jsoninstance = jsoninstance

    def resolve_constraints(self, constraints:list):
        freetext = ""
        access = None
        use = None

        for constr in constraints:
            logger.debug(f"Resolving constraint: --> {constr}")

            code = constr["code"]
            if code not in ("otherRestrictions", "limitation not listed"):
                logger.debug(f"Skipping constraint {constr}")
                continue

            href = constr["href"]
            text = constr["text"]

            if not href:
                logger.debug(f"Collecting text from {constr}")
                freetext = f"{freetext}\n{text} "
                continue

            # rndt_LimitationsOnPublicAccess -> url
            # rndt_ConditionsApplyingToAccessAndUse -> text or url

            t = ThesaurusKeyword.objects.filter(about=href).filter(
                thesaurus__identifier="LimitationsOnPublicAccess"
            ).first()
            if t:
                if access:
                    logger.warning(f"Duplicate LimitationsOnPublicAccess overridden {access}")
                access = {"id":href, "label":t.alt_label}
                continue

            t = ThesaurusKeyword.objects.filter(about=href).filter(
                thesaurus__identifier="ConditionsApplyingToAccessAndUse"
            ).first()
            if t:
                if use:
                    logger.warning(f"Duplicate ConditionsApplyingToAccessAndUse overridden {use}")
                use = {"inspire_url": True, "url": href}
                continue

            logger.warning(f"Skipping unknown URL {constr}")
            # we may try and parse license URLs: that's beyond RNDT requirements, but it would be nice
        #endfor

        if access:
            self.jsoninstance["rndt_LimitationsOnPublicAccess"] = access
        else:
            logger.info("LimitationsOnPublicAccess not found")

        if use:
            self.jsoninstance["rndt_ConditionsApplyingToAccessAndUse"] = use
            if freetext:
                logger.warning(f"Ignoring freetext constraint [{freetext}]")
        else:
            if freetext:
                self.jsoninstance["rndt_ConditionsApplyingToAccessAndUse"] = {
                    "inspire_url": False, "freetext": freetext
                }
            else:
                logger.info("ConditionsApplyingToAccessAndUse not found")

    def resolve_resolution(self, val):
        if val is not None:
            self.jsoninstance["rndt_resolution"] = val

    def resolve_accuracy(self, val):
        if val is not None:
            self.jsoninstance["rndt_accuracy"] = val


class RNDTMetadataParser:
    """
    A metadata parser compliant with the RNDT specification
    """

    def __init__(self, exml):
        self.exml = exml
        self.namespaces = get_namespaces()
        self.mdkws = exml.findall(
            util.nspath_eval(
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords",
                self.namespaces,
            )
        )

    def parse_codelist(self, xpath):
        """ This should be moved into the base parser """
        elem = self.exml.find(util.nspath_eval(xpath, self.namespaces,))
        return (elem.attrib.get("codeListValue", None), elem.text) if elem is not None else None

    def parse_constraints(self) -> list:
        """
        Function responsible to parse the access constraints elements
        - returns a list of dict:
           - code: restriction codeListValue
           - href: if gmx:Anchor in gmd:otherConstraints, its href
           - text: text content of gmd:otherConstraints, either if CharacterString or Anchor
        """
        access_constraints = self.exml.findall(
            util.nspath_eval(
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints",
                self.namespaces,
            )
        )
        ret = []
        for node in access_constraints:
            constr = {}
            logger.debug(f"Parsing constraint: --> {node}")

            md_restriction_code = node.find(
                util.nspath_eval("gmd:accessConstraints/gmd:MD_RestrictionCode", self.namespaces)
            )
            if md_restriction_code is not None:
                constr["type"] = "accessConstraints"
            else:
                md_restriction_code = node.find(
                    util.nspath_eval("gmd:useConstraints/gmd:MD_RestrictionCode", self.namespaces)
                )
                if md_restriction_code is not None:
                    constr["type"] = "useConstraints"
                else:
                    logger.warning("Missing known restrictioncode")
                    continue

            constr["code"] = md_restriction_code.attrib.get("codeListValue", "")

            anchor = node.find(util.nspath_eval("gmd:otherConstraints/gmx:Anchor", self.namespaces))
            if anchor is not None:
                constr["href"] = anchor.attrib.get("{http://www.w3.org/1999/xlink}href")
                constr["text"] = anchor.text
            else:
                charstring = node.find(
                        util.nspath_eval("gmd:otherConstraints/gco:CharacterString", self.namespaces)
                    ).text
                constr["href"] = None
                constr["text"] = charstring

            ret.append(constr)

        return ret

    def parse_resolution(self, default=None):
        resolution = self.exml.find(
            util.nspath_eval(
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance",
                self.namespaces,
            )
        )

        if resolution is None:
            logger.info(f"Resolution not found")
            return default
        if isinstance(resolution, (float, int)):
            return resolution

        try:
            res = ast.literal_eval(resolution.text)
            if isinstance(res, (float, int)):
                return res
        except ValueError as e:
            logger.warning(f"Error parsing resolution '{resolution.text}': {e}")
            return default

        logger.warning(f"Resolution cannot be parsed: [{resolution}]")
        return default

    def parse_accuracy(self, default=None):
        acc = self.exml.find(
            util.nspath_eval(
                "gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_AbsoluteExternalPositionalAccuracy/gmd:result/gmd:DQ_QuantitativeResult/gmd:value/gco:Record/gco:Real",
                self.namespaces,
            )
        )

        if acc is None:
            logger.info(f"Accuracy not found")
            return default
        if isinstance(acc, (float, int)):
            return float(acc)

        try:
            eval_acc = ast.literal_eval(acc.text)
            if isinstance(eval_acc, (float, int)):
                return float(eval_acc)
        except ValueError as e:
            logger.warning(f"Error parsing resolution '{acc.text}': {e}")
            return default

        logger.warning(f"Accuracy cannot be parsed: [{acc}]")
        return default


    def resolve_keywords(self):
        """
        Function to resolve keywords.
        By xpaths will resove which keywords will used converted for the keyword Handler object
        """
        k_not_found = []
        keywords = []
        discarded = []
        for mdkw in self.mdkws:
            tkeys = mdkw.findall(util.nspath_eval("gmd:keyword/gmx:Anchor", self.namespaces))
            keys = mdkw.findall(util.nspath_eval("gmd:keyword/gco:CharacterString", self.namespaces))
            all_keys = tkeys + keys
            if len(all_keys) > 0:
                theme = util.testXMLValue(
                    mdkw.find(util.nspath_eval("gmd:type/gmd:MD_KeywordTypeCode", self.namespaces))
                )

                thesaurus_info = mdkw.find(util.nspath_eval("gmd:thesaurusName/gmd:CI_Citation", self.namespaces))
                k_available, k_not_found, discarded = self._get_keywords(all_keys, thesaurus_info)

                if len(k_not_found) > 0:
                    keywords.extend(convert_keyword(k_not_found, theme=theme))

                if len(k_available) > 0:
                    date = util.testXMLValue(
                        thesaurus_info.find(
                            util.nspath_eval(
                                "gmd:date/gmd:CI_Date/gmd:date/gco:Date",
                                self.namespaces,
                            )
                        )
                    )

                    dateType = util.testXMLValue(
                        thesaurus_info.find(
                            util.nspath_eval(
                                "gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode",
                                self.namespaces,
                            )
                        )
                    )
                    keywords.append(
                        {
                            "keywords": k_available,
                            "thesaurus": {
                                "date": date,
                                "datetype": dateType,
                                "title": self._get_thesaurus_title(thesaurus_info),
                            },
                            "type": theme,
                        }
                    )
        return keywords, discarded

    def _get_thesaurus_title(self, thesaurus_info):
        """
        Will get gather Thesauro title.
        """

        raw_url = thesaurus_info.find(util.nspath_eval("gmd:title/gmx:Anchor", self.namespaces))
        evaluator = "gmd:title/gco:CharacterString"
        if raw_url is not None:
            url = raw_url.attrib.get("{http://www.w3.org/1999/xlink}href", None)
            if url is not None:
                evaluator = "gmd:title/gmx:Anchor"
                t = Thesaurus.objects.filter(about=url)
                if t.exists():
                    # first used in case of multiple thesaurus with the same url
                    return t.first().title
        return util.testXMLValue(thesaurus_info.find(util.nspath_eval(evaluator, self.namespaces)))

    @staticmethod
    def _get_keywords(keywords, thesaurus_info):
        """
        Will decide if a keywords should be mapped as thesaurus keyword or not:
         - not_tkey = will contains the keywords without thesaurus information
         - available = will contains the keyword with thesaurus information available in the system
         - discarded = will contains the keyword with thesaurus information not available in the system
        """
        not_tkey = []
        available = []
        discarded = []
        for keyword in keywords:
            text = util.testXMLValue(keyword)
            url = keyword.attrib.get("{http://www.w3.org/1999/xlink}href", None)
            if url is not None:
                k = ThesaurusKeyword.objects.filter(about=url)
                if k.exists():
                    available.append(k.first().alt_label)
                else:
                    discarded.append(text)
            elif thesaurus_info:
                available.append(text)
            else:
                not_tkey.append(text)
        return available, not_tkey, discarded

    def parse_frequency(self):
        """ This should be moved into the base parser """
        return self.parse_codelist("gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceMaintenance/gmd:MD_MaintenanceInformation/gmd:maintenanceAndUpdateFrequency/gmd:MD_MaintenanceFrequencyCode")

    def get_freq(self, vals):
        freq = self.parse_frequency()
        code = freq[0] if freq else None
        if freq is None:
            logger.info(f"Frequency not found")
        vals["maintenance_frequency"] = code or "unknown"
