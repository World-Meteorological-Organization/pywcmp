# pywcmp

[![Build Status](https://github.com/World-Meteorological-Organization/pywcmp/workflows/build%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/World-Meteorological-Organization/pywcmp/actions)

# WMO Core Metadata Profile Test Suite

pywcmp provides validation and quality assessment capabilities for the [WMO WIS](https://community.wmo.int/en/activity-areas/wis) Core Metadata Profile (WCMP).

- validation against [WCMP2](https://wmo-im.github.io/wcmp2/standard/wcmp2-STABLE.html), specifically [Annex A: Conformance Class Abstract Test Suite](https://wmo-im.github.io/wcmp2/standard/wcmp2-STABLE.html#_conformance_class_abstract_test_suite_normative)), implementing an executable test suite against the ATS
- quality assessement against the [WCMP Key Performance Indicators]([https://community.wmo.int/activity-areas/wis/wis-metadata-kpis](https://wmo-im.github.io/wcmp2/kpi/wcmp2-kpi-DRAFT.html))

## Installation

### pip

Install latest stable version from [PyPI](https://pypi.org/project/pywcmp).

```bash
pip3 install pywcmp
```

### From source

Install latest development version.

```bash
python3 -m venv pywcmp
cd pywcmp
. bin/activate
git clone https://github.com/World-Meteorological-Organization/pywcmp.git
cd pywcmp
pip3 install -r requirements.txt
python3 setup.py install
```

## Running

From command line:
```bash
# fetch version
pywcmp --version

# sync supporting configuration bundle (schemas, topics, etc.)
pywcmp bundle sync

# abstract test suite

# validate WCMP2 metadata against abstract test suite (file on disk)
pywcmp ets validate /path/to/file.json

# validate WCMP2 metadata against abstract test suite (URL)
pywcmp ets validate https://example.org/path/to/file.json

# validate WCMP2 metadata against abstract test suite (URL), but turn JSON Schema validation off
pywcmp ets validate https://example.org/path/to/file.json --no-fail-on-schema-validation

# adjust debugging messages (CRITICAL, ERROR, WARNING, INFO, DEBUG) to stdout
pywcmp ets validate https://example.org/path/to/file.json --verbosity DEBUG

# write results to logfile
pywcmp ets validate https://example.org/path/to/file.json --verbosity DEBUG --logfile /tmp/foo.txt

# key performance indicators

# all key performance indicators at once
pywcmp kpi validate https://example.org/path/to/file.json --verbosity DEBUG

# all key performance indicators at once, but turn ETS validation off
pywcmp kpi validate https://example.org/path/to/file.json --no-fail-on-ets --verbosity DEBUG

# all key performance indicators at once, in summary
pywcmp kpi validate https://example.org/path/to/file.json --verbosity DEBUG --summary

# selected key performance indicator
pywcmp kpi validate --kpi title /path/to/file.json -v INFO
```

## Using the API
```pycon
>>> # test a file on disk
>>> import json
>>> from pywcmp.wcmp2.ets import WMOCoreMetadataProfileTestSuite2
>>> from pywcmp.errors import TestSuiteError
>>> with open('/path/to/file.json') as fh:
...     data = json.load(fh)
>>> # test ETS
>>> ts = WMOCoreMetadataProfileTestSuite2(datal)
>>> ts.run_tests()
>>> ts.raise_for_status()  # raises pywcmp.errors.TestSuiteError on exception with list of errors captured in .errors property
>>> # test a URL
>>> from urllib2 import urlopen
>>> from StringIO import StringIO
>>> content = StringIO(urlopen('https://....').read())
>>> data = json.loads(content)
>>> ts = WMOCoreMetadataProfileTestSuite2(data)
>>> ts.run_tests()
>>> ts.raise_for_status()  # raises pywcmp.errors.TestSuiteError on exception with list of errors captured in .errors property
>>> # test KPI
>>> from pywcmp.wcmp2.kpi import WMOCoreMetadataProfileKeyPerformanceIndicators
>>> kpis = WMOCoreMetadataProfileKeyPerformanceIndicators(data)
>>> results = kpis.evaluate()
>>> results['summary']
```

## Development

```bash
python3 -m venv pywcmp
cd pywcmp
source bin/activate
git clone https://github.com/World-Meteorological-Organization/pywcmp.git
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
python3 setup.py install
```

### Running tests

```bash
# via setuptools
python3 setup.py test
# manually
python3 tests/run_tests.py
```

## Releasing

```bash
# create release (x.y.z is the release version)
vi pywcmp/__init__.py  # update __version__
git commit -am 'update release version x.y.z'
git push origin master
git tag -a x.y.z -m 'tagging release version x.y.z'
git push --tags

# upload to PyPI
rm -fr build dist *.egg-info
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*

# publish release on GitHub (https://github.com/World-Meteorological-Organization/pywcmp/releases/new)

# bump version back to dev
vi pywcmp/__init__.py  # update __version__
git commit -am 'back to dev'
git push origin master
```

## Code Conventions

[PEP8](https://www.python.org/dev/peps/pep-0008)

## Issues

Issues are managed at https://github.com/World-Meteorological-Organization/pywcmp/issues

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
* [Ján Osuský](https://github.com/josusky)
