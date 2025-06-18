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
    Data,
    CmdResult,
    StatusCode,
)
import httpx
import threading
import math


class ExtensionTesterData(ExtensionTester):
    def __init__(self):
        super().__init__()
        self.thread = None

    def on_data(self, ten_env: TenEnvTester, data: Data) -> None:
        ten_env.log_debug(f"on_data name {data.get_name()}")

        num_val, _ = data.get_property_int("num")
        assert num_val == 1
        str_val, _ = data.get_property_string("str")
        assert str_val == "111"
        unicode_str_val, _ = data.get_property_string("unicode_str")
        assert unicode_str_val == "你好！"
        num_float_val, _ = data.get_property_float("num_float")
        assert math.isclose(num_float_val, -1.5)

    def on_start(self, ten_env: TenEnvTester) -> None:

        self.thread = threading.Thread(target=self._async_test, args=[ten_env])
        self.thread.start()

        ten_env.on_start_done()

    def _async_test(self, ten_env: TenEnvTester) -> None:
        property_json = {
            "num": 1,
            "num_float": -1.5,
            "str": "111",
            "unicode_str": "你好！",
        }

        r = httpx.post("http://127.0.0.1:8888/data/abc", json=property_json, timeout=5)
        ten_env.log_debug(f"{r}")

        if r.status_code == httpx.codes.OK:
            ten_env.stop_test()


def test_data():
    tester = ExtensionTesterData()
    tester.set_test_mode_single("http_server_python")
    tester.run()


if __name__ == "__main__":
    test_data()
