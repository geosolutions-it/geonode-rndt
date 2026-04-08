# geonode-rndt

Geonode-RNDT is a Django App to let GeoNode be able to expose the metadata compliant to the RNDT standard

![image](https://user-images.githubusercontent.com/717359/107668977-91f8ee00-6c91-11eb-8006-80e988dddeef.png)

Detailed information on the definition of RNDT are available at this [link](https://geodati.gov.it/geoportale/)

-----

## Configuration

1. Install the application as requirement:

       pip install -e git+https://github.com/geosolutions-it/geonode-rndt@master#egg=rndt

1. Add "rndt" to your `INSTALLED_APPS setting` like this::

       INSTALLED_APPS = [
          'rndt',
          ...
       ]
   
   If you have a `local_setting` file, you may want to add the `rndt` app with these lines:
   
       INSTALLED_APPS += ('rndt',)


1. Run ``python manage.py migrate`` to migrate pre-5.0 RNDT models into SparseFields.  
   If you are installing this app for the first time in GeoNode >= 5.0, you can skip the real migrations
   and apply fake migrations with the following command:

       python manage.py migrate --fake rndt

1. To enable the `UUIDHandler`, add the following line in the `geonode.settings.py` file:

       LAYER_UUID_HANDLER = "rndt.uuidhandler.UUIDHandler"

1. To customize the metadata document to be RNDT compliant, use the rndt template:  

       CATALOG_METADATA_TEMPLATE = 'xml/template-rndt.xml'

1. To customize the XSL transformation to be aligned to the RNDT metadata format, use the provided XSL file:

       CATALOG_METADATA_XSL = '/static/rndt/rndt-metadata.xsl'

1. Load thesauri
Load the needed thesauri, either from the Thesaurus admin page or using the [`thesaurus load` command](https://docs.geonode.org/en/5.0.x/admin/thesaurus/index.html#importing-a-thesaurus-thesaurus-load).  
You can find them in the [`rndt/thesauri/`](https://github.com/geosolutions-it/geonode-rndt/tree/main/rndt/thesauri) directory.
- INSPIRE/RNDT thesauri 
  - `3-2-4-1_gemet-inspire-themes.rdf`
  - `3-2-4-2_PriorityDataset.rdf`
  - `3-2-4-3_SpatialScope.rdf`
  - `3-2-4-5_rndt-all1-fixed.rdf` ("Registro dei dati di interesse generale per il RNDT")
  - `4-1-2-1_SpatialDataServiceCategory_RNDT-fixed.rdf`
- Codelists for INSPIRE/RNDT metadata fields:
  - `ConditionsApplyingToAccessAndUse.rdf`
  - `LimitationsOnPublicAccess.rdf`
- Localization entries for the RNDT custom metadata fields:
  - `labels-i18n.rndt.rdf` 

## Uninstalling

To uninstall the app, remove all the `rndt` functionalities (`INSTALLED_APPS` and `context_processors`) from  `settings.py` and restart the server. 
If needed made an hard refresh to let the browser reload the js/css/html files (windows: CTRL+ SHIFT+R | Mac: CMD+SHIFT+R)
