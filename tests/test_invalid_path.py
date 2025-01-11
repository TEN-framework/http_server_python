#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
from pathlib import Path
from typing import Optional
from ten import (
    ExtensionTester,
    TenEnvTester,
    Cmd,
    CmdResult,
    StatusCode,
    TenError,
)
import httpx


class ExtensionTesterInvalidPathCase1(ExtensionTester):
    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()

        property_json = {"num": 1, "str": "111"}
        r = httpx.post("http://127.0.0.1:8888/cmd", json=property_json)
        print(r)
        if r.status_code == httpx.codes.NOT_FOUND:
            ten_env.stop_test()


class ExtensionTesterInvalidPathCase2(ExtensionTester):
    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()

        property_json = {"num": 1, "str": "111"}
        r = httpx.post("http://127.0.0.1:8888/cmd/aaa/123", json=property_json)
        print(r)
        if r.status_code == httpx.codes.NOT_FOUND:
            ten_env.stop_test()


def test_invalid_path():
    tester = ExtensionTesterInvalidPathCase1()
    tester.add_addon_base_dir(str(Path(__file__).resolve().parent.parent))
    tester.set_test_mode_single("http_server_python")
    tester.run()

    tester2 = ExtensionTesterInvalidPathCase2()
    tester2.add_addon_base_dir(str(Path(__file__).resolve().parent.parent))
    tester2.set_test_mode_single("http_server_python")
    tester2.run()
