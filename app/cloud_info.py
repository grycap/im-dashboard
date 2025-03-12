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
"""Function to contact EGI Cloud Info."""
import requests

CLOUDINFO_URL = "http://is.ops.fedcloud.eu"
CLOUDINFO_TIMEOUT = 10


def cloudinfo_call(path, retries=3, url=CLOUDINFO_URL, timeout=CLOUDINFO_TIMEOUT):
    """Basic Cloud info REST API call."""
    data = None
    try:
        cont = 0
        while data is None and cont < retries:
            cont += 1
            resp = requests.request("GET", url + path, timeout=timeout)
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        data = {}

    return data


def get_vo_list():
    vos = []
    data = cloudinfo_call("/vos/")
    if data:
        vos = data
    return vos


def get_sites(vo=None):
    cloudinfo_url = "/sites/"
    if vo:
        cloudinfo_url += f"?vo_name={vo}"

    endpoints = {}
    data = cloudinfo_call(cloudinfo_url)
    for site in data:
        endpoints[site["name"]] = site
    return endpoints


def get_images(site_id, vo):
    oss = []

    cloudinfo_url = f"/site/{site_id}/{vo}/images"

    images = set()
    data = cloudinfo_call(cloudinfo_url)
    if data:
        images = set([(img["name"], img["appdb_id"]) for img in data])

    return list(images)


def get_project_ids(site_id):
    projects = {}
    data = cloudinfo_call(f"/site/{site_id}/projects")
    if data:
        projects = {proj["name"]: proj["id"] for proj in data}
    return projects
