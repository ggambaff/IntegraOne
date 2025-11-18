from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Environment, FileSystemLoader
import os
import mimetypes  # Asegurate de tener esta importación al inicio del archivo

class JinjaRequestHandler(BaseHTTPRequestHandler):
    def custom_static_url_for(self,filename):
        return f"/static/{filename}"
    def do_GET(self):
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        static_path = os.path.join(os.path.dirname(__file__), 'static')

        # ✅ SERVIR ARCHIVOS ESTÁTICOS
        if self.path.startswith('/static/'):
            file_path = os.path.join(static_path, self.path[len('/static/'):])
            if os.path.isfile(file_path):
                self.send_response(200)
                mime_type, _ = mimetypes.guess_type(file_path)
                self.send_header('Content-type', mime_type or 'application/octet-stream')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Archivo no encontrado")
            return

        # ✅ RENDERIZAR PLANTILLA JINJA2
        env = Environment(loader=FileSystemLoader(template_path))
        env.globals['url_for'] = self.custom_static_url_for
        try:
            template = env.get_template('index.xml')
            html = template.render({
                'titulo': 'In Party',
                'mensaje': '¡Bienvenido al sistema In Party!'
            })
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error al renderizar la plantilla: {e}".encode('utf-8'))

def start_web_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, JinjaRequestHandler)
    print(f"Servidor web activo en http://localhost:{port}")
    httpd.serve_forever()