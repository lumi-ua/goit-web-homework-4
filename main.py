from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
import logging
import json
from threading import Thread
from datetime import datetime

BASE_DIR = pathlib.Path()

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000



def send_data_to_socket(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(data, (SERVER_IP, SERVER_PORT))
    client_socket.close()
     


class HttpHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        send_data_to_socket(data)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:    
                self.send_html_file('error.html', 404)

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

# def save_data_to_json(data):
#         data_parse = urllib.parse.unquote_plus(data.decode())
#         data_parse = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
#         with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
#             json.dump(data_parse, fd, ensure_ascii=False)


def save_data_to_json(data):
    global BASE_DIR
    save_data = {}
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    data_parse = urllib.parse.unquote_plus(data.decode())
    try:
        data_parse = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        if pathlib.Path.exists(pathlib.Path('storage/data.json')):
            with open(BASE_DIR.joinpath('storage/data.json'), 'r', encoding="utf-8") as fd:
                save_data = json.load(fd)


        dct = {current_datetime:data_parse}
        save_data.update(dct)
        with open(BASE_DIR.joinpath('storage/data.json'), 'w', encoding='utf-8') as fd:
            json.dump(save_data, fd, ensure_ascii=False)
    except ValueError as err:
        logging.error(f'Field parse data {data_parse} with error {err}')
    except OSError as err:
        logging.error(f'Field write data {data_parse} with error {err}')




def run_socket_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#когда к нам постучались мы с ним работаем, остальных игнорируем
    server = ip, port
    server_socket.bind(server) #bind привязывает, в данном случае хост и порт 
    logging.info('Socket started.')
    try:
        while True:
            data, address = server_socket.recvfrom(1024)
            save_data_to_json(data)

    except KeyboardInterrupt:
        logging.info('Socket server stopped')
        
    finally:
        server_socket.close()


if __name__ == '__main__':
    # run()
    # run_socket_server(SERVER_IP, SERVER_PORT)

    logging.basicConfig(level=logging.INFO, format='%(threadName)s %(message)s')
    thread_server = Thread(target=run)
    thread_server.start()
    
    thread_socket_server = Thread(target=run_socket_server(SERVER_IP, SERVER_PORT))
    thread_socket_server.start()

    #thread_server.join()
    #thread_socket_server.join()
