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
<<<<<<< HEAD
5. enable RNDT context processors in `geonode.settings.py` by adding the following line in `TEMPLATES`:
```
'OPTIONS': {
    'context_processors': [
        .........
        'rndt.context_processors.rndt_tags'
    ],
}
```

6. Run ``python manage.py migrate`` to create the RNDT models.

To uninstall the app, remove all the `rndt` functionalities (`installed_apps` and `context_processors`) from  `geonode.settings.py` and restart the server. If needed made an hard refresh to let the browser reload the js/css/html files (windows: CTRL+ SHIFT+R | Mac: CMD+SHIFT+R)


Configs
--
---------

Some custom environment variables are avaiable:

DISABLE_LAYER_CONSTRAINTS (default `true`)

If `true` will hide from the Layers Metadata edit wizard page, the contraints in the tab `Location and Licenses`
=======

5. Run ``python manage.py migrate`` to create the RNDT models.

<<<<<<< HEAD
To uninstall the app remove `rndt` from  `geonode.settings.py`, restart the server. If needed made an hard refresh to let the browser reload the js/css/html files (windows: CTRL+ SHIFT+R | Mac: CMD+SHIFT+R)
>>>>>>> e4b6599fdc98790b86a70b89620582485f735ad2
=======

4. Run Tests (NOTE: must be in geonode venv) ``python -m unittest -v`` to create the RNDT models.

5. To enable the UUIDHandler, add the following line in the `geonode.settings.py` file

```
LAYER_UUID_HANDLER = "rndt.uuidhandler.UUIDHandler"
```
>>>>>>> b719c0b377e9542ae1b39c1fff843926fdb995be
