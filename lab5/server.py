from http.server import BaseHTTPRequestHandler, HTTPServer


class RequestHandler(BaseHTTPRequestHandler):
    @staticmethod
    def get_path(page_name: str):
        return f'./webpage/{page_name}'

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        page = self.path[1:]
        if page == "":
            page = 'index.html'

        path = RequestHandler.get_path(page)

        try:
            with open(path, "rb") as f:
                self.wfile.write(f.read())
        except FileNotFoundError:
            self.send_error(404, "Page not found :(")


def main():
    hostname = "localhost"
    port = 1234

    server = HTTPServer((hostname, port), RequestHandler)
    print(f"Listening at: http://{hostname}:{port}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()


if __name__ == "__main__":        
    main()