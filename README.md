# geonode-rndt

Geonode-RNDT is a Django App to let GeoNode be able to expose the metadata compliant to the RNDT standard

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
        ...
        'rndt',
    ]

3. Run ``python manage.py migrate`` to create the RNDT models.


4. Run Tests (NOTE: must be in geonode venv) ``python -m unittest -v`` to create the RNDT models.

5. To enable the UUIDHandler, add the following line in the `geonode.settings.py` file

```
LAYER_UUID_HANDLER = "rndt.uuidhandler.UUIDHandler"
```
