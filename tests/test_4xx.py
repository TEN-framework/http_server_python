#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
from pathlib import Path
from ten import (
    ExtensionTester,
    TenEnvTester,
)
import httpx


class ExtensionTester404NotFound1(ExtensionTester):
    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()

        property_json = {"num": 1, "str": "111"}
        r = httpx.post("http://127.0.0.1:8888/cmd", json=property_json)
        print(r)
        if r.status_code == httpx.codes.NOT_FOUND:
            ten_env.stop_test()


class ExtensionTester404NotFound2(ExtensionTester):
    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()

        property_json = {"num": 1, "str": "111"}
        r = httpx.post("http://127.0.0.1:8888/cmd/aaa/123", json=property_json)
        print(r)
        if r.status_code == httpx.codes.NOT_FOUND:
            ten_env.stop_test()


class ExtensionTester400BadRequest(ExtensionTester):
    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()

        property_str = '{num": 1, "str": "111"}'  # not a valid json
        r = httpx.post("http://127.0.0.1:8888/cmd/aaa", content=property_str)
        print(r)
        if r.status_code == httpx.codes.BAD_REQUEST:
            ten_env.stop_test()


def test_4xx():
    tester_404_1 = ExtensionTester404NotFound1()
    tester_404_1.add_addon_base_dir(
        str(Path(__file__).resolve().parent.parent))
    tester_404_1.set_test_mode_single("http_server_python")
    tester_404_1.run()

    tester_404_2 = ExtensionTester404NotFound2()
    tester_404_2.add_addon_base_dir(
        str(Path(__file__).resolve().parent.parent))
    tester_404_2.set_test_mode_single("http_server_python")
    tester_404_2.run()

    tester_400 = ExtensionTester400BadRequest()
    tester_400.add_addon_base_dir(str(Path(__file__).resolve().parent.parent))
    tester_400.set_test_mode_single("http_server_python")
    tester_400.run()
