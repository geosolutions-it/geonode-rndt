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

1. Optionally, also publish via CSW the services of the [csw_services](https://github.com/geosolutions-it/geonode-csw-services) app:
   CSW searches only return the resource types in the GeoNode `PYCSW["FILTER"]` (by default, datasets only):

       PYCSW["FILTER"] = {"resource_type__in": ["dataset", "cswservice"]}

1. Configure the thesauri  
   The thesauri in `rndt/thesauri/` are loaded by `python manage.py thesaurus autoload`, which the GeoNode Docker
   entrypoint runs at every start. They are created hidden from the metadata editor (max=0); to show the INSPIRE/RNDT
   vocabularies, set them in the Thesaurus admin page (reloading keeps these settings):

   | Identifier                     | min | max | order | facet |
   |--------------------------------|-----|-----|-------|-------|
   | `3-2-4-1_gemet-inspire-themes` | 1   | -1  | 10    | Yes   |
   | `3-2-4-2_PriorityDataset`      | 0   | -1  | 20    | Yes   |
   | `3-2-4-3_SpatialScope`         | 0   | -1  | 30    | Yes   |
   | `3-2-4-5_rndt-all1-fixed`      | 0   | -1  | 40    | Yes   |

## Upgrading from 4.x

- Custom metadata templates: replace `{% load metadata_tags %}` with `{% load rndt_tags %}`.
- Thesauri: `thesaurus autoload` identifies them by file name (see the table above, plus `ConditionsApplyingToAccessAndUse`,
  `LimitationsOnPublicAccess`, `labels-i18n`). Check the existing ones with `python manage.py thesaurus list`:
  if they were loaded with different identifiers, rename them in the Thesaurus admin page before the first autoload,
  or they will be loaded twice.
- Dataset uuids: datasets of groups that got their first PA before this version may lack the iPA prefix,
  so they are missing from `catalogue/csw/<iPA code>`. Check with `python manage.py rndt_uuids check`,
  then fix with `python manage.py rndt_uuids fix`; both accept a list of dataset ids or uuids to limit them.

## Endpoints

- `catalogue/csw/<iPA code>`: CSW limited to the resources of one Pubblica Amministrazione
- `api/pubblica_amministrazione/`: the list of the Pubbliche Amministrazioni

## Testing

The tests need GeoNode installed in the current environment, but no database. From the repository root:

```bash
python -m tests.run
```

CI runs them on every PR against GeoNode `5.1.1` and `master` (see `.github/workflows/tests.yml`).

Linting and formatting are done by [ruff](https://docs.astral.sh/ruff/) (configured in `pyproject.toml`, version pinned in the `dev` extra):

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
```

## Uninstalling

To uninstall the app, remove all the `rndt` functionalities (`INSTALLED_APPS` and `context_processors`) from  `settings.py` and restart the server. 
If needed made an hard refresh to let the browser reload the js/css/html files (windows: CTRL+ SHIFT+R | Mac: CMD+SHIFT+R)
