import json
import struct
import socketserver


class Server(socketserver.BaseRequestHandler):

    client_conn_dict = {}
    manage_conn_dict = {}

    code = {
        "100": "The administrator requested to join the link",
        "200": "Client Requested Join Link",
        "300": "The management side requests to view all clients",
        "400": "The management side requests to link the client",
        "500": "The management side tries to send a message to the client",
        "600": "The client tried to send a message to the manager",
        "700": "Tell the management side that the client has been disconnected",
    }

    def handle(self) -> None:

        while 1:
            try:
                recv_message = self.recv_message(1024)
                if not recv_message:
                    break

                if recv_message["code"] == "100":
                    self.add_manage_conn()

                elif recv_message["code"] == "200":
                    self.add_client_conn()

                elif recv_message["code"] == "300":
                    self.get_all_client()

                elif recv_message["code"] == "400":
                    self.manage_connection_client(recv_message["data"])

                elif recv_message["code"] == "500":
                    self.send_command_to_client(recv_message["data"])

                elif recv_message["code"] == "600":
                    self.send_result_to_manage(recv_message["data"])

            except Exception:
                break

        self.remove_current_conn()

    def get_ip_port_string(self):
        return self.client_address[0] + ":" + str(self.client_address[1])

    def add_manage_conn(self):
        key = self.get_ip_port_string()
        __class__.manage_conn_dict[key] = {
            "conn": self.request,
            "client": None,
        }

        self.send_message(code="101", data="connected successfully", error="")

    def add_client_conn(self):
        key = self.get_ip_port_string()
        __class__.client_conn_dict[key] = {
            "conn": self.request,
        }

        self.send_message(code="201", data="connected successfully", error="")

    def get_all_client(self):
        self.send_message(
            code="301", data=list(__class__.client_conn_dict.keys()), error="")

    def manage_connection_client(self, data):
        connection_client_index = int(data)

        if connection_client_index > len(__class__.client_conn_dict):
            self.send_message(
                code="402", data="", error="without this client")
            return

        connection_client_key = list(__class__.client_conn_dict.keys())[
            connection_client_index - 1]

        __class__.manage_conn_dict[self.get_ip_port_string(
        )]["client"] = __class__.client_conn_dict[connection_client_key]["conn"]

        self.send_message(
            code="401", data=connection_client_key, error="")

    def remove_current_conn(self):
        print("%s close connect" % self.client_address[0])

        self.request.close()
        current_conn_key = self.get_ip_port_string()

        if current_conn_key in __class__.client_conn_dict:
            del __class__.client_conn_dict[current_conn_key]

            for manage_key, manage_value in __class__.manage_conn_dict.items():
                if manage_value["client"] == current_conn_key:
                    manage_conn = manage_value["conn"]
                    __class__.manage_conn_dict[manage_key]["client"] = None
                    self.send_message(code=700, data="The client has disconnected",
                                      error="", conn=manage_conn)
                    break

        if current_conn_key in __class__.manage_conn_dict:
            del __class__.manage_conn_dict[current_conn_key]

    def send_command_to_client(self, data):

        client_conn = __class__.manage_conn_dict[data["manage"]].get("client")

        if client_conn:

            self.send_message(
                code=500, data=data, error="", conn=client_conn
            )

            return

        self.send_message(
            code=502, data="", error="Please link the client"
        )

    def send_result_to_manage(self, data):

        manage_conn = __class__.manage_conn_dict[data["manage"]]["conn"]

        self.send_message(
            code=600, data=data, error="", conn=manage_conn
        )

    def send_message(self, code: int, data: str, error: str, conn=None) -> None:

        if conn is None:
            conn = self.request

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

        conn.send(request_data)

    def recv_message(self, recv_size: int) -> str:

        response_headers_length = struct.unpack("i", self.request.recv(4))[0]

        response_headers = json.loads(
            self.request.recv(response_headers_length).decode("utf-8"))

        response_body_length = response_headers["data_length"]

        response_body = b""
        current_recv_response_body_length = 0

        while current_recv_response_body_length < response_body_length:
            current_recv_response = self.request.recv(recv_size)
            response_body += current_recv_response
            current_recv_response_body_length += len(current_recv_response)

        return json.loads(response_body.decode("utf-8"))


if __name__ == "__main__":
    socketserver.ThreadingTCPServer
    server = socketserver.ThreadingTCPServer(("localhost", 8080), Server)
    server.serve_forever()
