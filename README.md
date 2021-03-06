# geonode-rndt

Geonode-RNDT is a Django App to let GeoNode be able to expose the metadata compliant to the RNDT standard

![image](https://user-images.githubusercontent.com/717359/107668977-91f8ee00-6c91-11eb-8006-80e988dddeef.png)

Detailed information on the definition of RNDT are available at this [link](https://geodati.gov.it/geoportale/)

-----

## Configuration

1. Install the application as requirement:

       pip install -e git+https://github.com/geosolutions-it/geonode-rndt@master#egg=rndt

1. Add "rndt" to your INSTALLED_APPS setting like this::

       INSTALLED_APPS = [
          'rndt',
          ...
       ]
   
   If you have a `local_setting` file, you may want to add the `rndt` app with these lines:
   
       INSTALLED_APPS += ('rndt',)


1. Run ``python manage.py migrate`` to create the RNDT models.

1. To enable the `UUIDHandler`, add the following line in the `geonode.settings.py` file:

       LAYER_UUID_HANDLER = "rndt.uuidhandler.UUIDHandler"

1. To customize the metadata document to be RNDT compliant, use the rndt template:  

       CATALOG_METADATA_TEMPLATE = 'xml/template-rndt.xml'

1. To customize the XSL transformation to be aligned to the RNDT metadata format, use the provided XSL file:

       CATALOG_METADATA_XSL = '/static/rndt/rndt-metadata.xsl'


## Tests

In order to run tests (NOTE: must be in geonode venv), run ``python -m unittest -v`` to create the RNDT models.

## Uninstalling

To uninstall the app, remove all the `rndt` functionalities (`INSTALLED_APPS` and `context_processors`) from  `geonode.settings.py` and restart the server. 
If needed made an hard refresh to let the browser reload the js/css/html files (windows: CTRL+ SHIFT+R | Mac: CMD+SHIFT+R)


## Other config

Some custom environment variables are avaiable:

- `DISABLE_LAYER_CONSTRAINTS` (default `true`)  

  If `true` will hide from the Layers Metadata edit wizard page, the contraints in the tab `Location and Licenses`
