import asyncio
from aiohttp import web
import json

from ten_runtime import (
    AsyncExtension,
    AsyncTenEnv,
    Cmd,
    Data,
    StatusCode,
    CmdResult,
)


class HTTPServerExtension(AsyncExtension):
    def __init__(self, name: str):
        super().__init__(name)
        self.listen_addr: str = "127.0.0.1"
        self.listen_port: int = 8888

        self.ten_env: AsyncTenEnv = None

        # http server instances
        self.app = web.Application()
        self.runner = None

    # POST /cmd/{cmd_name}
    async def handle_post_cmd(self, request):
        ten_env = self.ten_env

        try:
            cmd_name = request.match_info.get("cmd_name")

            req_json = await request.json()
            input_json = json.dumps(req_json, ensure_ascii=False)

            ten_env.log_debug(
                f"process incoming request {request.method} {request.path} {input_json}"
            )

            cmd = Cmd.create(cmd_name)
            cmd.set_property_from_json("", input_json)
            [cmd_result, _] = await asyncio.wait_for(ten_env.send_cmd(cmd), 5.0)

            # return response
            status = 200 if cmd_result.get_status_code() == StatusCode.OK else 502
            response, err = cmd_result.get_property_to_json("")
            if err is not None:
                raise err
            return web.json_response(response, status=status)
        except json.JSONDecodeError:
            return web.Response(status=400)
        except asyncio.TimeoutError:
            return web.Response(status=504)
        except Exception as e:
            ten_env.log_warn(
                "failed to handle request with unknown exception, err {}".format(e)
            )
            return web.Response(status=500)

    # POST /data/{data_name}
    async def handle_post_data(self, request):
        ten_env = self.ten_env

        try:
            data_name = request.match_info.get("data_name")

            req_json = await request.json()
            input_json = json.dumps(req_json, ensure_ascii=False)

            ten_env.log_debug(
                f"process incoming request {request.method} {request.path} {input_json}"
            )

            data = Data.create(data_name)
            data.set_property_from_json("", input_json)
            await ten_env.send_data(data)

            # return response
            return web.Response(status=200)
        except json.JSONDecodeError:
            return web.Response(status=400)
        except Exception as e:
            ten_env.log_warn(
                "failed to handle request with unknown exception, err {}".format(e)
            )
            return web.Response(status=500)

    async def on_start(self, ten_env: AsyncTenEnv):
        if await ten_env.is_property_exist("listen_addr"):
            self.listen_addr, _ = await ten_env.get_property_string("listen_addr")
        if await ten_env.is_property_exist("listen_port"):
            self.listen_port, _ = await ten_env.get_property_int("listen_port")
        self.ten_env = ten_env

        ten_env.log_info(
            f"http server listening on {self.listen_addr}:{self.listen_port}"
        )

        self.app.router.add_post("/cmd/{cmd_name}", self.handle_post_cmd)
        self.app.router.add_post("/data/{data_name}", self.handle_post_data)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.listen_addr, self.listen_port)
        await site.start()

    async def on_stop(self, _: AsyncTenEnv):
        await self.runner.cleanup()
        self.ten_env = None

    async def on_cmd(self, ten_env: AsyncTenEnv, cmd: Cmd):
        cmd_name = cmd.get_name()
        ten_env.log_debug(f"on_cmd {cmd_name}")
        ten_env.return_result(CmdResult.create(StatusCode.OK, cmd))
