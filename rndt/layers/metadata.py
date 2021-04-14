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

    keywords = rndt_parser.resolve_keywords()

    #access_costraints = rndt_parser.get_access_costraints(vals)
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

    def resolve_keywords(self):
        k_not_found = []
        keywords = []
        for mdkw in self.mdkws:
            tkeys = mdkw.findall(
                util.nspath_eval("gmd:keyword/gmx:Anchor", self.namespaced)
            )
            keys = mdkw.findall(
                util.nspath_eval("gmd:keyword/gco:CharacterString", self.namespaced)
            )
            all_keys = tkeys + keys
            if len(all_keys) > 0:
                
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
                    k_available, k_not_found = self._get_keywords(all_keys, thesaurus_info)

                    if len(k_not_found) > 0:
                        keywords.extend(convert_keyword(k_not_found, theme=theme))

                    if len(k_available) > 0:
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

    @staticmethod
    def _get_keywords(keywords, thesaurus_info):
        not_tkey = []
        available = []
        for keyword in keywords:
            text = util.testXMLValue(keyword)
            url = keyword.values()
            if len(url) > 0:
                k = ThesaurusKeyword.objects.filter(about=url[0])
                if k.exists():
                    available.append(k.first().alt_label)
                else:
                    continue
            elif thesaurus_info:
                available.append(text)
            else:
                not_tkey.append(text)
        return available, not_tkey
