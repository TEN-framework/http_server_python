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


class ExtensionTesterTimeout(ExtensionTester):
    def on_cmd(self, ten_env: TenEnvTester, cmd: Cmd) -> None:
        ten_env.log_debug(f"on_cmd name {cmd.get_name()}")
        # NOTE: DON'T return result so that timeout will occur
        # ten_env.return_result(CmdResult.create(StatusCode.OK), cmd)
        pass

    def on_start(self, ten_env: TenEnvTester) -> None:
        ten_env.on_start_done()

        property_json = {"num": 1, "str": "111"}
        r = httpx.post("http://127.0.0.1:8888/cmd/abc",
                       json=property_json, timeout=10)
        ten_env.log_debug(f"{r}")
        if r.status_code == httpx.codes.GATEWAY_TIMEOUT:
            ten_env.stop_test()


def test_timeout():
    tester = ExtensionTesterTimeout()
    tester.set_test_mode_single("http_server_python")
    tester.run()
