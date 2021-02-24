# geonode-rndt

Geonode-RNDT is a Django App to let GeoNode be able to expose the metadata compliant to the RNDT standard

![image](https://user-images.githubusercontent.com/717359/107668977-91f8ee00-6c91-11eb-8006-80e988dddeef.png)


Detailed information on the definition of RNDT are available at this [link](https://geodati.gov.it/geoportale/)

-----

Quick start
-----------
1. Install the application as requirement
```
pip install -e git+https://github.com/geosolutions-it/geonode-rndt@master#egg=rndt
```

2. Add "rndt" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        'rndt',
        ...
    ]

NOTE: be sure to put it as first app

3.  in `geonode.settings.py` set `DIR` for `TEMPLATES` as `[]` in order to let the app overrides the templates

4.  in order to let the app overrides some static files move the `AppDirectoriesFinder` as first choice in `geonode.settings.py` in `STATICFILES_FINDERS` settings. The output should be something like this:
```
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder'
)

```

5. Run ``python manage.py migrate`` to create the RNDT models.

6. Run Tests (NOTE: must be in geonode venv) ``python -m unittest -v``

7. To enable the UUIDHandler, add the following line in the `geonode.settings.py` file

```
LAYER_UUID_HANDLER = "rndt.uuidhandler.UUIDHandler"
```

To uninstall the app remove `rndt` from  `geonode.settings.py`, restart the server. If needed made an hard refresh to let the browser reload the js/css/html files (windows: CTRL+ SHIFT+R | Mac: CMD+SHIFT+R)
