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
"""Class to manage user credentials using a Vault backend."""
import hvac
import requests
from flask import json
from app.cred import Credentials


class VaultCredentials(Credentials):

    def __init__(self, vault_url, mount_point=None, path=None, role=None, kv_ver=1, ssl_verify=False):
        self.mount_point = "credentials/"
        if mount_point:
            self.mount_point = mount_point
        self.path = path
        self.role = role
        self.client = None
        self.ssl_verify = ssl_verify
        self.kv_ver = kv_ver
        super().__init__(vault_url)

    def _login(self, token_vault):
        # split the data from the token_vault var
        token, vault_info = token_vault
        if vault_info:
            # if set use this values
            url, mount_point, path, kv_ver = vault_info
        else:
            # if not use the default ones
            url = self.url
            kv_ver = self.kv_ver
            mount_point = self.mount_point
            path = self.path

        login_url = url + '/v1/auth/jwt/login'

        if self.role:
            data = '{ "jwt": "' + token + '", "role": "' + self.role + '" }'
        else:
            data = '{ "jwt": "' + token + '" }'

        response = requests.post(login_url, data=data, verify=self.ssl_verify, timeout=5)

        if not response.ok:
            raise Exception("Error getting Vault token: {} - {}".format(response.status_code, response.text))

        deserialized_response = response.json()

        vault_auth_token = deserialized_response["auth"]["client_token"]
        vault_entity_id = deserialized_response["auth"]["entity_id"]

        client = hvac.Client(url=url, token=vault_auth_token, verify=self.ssl_verify)
        if not client.is_authenticated():
            raise Exception("Error authenticating against Vault with token: {}".format(vault_auth_token))

        if path is None:
            path = vault_entity_id

        if kv_ver == 1:
            return client.secrets.kv.v1, mount_point, path
        elif kv_ver == 2:
            return client.secrets.kv.v2, mount_point, path
        else:
            raise Exception("Invalid KV version (1 or 2)")

    def get_creds(self, userid, enabled=None):
        client, mount_point, path = self._login(userid)
        data = []

        try:
            creds = client.read_secret(path=path, mount_point=mount_point)
            for cred_json in creds["data"].values():
                new_item = json.loads(cred_json)
                if enabled is None or enabled == new_item['enabled']:
                    data.append(new_item)
        except Exception:
            pass

        return data

    def get_cred(self, serviceid, userid):
        client, mount_point, path = self._login(userid)
        creds = client.read_secret(path=path, mount_point=mount_point)
        if serviceid in creds["data"]:
            return json.loads(creds["data"][serviceid])
        else:
            return None

    def write_creds(self, serviceid, userid, data, insert=False):
        client, mount_point, path = self._login(userid)
        try:
            creds = client.read_secret(path=path, mount_point=mount_point)
        except Exception:
            creds = None

        if creds:
            old_data = creds["data"]
            if serviceid in creds["data"]:
                if insert:
                    raise Exception("Duplicated Credential ID!.")
                service_data = json.loads(creds["data"][serviceid])
                service_data.update(data)
                creds["data"][serviceid] = service_data
            else:
                old_data[serviceid] = data
                old_data[serviceid]['enabled'] = 1
        else:
            old_data = {serviceid: data}
            old_data[serviceid]['enabled'] = 1

        old_data[serviceid] = json.dumps(old_data[serviceid])
        response = client.create_or_update_secret(path,
                                                  old_data,
                                                  mount_point=mount_point)

        response.raise_for_status()

    def delete_cred(self, serviceid, userid):
        client, mount_point, path = self._login(userid)

        creds = client.read_secret(path=path, mount_point=mount_point)
        if serviceid in creds["data"]:
            del creds["data"][serviceid]
            if creds["data"]:
                response = client.create_or_update_secret(path,
                                                          creds["data"],
                                                          method="PUT",
                                                          mount_point=mount_point)
            else:
                if self.kv_ver == 1:
                    response = client.delete_secret(path,
                                                    mount_point=mount_point)
                else:
                    response = client.delete_metadata_and_all_versions(path,
                                                                       mount_point=mount_point)
            response.raise_for_status()

    def enable_cred(self, serviceid, userid, enable=1):
        client, mount_point, path = self._login(userid)

        creds = client.read_secret(path=path, mount_point=mount_point)
        if serviceid in creds["data"]:
            service_data = json.loads(creds["data"][serviceid])
            service_data["enabled"] = int(enable)
            creds["data"][serviceid] = json.dumps(service_data)
            response = client.create_or_update_secret(path,
                                                      creds["data"],
                                                      method="PUT",
                                                      mount_point=mount_point)
            response.raise_for_status()
