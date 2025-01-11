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
        self.event = threading.Event()

    def on_cmd(self, ten_env: TenEnvTester, cmd: Cmd) -> None:
        print(f"on_cmd name {cmd.get_name()}")
        ten_env.return_result(CmdResult.create(StatusCode.OK), cmd)

        event_got = self.event.wait(timeout=5)
        if not event_got:  # timeout
            print("test error")
        else:
            ten_env.stop_test()

    def on_start(self, ten_env: TenEnvTester) -> None:

        self.thread = threading.Thread(target=self._async_request, args=[])
        self.thread.start()

        ten_env.on_start_done()

    def _async_request(self) -> None:
        property_json = {"num": 1, "str": "111"}
        r = httpx.post("http://127.0.0.1:8899/cmd/abc",
                       json=property_json, timeout=5)
        print(r)

        if r.status_code == httpx.codes.OK:
            # TODO: stop test directly once albe to call it in separate thread
            #   ten_env.stop_test()
            self.event.set()


def test_property():

    # change port
    property_json_1 = '{"listen_port":8899}'
    tester_1 = ExtensionTesterSetProperty()
    tester_1.add_addon_base_dir(str(Path(__file__).resolve().parent.parent))
    tester_1.set_test_mode_single("http_server_python", property_json_1)
    tester_1.run()

    # change port with localhost
    property_json_2 = '{"listen_addr":"127.0.0.1","listen_port":8899}'
    tester_2 = ExtensionTesterSetProperty()
    tester_2.add_addon_base_dir(str(Path(__file__).resolve().parent.parent))
    tester_2.set_test_mode_single("http_server_python", property_json_2)
    tester_2.run()

    # change port with any addr
    property_json_3 = '{"listen_addr":"0.0.0.0","listen_port":8899}'
    tester_3 = ExtensionTesterSetProperty()
    tester_3.add_addon_base_dir(str(Path(__file__).resolve().parent.parent))
    tester_3.set_test_mode_single("http_server_python", property_json_3)
    tester_3.run()
