import ast
import logging

from defusedxml import ElementTree as dlxml
# Geonode functionality
from geonode import GeoNodeException
from geonode.base.models import Thesaurus, ThesaurusKeyword
from geonode.layers.metadata import convert_keyword, get_tagname
from owslib import util
from owslib.iso import get_namespaces

ACCESS_CONSTRAINTS_URL = "http://inspire.ec.europa.eu/metadata-codelist/LimitationsOnPublicAccess/noLimitations"


def rndt_parser(xml, uuid="", vals={}, regions=[], keywords=[], custom={}):
    # check if document is XML
    try:
        exml = dlxml.fromstring(xml.encode())
    except Exception as err:
        raise GeoNodeException(f"Uploaded XML document is not XML: {str(err)}")

    # check if document is an accepted XML metadata format
    tagname = get_tagname(exml)
    if tagname == "GetRecordByIdResponse":  # strip CSW element
        try:
            exml = exml.getchildren()[0]
        except:
            exml = list(exml)[0]
        tagname = get_tagname(exml)

    rndt_parser = RNDTMetadataParser(exml)

    keywords, discarded = rndt_parser.resolve_keywords()
    custom["rejected_keywords"] = discarded

    custom['rndt'] = {}

    use_constr = rndt_parser.get_access_costraints(custom)
    rndt_parser.get_use_costraints(vals, use_constr)
    rndt_parser.get_resolutions(custom)
    rndt_parser.get_accuracy(custom)

    return uuid, vals, regions, keywords, custom


