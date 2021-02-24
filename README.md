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

   **NOTE**: make sure to put '`rndt`' as the first app (or anyway before '`geonode`')
   
   If you have a `local_setting` file, you may want to add the `rndt` app with these lines:
   
       geonode_index = INSTALLED_APPS.index('geonode')
       INSTALLED_APPS = INSTALLED_APPS[:geonode_index]+('rndt',)+INSTALLED_APPS[geonode_index:]

1. In `geonode.settings.py` set `DIR` for `TEMPLATES` as `[]` in order to let the app overrides the templates.  
 
   If you have a `local_setting` file, you may want to do it with this line:
   
       TEMPLATES[0]['DIRS'] = []

1. In order to let the app overrides some static files, move the `AppDirectoriesFinder` as the first item
   in `geonode.settings.py` in `STATICFILES_FINDERS` settings.  
   The output should be something like this:

       STATICFILES_FINDERS = (
          'django.contrib.staticfiles.finders.AppDirectoriesFinder',
          'django.contrib.staticfiles.finders.FileSystemFinder'
       )

1. Enable RNDT context processors in `geonode.settings.py` by adding the following line in `TEMPLATES`:

       'OPTIONS': {
          'context_processors': [
              ...
              'rndt.context_processors.rndt_tags'
          ],
       }

   If you have a `local_setting` file, you may want to do it with this line:

       TEMPLATES[0]['OPTIONS']['context_processors'].append('rndt.context_processors.rndt_tags')


1. Run ``python manage.py migrate`` to create the RNDT models.

1. To enable the `UUIDHandler`, add the following line in the `geonode.settings.py` file:

       LAYER_UUID_HANDLER = "rndt.uuidhandler.UUIDHandler"

1. To customize the metadata document to be RNDT compliant, use the rndt template:  

       CATALOG_METADATA_TEMPLATE = 'xml/template-rndt.xml'




## Tests

In order to run tests (NOTE: must be in geonode venv), run ``python -m unittest -v`` to create the RNDT models.

## Uninstalling

To uninstall the app, remove all the `rndt` functionalities (`INSTALLED_APPS` and `context_processors`) from  `geonode.settings.py` and restart the server. 
If needed made an hard refresh to let the browser reload the js/css/html files (windows: CTRL+ SHIFT+R | Mac: CMD+SHIFT+R)


## Other config

Some custom environment variables are avaiable:

- `DISABLE_LAYER_CONSTRAINTS` (default `true`)  

  If `true` will hide from the Layers Metadata edit wizard page, the contraints in the tab `Location and Licenses`
