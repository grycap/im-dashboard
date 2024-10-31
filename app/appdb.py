#
# IM - Infrastructure Manager Dashboard
# Copyright (C) 2020 - GRyCAP - Universitat Politecnica de Valencia
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
"""Function to contact EGI AppDB."""
import requests
import xmltodict
from urllib.parse import urlparse

APPDB_URL = "https://appdb.egi.eu"
APPDB_TIMEOUT = 10


def appdb_call(path, retries=3, url=APPDB_URL, timeout=APPDB_TIMEOUT):
    """Basic AppDB REST API call."""
    data = None
    try:
        cont = 0
        while data is None and cont < retries:
            cont += 1
            resp = requests.request("GET", url + path, verify=False, timeout=timeout)
            if resp.status_code == 200:
                data = xmltodict.parse(resp.text.replace('\n', ''))['appdb:appdb']
    except Exception:
        data = {}

    return data


def get_vo_list():
    vos = []
    data = appdb_call('/rest/1.0/vos')
    if data:
        if isinstance(data['vo:vo'], list):
            for vo in data['vo:vo']:
                vos.append(vo['@name'])
        else:
            vos.append(data['vo:vo']['@name'])
    return vos


def _get_services(vo=None):
    appdburl = '/rest/1.0/sites'
    if vo:
        appdburl += '?flt=%%2B%%3Dvo.name:%s&%%2B%%3Dsite.supports:1' % vo

    data = appdb_call(appdburl)

    if not data or 'appdb:site' not in data:
        return []

    if isinstance(data['appdb:site'], list):
        sites = data['appdb:site']
    else:
        sites = [data['appdb:site']]

    services = []
    for site in sites:
        if 'site:service' in site:
            if isinstance(site['site:service'], list):
                services.extend(site['site:service'])
            else:
                services.append(site['site:service'])

    return services


def get_sites(vo=None):
    providersID = [service['@id'] for service in _get_services(vo)]

    # Get provider metadata
    endpoints = {}
    for ID in providersID:
        data = appdb_call('/rest/1.0/va_providers/%s' % ID)
        if data and 'virtualization:provider' in data:
            site = data['virtualization:provider']
            if ('provider:url' in site and site['@service_type'] == 'org.openstack.nova'):
                provider_name = site['provider:name']
                critical = ""
                if '@service_status' in site and site['@service_status'] == "CRITICAL":
                    critical = "CRITICAL"
                provider_endpoint_url = site['provider:url']
                url = urlparse(provider_endpoint_url)
                endpoints[provider_name] = {"url": "%s://%s" % url[0:2],
                                            "state": critical,
                                            "id": ID,
                                            "name": provider_name}

    return endpoints


def get_images(site_id, vo):
    oss = []

    try:
        va_data = appdb_call('/rest/1.0/va_providers/%s' % site_id, timeout=APPDB_TIMEOUT * 4)

        images = []
        if ('provider:image' in va_data['virtualization:provider'] and
                va_data['virtualization:provider']['provider:image']):
            if isinstance(va_data['virtualization:provider']['provider:image'], list):
                images = va_data['virtualization:provider']['provider:image']
            else:
                images = [va_data['virtualization:provider']['provider:image']]

        for os_tpl in images:
            try:
                if '@voname' in os_tpl and vo == os_tpl['@voname']:
                    if (os_tpl['@appname'], os_tpl['@appcname']) not in oss:
                        oss.append((os_tpl['@appname'], os_tpl['@appcname']))
            except Exception:
                continue
    except Exception:
        oss = []

    return oss


def get_project_ids(service_id):
    projects = {}
    # Until it is on the prod instance use the Devel one

    data = appdb_call('/rest/1.0/va_providers/%s' % service_id)
    if (data and 'virtualization:provider' in data and data['virtualization:provider'] and
            'provider:shares' in data['virtualization:provider'] and
            data['virtualization:provider']['provider:shares'] and
            'vo:vo' in data['virtualization:provider']['provider:shares'] and
            data['virtualization:provider']['provider:shares']['vo:vo']):
        if isinstance(data['virtualization:provider']['provider:shares']['vo:vo'], list):
            shares = data['virtualization:provider']['provider:shares']['vo:vo']
        else:
            shares = [data['virtualization:provider']['provider:shares']['vo:vo']]

        for vo in shares:
            projects[vo["#text"]] = vo['@projectid']

    return projects
