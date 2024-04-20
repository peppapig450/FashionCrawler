import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from jinja2 import Environment, FileSystemLoader


class RenderAndServe(HTTPServer):
    def __init__(
        self,
        context,
        template_path="fashioncrawler/resources/templates",
        template_name="base_template.html.j2",
        server_address=("localhost", 8000),
    ) -> None:
        self.template_path = template_path
        self.template_name = template_name
        self.server_address = server_address
        self.env = Environment(loader=FileSystemLoader(self.template_path))
        self.template = self.env.get_template(self.template_name)
        self.context = context

        super().__init__(self.server_address, MyHandler)


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            # TODO: figure out how to fix the type
            rendered_html = self.server.template.render(
                **self.server.context
            )
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rendered_html.encode("utf-8"))
        else:
            self.send_error(404, "File not found")


def render_and_serve(context, **kwargs):
    """Renders a Jinja2 template and serves it over an HTTP server.

    Args:
        context (dict): The context data to pass to the template.

    Keyword Args:
        template_path (str, optional): The path to the template directory. Defaults to "fashioncrawler/resources/templates".
        template_name (str, optional): The name of the template to render. Defaults to "base_template.html.j2".
        server_address (tuple, optional): The address for the HTTP server. Defaults to ("localhost", 8000).
    """
    server = RenderAndServe(context, **kwargs)
    try:
        print(
            f"Server running at http://{server.server_address[0]}:{server.server_address[1]}/"
        )
        server.serve_forever()
        os.popen(f"open {server.server_address}")
    except KeyboardInterrupt:
        print("^C Received, shutting down server")
        server.server_close()
