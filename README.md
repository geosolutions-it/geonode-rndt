# geonode-rndt

Geonode-RNDT is a Django App to let GeoNode be able to expose the metadata compliant to the RNDT standard

![image](https://user-images.githubusercontent.com/717359/107668977-91f8ee00-6c91-11eb-8006-80e988dddeef.png)

Detailed information on the definition of RNDT are available at this [link](https://geodati.gov.it/geoportale/)

-----

## Configuration

1. Install the application:
   - By hand in your virtual env: 
     ``` bash
        pip install -e git+https://github.com/geosolutions-it/geonode-rndt@master#egg=rndt
     ```
   - Or put it in your project requirements file.

1. Edit your `settings.py` file and add "rndt" to your `INSTALLED_APPS`, like this:

       INSTALLED_APPS += ('rndt',)

1. Run migrations

   You need to create/update the RNDT model by running
   ```
      python manage.py migrate
   ```

   In case you are running GeoNode within Docker, you need to run the `migrate` command from a shell within the container.  
   If you are running GeoNode via a GeoNode project, the migrations will be automatically run.

1. To enable the `UUIDHandler`, add the following line in the `geonode.settings.py` file:

       LAYER_UUID_HANDLER = "rndt.uuidhandler.UUIDHandler"

1. To customize the metadata document to be RNDT compliant, use the rndt template:  

       CATALOG_METADATA_TEMPLATE = 'xml/template-rndt.xml'

1. To customize the XSL transformation to be aligned to the RNDT metadata format, use the provided XSL file:

       CATALOG_METADATA_XSL = '/static/rndt/rndt-metadata.xsl'

1. Load and configure thesauri  
   Load the needed thesauri, either from the Thesaurus admin page or using the [`thesaurus load` command](https://docs.geonode.org/en/5.0.x/admin/thesaurus/index.html#importing-a-thesaurus-thesaurus-load).  
   You can find them in the [`rndt/thesauri/`](https://github.com/geosolutions-it/geonode-rndt/tree/main/rndt/thesauri) directory.

   Once loaded, [configure the thesauri](https://docs.geonode.org/en/5.0.x/admin/thesaurus/index.html#configuring-a-thesaurus):  

   - INSPIRE/RNDT thesauri  
     These thesauri are used as controlled vocabularies, so
     - the *max* cardinality should be set different than 0 (where -1 means unlimited elements)
     - *order* is the sort order they appear in the metadata editor
     - *facet* tells if the thesaurus should also appear as a dropdown filter in the resources page
   
     | File   | min | max | order | facet | Title |
     |--------|-----|-----|-------|-------|-------|
     | `3-2-4-1_gemet-inspire-themes.rdf` | 1 | -1 | 10 | Yes | Categorie tematiche INSPIRE |
     | `3-2-4-2_PriorityDataset.rdf`      | 0 | -1 | 20 | Yes | Dataset prioritari |
     | `3-2-4-3_SpatialScope.rdf`         | 0 | -1 | 30 | Yes | Ambito di applicazione territoriale | 
     | `3-2-4-5_rndt-all1-fixed.rdf`      | 0 | -1 | 40 | Yes | Registro dei dati di interesse generale per il RNDT |

   - Codelists for INSPIRE/RNDT metadata fields  
     These thesauri are used internally as codelists, so they should not appear in the thesauri list in the metadata editor (so max=0).
     What's important here is to double check the `identifier` value, because that's how these thesauri are referenced internally.
   
     | File   | max | Identifier |
     |--------|-----|------------|
     | `ConditionsApplyingToAccessAndUse.rdf` | 0 | `ConditionsApplyingToAccessAndUse` | 
     | `LimitationsOnPublicAccess.rdf`        | 0 | `LimitationsOnPublicAccess` |
     
   - Localization entries for the RNDT custom metadata fields:
     As per the codelists, this should not appear in the metadata editor, and its identifier is important:

     | File   | max | Identifier |
     |--------|-----|------------|
     | `labels-i18n.rndt.rdf` | 0 | `labels-i18n` |
     
     Note that the labels thesaurus is incremental, and the various apps can add their own entries to it.
     The default `thesaurus load` action is `create` (see the GeoNode thesaurus doc page linked above), so this file needs to be loaded using the `--action update` parameter, or it may raise an error since the thesaurus may already exist in GeoNode.     

## Uninstalling

To uninstall the app, remove all the `rndt` functionalities (`INSTALLED_APPS` and `context_processors`) from  `settings.py` and restart the server. 
If needed made an hard refresh to let the browser reload the js/css/html files (windows: CTRL+ SHIFT+R | Mac: CMD+SHIFT+R)
