from ten import (
    Extension,
    TenEnv,
    Cmd,
    StatusCode,
    CmdResult,
)
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from functools import partial


class HTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, ten: TenEnv, *args, directory=None, **kwargs):
        ten.log_debug(f"new handler: {directory} {args} {kwargs}")
        self.ten = ten
        super().__init__(*args, **kwargs)

    def do_POST(self):
        self.ten.log_debug(f"post request incoming {self.path}")
        if self.path == "/cmd":
            try:
                content_length = int(self.headers["Content-Length"])
                input = self.rfile.read(content_length).decode("utf-8")
                self.ten.log_info(f"incoming request {input}")

                # processing by send_cmd
                cmd_result_event = threading.Event()
                cmd_result: CmdResult
                def cmd_callback(_, result):
                    nonlocal cmd_result_event
                    nonlocal cmd_result
                    cmd_result = result
                    self.ten.log_info("cmd callback result: {}".format(cmd_result.to_json()))
                    cmd_result_event.set()

                self.ten.send_cmd(Cmd.create_from_json(input),cmd_callback)
                event_got = cmd_result_event.wait(timeout=5)

                # return response
                if not event_got:  # timeout
                    self.send_response_only(504)
                    self.end_headers()
                    return
                self.send_response(200 if cmd_result.get_status_code() == StatusCode.OK else 502)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(cmd_result.to_json().encode(encoding='utf_8'))
            except Exception as e:
                self.ten.log_warn("failed to handle request, err {}".format(e))
                self.send_response_only(500)
                self.end_headers()
        else:
            self.ten.log_warn(f"invalid path: {self.path}")
            self.send_response_only(404)
            self.end_headers()


class HTTPServerExtension(Extension):
    def __init__(self, name: str):
        super().__init__(name)
        self.listen_addr = "127.0.0.1"
        self.listen_port = 8888
        self.cmd_white_list = None
        self.server = None
        self.thread = None

    def on_start(self, ten: TenEnv):
        self.listen_addr = ten.get_property_string("listen_addr")
        self.listen_port = ten.get_property_int("listen_port")
        """
            white_list = ten.get_property_string("cmd_white_list")
            if len(white_list) > 0:
                self.cmd_white_list = white_list.split(",")
        """

        ten.log_info(
            f"on_start {self.listen_addr}:{self.listen_port}, {self.cmd_white_list}"
        )

        self.server = HTTPServer(
            (self.listen_addr, self.listen_port), partial(HTTPHandler, ten)
        )
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.start()

        ten.on_start_done()

    def on_stop(self, ten: TenEnv):
        self.server.shutdown()
        self.thread.join()
        ten.on_stop_done()

    def on_cmd(self, ten: TenEnv, cmd: Cmd):
        cmd_name = cmd.get_name()
        ten.log_info("on_cmd {cmd_name}")
        cmd_result = CmdResult.create(StatusCode.OK)
        ten.return_result(cmd_result, cmd)