class RNDTMetadataParser:
    """
    RNDTParser, parser complain for parse the RNDT specification
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

    def get_access_costraints(self, custom):
        '''
        Function responsible to get the access constraints complained with RNDT
        - will take all the instances of LegalConstraints
          - if the restriction MD_RestrictionCode under accessConstraints has a codeListValue = otherRestrictions
            - If is an anchor item, 
                - will put in the vals dictionary under constraints_other the thesaurus label if exists
                - otherwise will put in contraints_other the URL parsed
            - if is a charstring:
                - will save the value extracted in a variable since is required for get the use_constrains
        '''
        use_constrs = ""
        access_constraints = self.exml.findall(
            util.nspath_eval(
                'gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints',
                self.namespaces,
            )
        )
        for item in access_constraints:
            md_restriction_code = item.find(util.nspath_eval("gmd:accessConstraints/gmd:MD_RestrictionCode", self.namespaces))
            if md_restriction_code is not None and md_restriction_code.attrib.get('codeListValue', '') == 'otherRestrictions':
                acc_constr = item.find(util.nspath_eval("gmd:otherConstraints/gmx:Anchor", self.namespaces))
                if acc_constr is not None:
                    url = acc_constr.attrib.get('{http://www.w3.org/1999/xlink}href')
                    t = ThesaurusKeyword.objects.filter(about=url).filter(thesaurus__identifier='LimitationsOnPublicAccess')
                    if t.exists():
                        custom['rndt'] = {'constraints_other': url}
                    else:
                        custom['rndt'] = {'constraints_other': ACCESS_CONSTRAINTS_URL}
                else:
                    use_constrs = item.find(util.nspath_eval("gmd:otherConstraints/gco:CharacterString", self.namespaces)).text
        return use_constrs


    def get_use_costraints(self, vals, acc_constr):        
        '''
        Function responsible to get the use constraints complained with RNDT
        - will take all the instances of LegalConstraints
          - if the restriction MD_RestrictionCode under useConstraints has a codeListValue = otherRestrictions
            - If is an anchor item, 
                - will put in the custom dictionary under rndt the thesaurus label if exists
                - otherwise will put in custom[rndt] the text and the information extracted in the previous step
            - if is a charstring:
                - will put in custom[rndt] the text and the information extracted in the previous step
        '''
        use_constraints = self.exml.findall(
            util.nspath_eval(
                'gmd:identificationInfo/gmd:MD_DataIdentification/gmd:resourceConstraints/gmd:MD_LegalConstraints',
                self.namespaces,
            )
        )
        for item in use_constraints:
            md_restriction_code = item.find(util.nspath_eval("gmd:useConstraints/gmd:MD_RestrictionCode", self.namespaces))
            if md_restriction_code is not None and md_restriction_code.attrib.get('codeListValue', '') == 'otherRestrictions':
                use_constr = item.find(util.nspath_eval("gmd:otherConstraints/gmx:Anchor", self.namespaces))
                if use_constr is not None:
                    url = use_constr.attrib.get('{http://www.w3.org/1999/xlink}href')
                    t = ThesaurusKeyword.objects\
                        .filter(about=url)\
                        .filter(thesaurus__identifier='ConditionsApplyingToAccessAndUse')
                    if t.exists():
                        vals['constraints_other'] = url
                    else:
                        vals['constraints_other'] = f"{use_constr.text} {acc_constr}"
                else:
                    use_constr = item.find(util.nspath_eval("gmd:otherConstraints/gco:CharacterString", self.namespaces))
                    if use_constr is not None:
                        vals['constraints_other'] = f"{use_constr.text} {acc_constr}"
                    else:
                        vals['constraints_other'] = acc_constr
        return vals

    def get_resolutions(self, custom):
        resolution = self.exml.find(
            util.nspath_eval(
                'gmd:identificationInfo/gmd:MD_DataIdentification/gmd:spatialResolution/gmd:MD_Resolution/gmd:distance/gco:Distance',
                self.namespaces,
            )
        )
        
        if resolution is not None:
            custom['rndt']['resolution'] = (resolution if isinstance(resolution, float) else ast.literal_eval(resolution.text)) or 0
        else:
            logging.error("Resolution cannot be None, using default value 0")
            custom['rndt']['resolution'] = 0
        return custom

    def get_accuracy(self, custom):
        accuracy = self.exml.find(
            util.nspath_eval(
                'gmd:dataQualityInfo/gmd:DQ_DataQuality/gmd:report/gmd:DQ_AbsoluteExternalPositionalAccuracy/gmd:result/gmd:DQ_QuantitativeResult/gmd:value/gco:Record/gco:Real',
                self.namespaces,
            )
        )
        if accuracy is not None:
            custom['rndt']['accuracy'] = (accuracy if isinstance(accuracy, float) else ast.literal_eval(accuracy.text)) or 0
        else:
            logging.error("accuracy cannot be None, using default value 0")            
            custom['rndt']['accuracy'] = 0
        return custom


    def resolve_keywords(self):
        """
        Function to resolve keywords.
        By xpaths will resove which keywords will used converted for the keyword Handler object
        """
        k_not_found = []
        keywords = []
        discarded = []
        for mdkw in self.mdkws:
            tkeys = mdkw.findall(
                util.nspath_eval("gmd:keyword/gmx:Anchor", self.namespaces)
            )
            keys = mdkw.findall(
                util.nspath_eval("gmd:keyword/gco:CharacterString", self.namespaces)
            )
            all_keys = tkeys + keys
            if len(all_keys) > 0:

                theme = util.testXMLValue(
                    mdkw.find(
                        util.nspath_eval(
                            "gmd:type/gmd:MD_KeywordTypeCode", self.namespaces
                        )
                    )
                )

                thesaurus_info = mdkw.find(
                    util.nspath_eval(
                        "gmd:thesaurusName/gmd:CI_Citation", self.namespaces
                    )
                )
                k_available, k_not_found, discarded = self._get_keywords(
                    all_keys, thesaurus_info
                )

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

        raw_url = thesaurus_info.find(
            util.nspath_eval("gmd:title/gmx:Anchor", self.namespaces)
        )
        evaluator = "gmd:title/gco:CharacterString"
        if raw_url is not None:
            url = raw_url.attrib.get('{http://www.w3.org/1999/xlink}href', None)
            if url is not None:
                evaluator = "gmd:title/gmx:Anchor"
                t = Thesaurus.objects.filter(about=url)
                if t.exists():
                    # first used in case of multiple thesaurus with the same url
                    return t.first().title
        return util.testXMLValue(
            thesaurus_info.find(util.nspath_eval(evaluator, self.namespaces))
        )

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
            url = keyword.attrib.get('{http://www.w3.org/1999/xlink}href', None)
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
