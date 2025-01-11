import asyncio
from aiohttp import web
import re

from ten import (
    AsyncExtension,
    AsyncTenEnv,
    Cmd,
    StatusCode,
    CmdResult,
)


class HTTPServerExtension(AsyncExtension):
    def __init__(self, name: str):
        super().__init__(name)
        self.listen_addr = "127.0.0.1"
        self.listen_port = 8888

        self.app = web.Application()
        self.runner = None

    async def handle_post(self, request):
        ten_env = request.app["ten_env"]
        path = request.path
        ten_env.log_debug(f"post request incoming {path}")

        # match path /cmd/<cmd_name>
        match = re.match(r"^/cmd/([^/]+)$", path)
        if match:
            cmd_name = match.group(1)
            try:
                input = await request.text()
                ten_env.log_info(f"incoming request {path} {input}")

                # Directly await the send_cmd function
                cmd = Cmd.create(cmd_name)
                cmd.set_property_from_json("", input)
                cmd_result = await ten_env.send_cmd(cmd)

                # return response
                status = 200 if cmd_result.get_status_code() == StatusCode.OK else 502
                return web.json_response(
                    cmd_result.get_property_to_json(""), status=status
                )
            except asyncio.TimeoutError:
                return web.Response(status=504)
            except Exception as e:
                ten_env.log_warn("failed to handle request, err {}".format(e))
                return web.Response(status=500)
        else:
            ten_env.log_warn(f"invalid path: {path}")
            return web.Response(status=404)

    async def on_start(self, ten_env: AsyncTenEnv):
        if ten_env.is_property_exist("listen_addr"):
            self.listen_addr = ten_env.get_property_string("listen_addr")
        if ten_env.is_property_exist("listen_port"):
            self.listen_port = ten_env.get_property_int("listen_port")

        ten_env.log_info(f"http server listen on {self.listen_addr}:{self.listen_port}")

        self.app["ten_env"] = ten_env
        self.app.router.add_post("/cmd/{cmd_name}", self.handle_post)
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.listen_addr, self.listen_port)
        await site.start()

    async def on_stop(self, ten_env: AsyncTenEnv):
        await self.runner.cleanup()

    async def on_cmd(self, ten_env: AsyncTenEnv, cmd: Cmd):
        cmd_name = cmd.get_name()
        ten_env.log_debug(f"on_cmd {cmd_name}")
        ten_env.return_result(CmdResult.create(StatusCode.OK), cmd)
