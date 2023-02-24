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

#
# pywcmp as a service
# -------------------
#
# This file is intended to be used as a pygeoapi process plugin which will
# provide pywcmp functionality via OGC API - Processes.
#
# To integrate this plugin in pygeoapi:
#
# 1. ensure pywcmp is installed into the pygeoapi deployment environment
#
# 2. add the processes to the pygeoapi configuration as follows:
#
# pywcmp-wis2-topics-list:
#     type: process
#     processor:
#         name: pywcmp.pygeoapi_plugin.WIS2TopicHierarchyListTopicsProcessor
#
# pywcmp-wis2-topics-validate:
#     type: process
#     processor:
#         name: pywcmp.pygeoapi_plugin.WIS2TopicHierarchyListTopicsProcessor
#
# pywcmp-wis2-wcmp2-ets:
#     type: process
#     processor:
#         name: pywcmp.pygeoapi_plugin.WCMP2ETSProcessor
#
# 3. (re)start pygeoapi
#
# The resulting processes will be available at the following endpoints:
#
# /processes/pywcmp-wis2-topics-list
#
# /processes/pywcmp-wis2-topics-validate

# /processes/pywcmp-wis2-wcmp2-ets
#
# Note that pygeoapi's OpenAPI/Swagger interface (at /openapi) will also
# provide a developer-friendly interface to test and run requests
#


import logging

from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError

from pywcmp.wcmp2.topics import TopicHierarchy
from pywcmp.wcmp2.ats import WMOCoreMetadataProfileTestSuite2

LOGGER = logging.getLogger(__name__)

WIS2_TOPIC_HIERARCHY_LINKS = [{
    'type': 'text/html',
    'rel': 'about',
    'title': 'information',
    'href': 'https://github.com/wmo-im/wis2-topic-hierarchy',
    'hreflang': 'en-US'
}]

WIS2_TOPIC_HIERARCHY_INPUT_TOPIC = {
    'title': 'Topic',
    'description': 'Topic (full or partial)',
    'schema': {
        'type': 'string'
    },
    'minOccurs': 1,
    'maxOccurs': 1,
    'metadata': None,
    'keywords': ['topic']
}


PROCESS_LIST_TOPICS = {
    'version': '0.1.0',
    'id': 'pywcmp-wis2-topics-list',
    'title': {
        'en': 'list WIS2 topics'
    },
    'description': {
        'en': 'Lists WIS2 topics'
    },
    'keywords': ['wis2', 'topics', 'metadata'],
    'links': WIS2_TOPIC_HIERARCHY_LINKS,
    'inputs': {
        'topic': WIS2_TOPIC_HIERARCHY_INPUT_TOPIC,
    },
    'outputs': {
        'result': {
            'title': 'List of child topics',
            'description': 'List of child topics',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'topic': 'origin/a/wis2'
        }
    }
}


PROCESS_VALIDATE_TOPIC = {
    'version': '0.1.0',
    'id': 'pywcmp-wis2-topics-validate',
    'title': {
        'en': 'list WIS2 topics'
    },
    'description': {
        'en': 'Lists WIS2 topics'
    },
    'keywords': ['wis2', 'topics', 'metadata'],
    'links': WIS2_TOPIC_HIERARCHY_LINKS,
    'inputs': {
        'record': {
            'title': 'record',
            'description': 'WCMP2 record',
            'schema': {
                'type': object
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['topic']
        }
    },
    'outputs': {
        'result': {
            'title': 'List of child topics',
            'description': 'List of child topics',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'topic': 'origin/a/wis2',
            'fuzzy': True
        }
    }
}

PROCESS_WCMP2_ETS = {
    'version': '0.1.0',
    'id': 'pywcmp-wis2-wcmp2-ets',
    'title': {
        'en': 'validate a WCMP2 document against the ATS'
    },
    'description': {
        'en': 'validate a WCMP2 document against the ATS'
    },
    'keywords': ['wis2', 'wcmp2', 'metadata'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://wmo-im.github.io/wcmp2',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'record': {
            'title': 'WCMP2 record',
            'description': 'WCMP2 record',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'metadata': None,
            'keywords': ['wcmp2']
        }
    },
    'outputs': {
        'result': {
            'title': 'Report of ETS results',
            'description': 'Report of ETS results',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/json'
            }
        }
    },
    'example': {
        'inputs': {
            'record': {
                '$ref': 'https://raw.githubusercontent.com/wmo-im/pywcmp/master/tests/data/wcmp2-passing.json'
            }
        }
    }
}


class WIS2TopicHierarchyListTopicsProcessor(BaseProcessor):
    """WIS2 topic hierarchy list process"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: wis2box_api.plugins.process.metadata.WIS2TopicHierarchyListTopicsProcessor  # noqa
        """

        super().__init__(processor_def, PROCESS_LIST_TOPICS)

    def execute(self, data):

        response = None
        mimetype = 'application/json'
        topic = data.get('topic')

        if topic is None:
            msg = 'Missing topic'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        LOGGER.debug('Querying topic')
        th = TopicHierarchy()
        try:
            matching_topics = th.list_children(topic)
            response = {
                'topics': matching_topics
            }
        except ValueError as err:
            raise ProcessorExecuteError(err)

        return mimetype, response

    def __repr__(self):
        return '<WIS2TopicHierarchyListTopicsProcessor>'


class WIS2TopicHierarchyValidateTopicProcessor(BaseProcessor):
    """WIS2 topic hierarchy validate process"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: wis2box_api.plugins.process.metadata.WIS2TopicHierarchyValidateTopicProcessor  # noqa
        """

        super().__init__(processor_def, PROCESS_VALIDATE_TOPIC)

    def execute(self, data):

        response = None
        mimetype = 'application/json'
        topic = data.get('topic')
        fuzzy = data.get('fuzzy', False)

        if topic is None:
            msg = 'Missing topic'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        LOGGER.debug('Querying topic')
        th = TopicHierarchy()
        response = {
            'topic_is_valid': th.validate(topic, fuzzy)
        }
        return mimetype, response

    def __repr__(self):
        return '<WIS2TopicHierarchyValidateTopicProcessor>'


class WCMP2ETSProcessor(BaseProcessor):
    """WCMP2 ETS"""

    def __init__(self, processor_def):
        """
        Initialize object

        :param processor_def: provider definition

        :returns: wis2box_api.plugins.process.metadata.WCMP2ETSProcessor
        """

        super().__init__(processor_def, PROCESS_WCMP2_ETS)

    def execute(self, data):

        response = None
        mimetype = 'application/json'
        record = data.get('record')

        if record is None:
            msg = 'Missing record'
            LOGGER.error(msg)
            raise ProcessorExecuteError(msg)

        LOGGER.debug('Running ETS against record')
        response = WMOCoreMetadataProfileTestSuite2(record).run_tests()

        return mimetype, response

    def __repr__(self):
        return '<WCMP2ETSProcessor>'
