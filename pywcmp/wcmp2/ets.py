###############################################################################
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2023 Tom Kralidis
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
###############################################################################

# executable test suite as per WMO Core Metadata Profile 2, Annex A

import csv
import json
import logging
from pathlib import Path

from jsonschema.validators import Draft202012Validator

from pywcmp.bundle import WCMP2_FILES
from pywcmp.wcmp2.topics import TopicHierarchy
from pywcmp.util import get_userdir

LOGGER = logging.getLogger(__name__)


def gen_test_id(test_id: str) -> str:
    """
    Convenience function to print test identifier as URI

    :param test_id: test suite identifier

    :returns: test identifier as URI
    """

    return f'http://www.wmo.int/spec/wcmp/2/req/conf/core/{test_id}'


class WMOCoreMetadataProfileTestSuite2:
    """Test suite for WMO Core Metadata Profile assertions"""

    def __init__(self, data: dict):
        """
        initializer

        :param data: dict of WCMP2 JSON

        :returns: `pywcmp.wcmp2.ets.WMOCoreMetadataProfileTestSuite2`
        """

        self.test_id = None
        self.record = data
        self.report = []

    def run_tests(self, fail_on_schema_validation=False):
        """Convenience function to run all tests"""

        results = []
        tests = []
        ets_report = {
            'summary': {},
        }

        for f in dir(WMOCoreMetadataProfileTestSuite2):
            if all([
                    callable(getattr(WMOCoreMetadataProfileTestSuite2, f)),
                    f.startswith('test_requirement'),
                    not f.endswith('validation')]):

                tests.append(f)

        validation_result = self.test_requirement_validation()
        if validation_result['code'] == 'FAILED':
            if fail_on_schema_validation:
                msg = ('Record fails WCMP2 validation. Stopping ETS ',
                       f"errors: {validation_result['message']}")
                LOGGER.error(msg)
                raise ValueError(msg)

        for t in tests:
            results.append(getattr(self, t)())

        for code in ['PASSED', 'FAILED', 'SKIPPED']:
            r = len([t for t in results if t['code'] == code])
            ets_report['summary'][code] = r

        ets_report['tests'] = results

        return {
            'ets-report': ets_report
        }

    def test_requirement_validation(self):
        """
        Validate that a WCMP record is valid to the authoritative WCMP schema.
        """

        validation_errors = []

        status = {
            'id': gen_test_id('validation'),
            'code': 'PASSED'
        }

        schema = WCMP2_FILES / 'wcmp2-bundled.json'

        if not schema.exists():
            msg = "WCMP2 schema missing. Run 'pywcmp bundle sync' to cache"
            LOGGER.error(msg)
            raise RuntimeError(msg)

        with schema.open() as fh:
            LOGGER.debug(f'Validating {self.record} against {schema}')
            validator = Draft202012Validator(json.load(fh))

            for error in validator.iter_errors(self.record):
                LOGGER.debug(f'{error.json_path}: {error.message}')
                validation_errors.append(f'{error.json_path}: {error.message}')

            if validation_errors:
                status['code'] = 'FAILED'
                status['message'] = f'{len(validation_errors)} error(s)'
                status['errors'] = validation_errors

        return status

    def test_requirement_identifier(self):
        """
        Validate that a WCMP record has a valid identifier.
        """

        status = {
            'id': gen_test_id('identifier'),
            'code': 'PASSED'
        }

        identifier = self.record['id']

        if identifier.count(':') != 5:
            status['code'] = 'FAILED'
            status['message'] = "identifier does not have six ':' delimiters"
            return status

        if not identifier.startswith('urn:x-wmo:md:'):
            status['code'] = 'FAILED'
            status['message'] = 'bad prefix'
            return status

        th = TopicHierarchy()

        country, centre_id = identifier.split(':')[3:5]

        if country not in th.list_children('origin/a/wis2'):
            status['code'] = 'FAILED'
            status['message'] = f'Invalid country: {country}'
            return status

        centre_ids = th.list_children(f'origin/a/wis2/{country}')
        if centre_id not in centre_ids:
            status['code'] = 'FAILED'
            status['message'] = f'Invalid centre_id: {centre_id}'
            return status

        if not identifier.isascii():
            status['code'] = 'FAILED'
            status['message'] = 'Bad characters in id'
            return status

        return status

    def test_requirement_conformance(self):
        """
        Validate that a WCMP record provides valid conformance information.
        """

        conformance_class = 'http://wis.wmo.int/spec/wcmp/2/conf/core'

        status = {
            'id': gen_test_id('conformance'),
            'code': 'PASSED'
        }

        conformance = self.record.get('conformsTo')

        if conformance_class not in conformance:
            status['code'] = 'FAILED'
            status['message'] = f'Missing conformance class {conformance_class}'  # noqa

        return status

    def test_requirement_type(self):
        """
        Check for the existence of a valid properties.type property in
        the WCMP record.
        """

        found = False

        status = {
            'id': gen_test_id('type'),
            'code': 'PASSED'
        }

        rt = Path(get_userdir()) / 'wcmp-2' / 'codelists' / 'resource-type.csv'

        if not rt.exists():
            msg = 'WCMP2 codeslists missing. Run "pywcmp bundle sync"'
            LOGGER.error(msg)
            raise RuntimeError(msg)

        with rt.open() as fh:
            LOGGER.debug(f'Reading topic hierarchy file {rt}')
            reader = csv.DictReader(fh)
            for row in reader:
                if self.record['properties']['type'] == row['Name']:
                    found = True
                    break

        if not found:
            status['code'] = 'FAILED'
            status['message'] = f"Invalid type: {self.record['properties']['type']}"  # noqa

        return status

    def test_requirement_extent_geospatial(self):
        """
        Check for the existence of a valid geometry property in
        the WCMP record.
        """

        status = {
            'id': gen_test_id('extent_geospatial'),
            'code': 'PASSED',
            'message': 'Passes given schema is compliant/valid'
        }

        return status

    def test_requirement_extent_temporal(self):
        """
        Validate that a WCMP record provides a valid temporal extent property.
        """

        status = {
            'id': gen_test_id('extent_temporal'),
            'code': 'PASSED',
            'message': 'Passes given schema is compliant/valid'
        }

        return status

    def test_requirement_title(self):
        """
        Validate that a WCMP record provides a title property.
        """

        status = {
            'id': gen_test_id('title'),
            'code': 'PASSED',
            'message': 'Passes given schema is compliant/valid'
        }

        return status

    def test_requirement_description(self):
        """
        Validate that a WCMP record provides a description property.
        """

        status = {
            'id': gen_test_id('description'),
            'code': 'PASSED',
            'message': 'Passes given schema is compliant/valid'
        }

        return status

    def test_requirement_themes(self):
        """
        Validate that a WCMP record provides a themes property.
        """

        status = {
            'id': gen_test_id('themes'),
            'code': 'PASSED'
        }

        themes = self.record['properties']['themes']

        if len(themes) < 1:
            status['code'] = 'FAILED'
            status['message'] = 'Missing at least one theme'

            return status

        for t in themes:
            concepts = t['concepts']
            if len(concepts) < 1:
                status['code'] = 'FAILED'
                status['message'] = 'Missing at least one concept'

                return status

            if t.get('scheme') is None:
                status['code'] = 'FAILED'
                status['message'] = 'Missing scheme'

                return status

            for c in concepts:
                if c.get('id') is None:
                    status['code'] = 'FAILED'
                    status['message'] = 'Missing concept id'

                return status

        return status

    def test_requirement_contacts(self):
        """
        Validate that a WCMP record provides contact information for the
        metadata point of contact and originator of the data.
        """

        status = {
            'id': gen_test_id('contacts'),
            'code': 'PASSED'
        }

        contacts = self.record['properties']['contacts']

        for role_type in ['originator', 'pointOfContact']:
            for c in contacts:
                if role_type not in c['roles']:
                    status['code'] = 'FAILED'
                    status['message'] = f'Missing required role {role_type}'

        return status

    def test_requirement_creation_date(self):
        """
        Validate that a WCMP record provides a record creation date.
        """

        status = {
            'id': gen_test_id('record_creation_date'),
            'code': 'PASSED',
            'message': 'Passes given schema is compliant/valid'
        }

        return status

    def test_requirement_data_policy(self):
        """
        Validate that a WCMP record provides information about data policy and,
        if applicable additional information about licensing and/or rights.
        """

        found = False

        status = {
            'id': gen_test_id('data_policy'),
            'code': 'PASSED'
        }

        if self.record['properties']['type'] == 'dataset':
            if 'wmo:dataPolicy' not in self.record['properties']:
                status['code'] = 'FAILED'
                status['message'] = 'Missing data policy'
                return status

            data_policy = self.record['properties']['wmo:dataPolicy']

            dp = Path(get_userdir()) / 'wis2-topic-hierarchy' / 'data-policy.csv'  # noqa

            if not dp.exists():
                msg = 'WCMP2 codelists missing. Run "pywcmp bundle sync"'
                LOGGER.error(msg)
                raise RuntimeError(msg)

            with dp.open() as fh:
                LOGGER.debug(f'Reading topic hierarchy file {dp}')
                reader = csv.DictReader(fh)
                for row in reader:
                    if data_policy == row['Name']:
                        found = True
                        break

            if not found:
                status['code'] = 'FAILED'
                status['message'] = f'Invalid data policy {data_policy}'
                return status

            if data_policy == 'recommended':
                conditions_links = [link for link in self.record['links']
                                    if link['rel'] in ['license', 'copyright']]
                if not conditions_links:
                    status['code'] = 'FAILED'
                    status['message'] = 'missing recommended conditions'
                    return status

        return status

    def test_requirement_links(self):
        """
        Validate that a WCMP record provides a link property.
        """

        status = {
            'id': gen_test_id('links'),
            'code': 'PASSED'
        }

        links = self.record['links']

        LOGGER.debug('Checking for at least one link')
        if len(links) < 1:
            status['code'] = 'FAILED'
            status['message'] = 'missing at least one link'
            return status

        for link in links:
            LOGGER.debug('Checking that Pub/Sub links have a channel')
            if link['href'].startswith('mqtt'):
                if 'channel' not in link:
                    status['code'] = 'FAILED'
                    status['message'] = 'missing channel for Pub/Sub link'
                    return status

            LOGGER.debug('Checking that links with security have descriptions')
            if 'security' in link:
                if link['security'].get('description') is None:
                    status['code'] = 'FAILED'
                    status['message'] = 'missing security descirption for link'
                    return status

        return status
