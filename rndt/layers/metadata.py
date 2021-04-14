from defusedxml import lxml as dlxml
# Geonode functionality
from geonode import GeoNodeException
from geonode.base.models import Thesaurus, ThesaurusKeyword
from geonode.layers.metadata import convert_keyword, get_tagname
from owslib import util
from owslib.iso import get_namespaces


def rndt_parser(xml, uuid="", vals={}, regions=[], keywords=[], custom={}):
    # check if document is XML
    try:
        exml = dlxml.fromstring(xml.encode())
    except Exception as err:
        raise GeoNodeException(f"Uploaded XML document is not XML: {str(err)}")

    # check if document is an accepted XML metadata format
    tagname = get_tagname(exml)

    if tagname == "GetRecordByIdResponse":  # strip CSW element
        exml = exml.getchildren()[0]
        tagname = get_tagname(exml)

    rndt_parser = RNDTMetadataParser(exml)

    keywords = rndt_parser.resolve_keywords(keywords)

    # keyword  = get_keyword ()
    # access_costraints = get_access_costraints()
    # use_costraints = get_use_costraints()
    # resolutions = get_resolutions()
    # accuracy = get_accuracy()

    return uuid, vals, regions, keywords, custom


class RNDTMetadataParser:
    def __init__(self, exml):
        self.exml = exml
        self.namespaced = get_namespaces()
        self.mdkws = exml.findall(
            util.nspath_eval(
                "gmd:identificationInfo/gmd:MD_DataIdentification/gmd:descriptiveKeywords/gmd:MD_Keywords",
                self.namespaced,
            )
        )

    def resolve_keywords(self, keywords):
        k_not_found = []
        for mdkw in self.mdkws:
            tkeys = mdkw.findall(
                util.nspath_eval("gmd:keyword/gmx:Anchor", self.namespaced)
            )
            if len(tkeys) > 0:
                k_available, k_not_found = self._get_keywords(tkeys)
                if len(k_not_found) > 0:
                    keywords.extend(convert_keyword(k_not_found))

                if len(k_available) > 0:
                    theme = util.testXMLValue(
                        mdkw.find(
                            util.nspath_eval(
                                "gmd:type/gmd:MD_KeywordTypeCode", self.namespaced
                            )
                        )
                    )

                    thesaurus_info = mdkw.find(
                        util.nspath_eval(
                            "gmd:thesaurusName/gmd:CI_Citation", self.namespaced
                        )
                    )

                    date = util.testXMLValue(
                        thesaurus_info.find(
                            util.nspath_eval(
                                "gmd:date/gmd:CI_Date/gmd:date/gco:Date", self.namespaced
                            )
                        )
                    )

                    dateType = util.testXMLValue(
                        thesaurus_info.find(
                            util.nspath_eval(
                                "gmd:date/gmd:CI_Date/gmd:dateType/gmd:CI_DateTypeCode",
                                self.namespaced,
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
        return keywords

    def _get_thesaurus_title(self, thesaurus_info):
        title = util.testXMLValue(
            thesaurus_info.find(
                util.nspath_eval("gmd:title/gmx:Anchor", self.namespaced)
            )
        )

        url = thesaurus_info.find(
            util.nspath_eval("gmd:title/gmx:Anchor", self.namespaced)
        ).values()[0]

        t = Thesaurus.objects.filter(about=url)

        if t.exists():
            # first used in case of multiple thesaurus with the same url
            return t.first().title
        return title

    def _get_keywords(self, keywords):
        not_found = []
        available = []
        for keyword in keywords:
            text = util.testXMLValue(keyword)
            url = keyword.values()[0]

            k = ThesaurusKeyword.objects.filter(about=url)
            if k.exists():
                available.append(k.first().alt_label)
            else:
                not_found.append(text)
        return available, not_found
