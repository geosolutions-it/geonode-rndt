"""Run the rndt tests: they need GeoNode installed, but no database."""

import os
import sys
import unittest

import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
# GeoNode settings require them, but no connection is ever opened
os.environ.setdefault("DATABASE_URL", "postgis://user:pass@localhost:5432/geonode")
os.environ.setdefault("GEODATABASE_URL", "postgis://user:pass@localhost:5432/geonode_data")
os.environ.setdefault("SITEURL", "http://localhost:8000/")

django.setup()
result = unittest.main(module="rndt.tests", argv=["rndt.tests", "-v"] + sys.argv[1:], exit=False).result
sys.exit(not result.wasSuccessful())
