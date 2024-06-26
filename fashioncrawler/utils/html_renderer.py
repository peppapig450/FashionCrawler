import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from jinja2 import Environment, FileSystemLoader


# TODO: Render html in io_utils and then serve it here.
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
            rendered_html = self.server.template.render(**self.server.context)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rendered_html.encode("utf-8"))
        elif self.path.endswith(".css"):
            css_file_path = self.server.template_path + "/" + self.path[1:]
            if os.path.exists(css_file_path):
                with open(css_file_path, "rb") as file:
                    self.send_response(200)
                    self.send_header("Content-type", "text/css")
                    self.end_headers()
                    self.wfile.write(file.read())

            else:
                self.send_error(404, "File not found")
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
    return server
