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
import threading


class ExtensionTester5xx(ExtensionTester):
    def __init__(self):
        super().__init__()
        self.thread = None

    def on_cmd(self, ten_env: TenEnvTester, cmd: Cmd) -> None:
        print(f"on_cmd name {cmd.get_name()}")
        ten_env.return_result(CmdResult.create(StatusCode.ERROR), cmd)

    def on_start(self, ten_env: TenEnvTester) -> None:
        self.thread = threading.Thread(
            target=self._async_test, args=[ten_env])
        self.thread.start()

        ten_env.on_start_done()

    def _async_test(self, ten_env: TenEnvTester) -> None:
        property_json = {"num": 1, "str": "111"}
        r = httpx.post("http://127.0.0.1:8888/cmd/abc",
                       json=property_json, timeout=5)
        print(r)

        if r.status_code >= 500:
            ten_env.stop_test()


def test_5xx():
    tester = ExtensionTester5xx()
    tester.set_test_mode_single("http_server_python")
    tester.run()
