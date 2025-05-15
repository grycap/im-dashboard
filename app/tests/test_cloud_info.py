#! /usr/bin/env python
#
# IM - Infrastructure Manager
# Copyright (C) 2011 - GRyCAP - Universitat Politecnica de Valencia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
import os
import json

from app import cloud_info
from mock import patch, MagicMock
from urllib.parse import urlparse


def read_file_as_string(file_name):
    tests_path = os.path.dirname(os.path.abspath(__file__))
    abs_file_path = os.path.join(tests_path, file_name)
    return open(abs_file_path, "r").read()


class TestCloudInfo(unittest.TestCase):
    """Class to test the cloud info functions."""

    @staticmethod
    def requests_response(method, url, **kwargs):
        resp = MagicMock()
        parts = urlparse(url)
        url = parts[2]

        resp.status_code = 404
        resp.ok = False

        if url == "/vos/":
            resp.ok = True
            resp.status_code = 200
            resp.json.return_value = ["acc-comp.egi.eu"]
        return resp

    @patch("requests.request")
    def test_cloudinfo_call(self, requests):
        requests.side_effect = self.requests_response
        res = cloud_info.cloudinfo_call("/vos/")
        self.assertEqual(res[0], "acc-comp.egi.eu")

    @patch("app.cloud_info.cloudinfo_call")
    def test_vo_list(self, cloudinfo_call):
        cloud_info.VO_LIST = []
        vos = '["acc-comp.egi.eu"]'
        cloudinfo_call.return_value = json.loads(vos)
        res = cloud_info.get_vo_list()
        self.assertEqual(res, ["acc-comp.egi.eu"])
        cloud_info.VO_LIST = []

        vos = '["acc-comp.egi.eu", "vo.access.egi.eu"]'
        cloudinfo_call.return_value = json.loads(vos)
        res = cloud_info.get_vo_list()
        self.assertEqual(res, ["acc-comp.egi.eu", "vo.access.egi.eu"])

    @patch("app.cloud_info.cloudinfo_call")
    def test_get_sites(self, cloudinfo_call):
        site_json = """ [{
            "id": "1",
            "name": "TR-FC1-ULAKBIM",
            "url": "https://bulut.truba.gov.tr:5000/v3",
            "state": ""
        }]"""
        cloudinfo_call.return_value = json.loads(site_json)
        res = cloud_info.get_sites("vo.access.egi.eu")
        self.assertEqual(
            res,
            {
                "TR-FC1-ULAKBIM": {
                    "url": "https://bulut.truba.gov.tr:5000/v3",
                    "state": "",
                    "id": "1",
                    "name": "TR-FC1-ULAKBIM",
                }
            },
        )

    @patch("app.cloud_info.cloudinfo_call")
    def test_get_project_ids(self, cloudinfo_call):
        shares = """[
            {
                "id": "3a8e9d966e644405bf19b536adf7743d",
                "name": "vo.access.egi.eu"
            },
            {
                "id": "972298c557184a2192ebc861f3184da8",
                "name": "covid-19.eosc-synergy.eu"
            }
        ]"""
        cloudinfo_call.return_value = json.loads(shares)
        res = cloud_info.get_project_ids("TR-FC1-ULAKBIM")
        self.assertEqual(
            res,
            {
                "vo.access.egi.eu": "3a8e9d966e644405bf19b536adf7743d",
                "covid-19.eosc-synergy.eu": "972298c557184a2192ebc861f3184da8",
            },
        )

    @patch("app.cloud_info.cloudinfo_call")
    def test_get_images(self, cloudinfo_call):
        images = """[
            {
                "name": "ScipionCloud-GPU",
                "appdb_id": "scipioncloud.gpu",
                "id": "cea20767-9a69-46b2-aa7f-3da2f5857f1b",
                "mpuri": "https://appdb.egi.eu/store/vo/image/57bb9e4e-0d8d-5eff-aff1-57aa65e32c5c:15494/"
            }
        ]"""
        cloudinfo_call.return_value = json.loads(images)
        res = cloud_info.get_images("RECAS-BARI", "vo.access.egi.eu")
        self.assertEqual(res, [("ScipionCloud-GPU", "scipioncloud.gpu")])


if __name__ == "__main__":
    unittest.main()
