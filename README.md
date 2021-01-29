# geonode-rndt

Geonode-RNDT is a Django App to let GeoNode be able to expose the metadata complaint to the RNDT standard

Detailed information on the definition of RNDT are available at this [link](https://geodati.gov.it/geoportale/)

-----

Quick start
-----------
1. Install the application as requirement
```
pip install -e git+https://github.com/geosolutions-it/geonode-rndt@setup_minimum_django_req#egg=rndt
```

2. Add "rndt" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'rndt',
    ]

3. Run ``python manage.py migrate`` to create the RNDT models.

