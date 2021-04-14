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

    keywords, discarded = rndt_parser.resolve_keywords()
    custom['rejected_keywords'] = discarded
    #access_costraints = rndt_parser.get_access_costraints(vals)
    # use_costraints = get_use_costraints()
    # resolutions = get_resolutions()
    # accuracy = get_accuracy()

    return uuid, vals, regions, keywords, custom


class RNDTMetadataParser:
    '''
    RNDTParser, parser complain for parse the RNDT specification
    '''
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
        '''
        Function to resolve keywords.
        By xpaths will resove which keywords will used converted for the keyword Handler object
        '''
        k_not_found = []
        keywords = []
        discarded = []
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
                    k_available, k_not_found, discarded = self._get_keywords(all_keys, thesaurus_info)

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
        return keywords, discarded

    def _get_thesaurus_title(self, thesaurus_info):
        '''
        Will get gather Thesauro title.
        '''

        url = thesaurus_info.find(
            util.nspath_eval("gmd:title/gmx:Anchor", self.namespaced)
        )

        evaluator = "gmd:title/gco:CharacterString"
        if url is not None:
            evaluator = "gmd:title/gmx:Anchor"
            t = Thesaurus.objects.filter(about=url.values()[0])
            if t.exists():
                # first used in case of multiple thesaurus with the same url
                return t.first().title
        return util.testXMLValue(
            thesaurus_info.find(
                util.nspath_eval(evaluator, self.namespaced)
            )
        )

    @staticmethod
    def _get_keywords(keywords, thesaurus_info):
        '''
        Will decide if a keywords should be mapped as thesaurus keyword or not:
         - not_tkey = will contains the keywords without thesaurus information
         - available = will contains the keyword with thesaurus information available in the system
         - discarded = will contains the keyword with thesaurus information not available in the system
        '''
        not_tkey = []
        available = []
        discarded = []
        for keyword in keywords:
            text = util.testXMLValue(keyword)
            url = keyword.values()
            if len(url) > 0:
                k = ThesaurusKeyword.objects.filter(about=url[0])
                if k.exists():
                    available.append(k.first().alt_label)
                else:
                    discarded.append(text)
            elif thesaurus_info:
                available.append(text)
            else:
                not_tkey.append(text)
        return available, not_tkey, discarded
