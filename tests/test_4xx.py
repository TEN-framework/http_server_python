#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
from pathlib import Path
import time
from ten_runtime import (
    ExtensionTester,
    TenEnvTester,
)
import httpx


class ExtensionTester400MissingName(ExtensionTester):
    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()
        time.sleep(1)

        # Missing 'name' field should return 400
        property_json = {"payload": {"num": 1, "str": "111"}}
        r = httpx.post("http://127.0.0.1:8888/cmd", json=property_json)
        ten_env.log_debug(f"{r}")
        if r.status_code == httpx.codes.BAD_REQUEST:
            ten_env.stop_test()


class ExtensionTester404NotFound(ExtensionTester):
    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()
        time.sleep(1)

        # Non-existent path should return 404
        property_json = {"name": "aaa", "payload": {"num": 1, "str": "111"}}
        r = httpx.post("http://127.0.0.1:8888/cmd/aaa/123", json=property_json)
        ten_env.log_debug(f"{r}")
        if r.status_code == httpx.codes.NOT_FOUND:
            ten_env.stop_test()


class ExtensionTesterCmd400BadRequest(ExtensionTester):
    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()
        time.sleep(1)

        # Invalid JSON should return 400
        property_str = '{num": 1, "str": "111"}'  # not a valid json
        r = httpx.post("http://127.0.0.1:8888/cmd", content=property_str)
        ten_env.log_debug(f"{r}")
        if r.status_code == httpx.codes.BAD_REQUEST:
            ten_env.stop_test()


class ExtensionTesterData400BadRequest(ExtensionTester):
    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()
        time.sleep(1)

        # Invalid JSON should return 400
        property_str = '{num": 1, "str": "111"}'  # not a valid json
        r = httpx.post("http://127.0.0.1:8888/data", content=property_str)
        ten_env.log_debug(f"{r}")
        if r.status_code == httpx.codes.BAD_REQUEST:
            ten_env.stop_test()


def test_4xx():
    tester_400_missing = ExtensionTester400MissingName()
    tester_400_missing.set_test_mode_single("http_server_python")
    tester_400_missing.run()

    tester_404 = ExtensionTester404NotFound()
    tester_404.set_test_mode_single("http_server_python")
    tester_404.run()

    tester_cmd_400 = ExtensionTesterCmd400BadRequest()
    tester_cmd_400.set_test_mode_single("http_server_python")
    tester_cmd_400.run()

    tester_data_400 = ExtensionTesterData400BadRequest()
    tester_data_400.set_test_mode_single("http_server_python")
    tester_data_400.run()
