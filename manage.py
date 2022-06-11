import json
import struct

from socket import *


class Manage:
    echo = "[no connection] "

    @property
    def help(self) -> str:
        return """
        ==== help menu ===

        help: show help menu
        show: show all client
        [1-n]: select client
        exit: exit
        """

    def __init__(self):
        self.socket = socket()

    def connect(self, host: str, port: int) -> None:
        self.socket.connect((host, port))

    def run(self) -> None:
        # join management connection
        self.send_message(code=100, data="", error="")
        print(self.recv_message(1024))

        while 1:
            command = input(self.echo).strip()

            if not command:
                continue

            if command == "help":
                print(self.help)
                continue

            if command == "exit":
                break

            if command == "show":
                self.send_message(code=300, data="", error="")

            elif command.isdigit():
                self.send_message(code=400, data=command, error="")

            else:
                self.send_message(code=500, data={
                    "manage": self.get_ip_port_string(),
                    "command": command,
                }, error="")

            self.response_handler(self.recv_message(1024))

    def response_handler(self, response_data: dict) -> None:
        if response_data["code"] == "301":
            self.show_all_client(response_data["data"])

        elif response_data["code"] == "401":
            self.echo = f"[{response_data['data']}] "

        elif response_data["code"] == "402":
            print(response_data["error"])

        elif response_data["code"] == "502":
            print(response_data["error"])

        elif response_data["code"] == "600":
            print(response_data["data"]["result"])

        elif response_data["code"] == "700":
            print(response_data["data"])
            self.echo = __class__.echo

    def show_all_client(self, data) -> None:
        if not data:
            print("No client")
            return

        for i in range(len(data)):
            print(f"- ${i + 1} {data[i]}")

    def get_ip_port_string(self):
        sockname = self.socket.getsockname()
        return sockname[0] + ":" + str(sockname[1])

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
    manage = Manage()
    manage.connect("localhost", 8080)
    manage.run()
