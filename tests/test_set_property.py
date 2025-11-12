#
# Copyright © 2025 Agora
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0, with certain conditions.
# Refer to the "LICENSE" file in the root directory for more information.
#
from pathlib import Path
from ten_runtime import (
    ExtensionTester,
    TenEnvTester,
    Cmd,
    CmdResult,
    StatusCode,
)
import httpx
import threading


class ExtensionTesterSetProperty(ExtensionTester):
    def __init__(self):
        super().__init__()
        self.thread = None

    def on_cmd(self, ten_env: TenEnvTester, cmd: Cmd) -> None:
        ten_env.log_debug(f"on_cmd name {cmd.get_name()}")
        assert cmd.get_name() == "http_cmd"
        ten_env.return_result(CmdResult.create(StatusCode.OK, cmd))

    def on_start(self, ten_env: TenEnvTester) -> None:

        self.thread = threading.Thread(target=self._async_test, args=[ten_env])
        self.thread.start()

        ten_env.on_start_done()

    def _async_test(self, ten_env: TenEnvTester) -> None:
        request_body = {"name": "abc", "payload": {"num": 1, "str": "111"}}
        r = httpx.post("http://127.0.0.1:8899/cmd", json=request_body, timeout=5)
        ten_env.log_debug(f"{r}")

        if r.status_code == httpx.codes.OK:
            ten_env.stop_test()


def test_set_property():

    # change port
    property_json_1 = '{"listen_port":8899}'
    tester_1 = ExtensionTesterSetProperty()
    tester_1.set_test_mode_single("http_server_python", property_json_1)
    tester_1.run()

    # change port with localhost
    property_json_2 = '{"listen_addr":"127.0.0.1","listen_port":8899}'
    tester_2 = ExtensionTesterSetProperty()
    tester_2.set_test_mode_single("http_server_python", property_json_2)
    tester_2.run()

    # change port with any addr
    property_json_3 = '{"listen_addr":"0.0.0.0","listen_port":8899}'
    tester_3 = ExtensionTesterSetProperty()
    tester_3.set_test_mode_single("http_server_python", property_json_3)
    tester_3.run()
