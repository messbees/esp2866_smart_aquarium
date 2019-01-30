#!/usr/bin/env python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import argparse
import logging
from log import init_console_logging
import os
import json
from tinydb import TinyDB, Query
import datetime
#from exceptions import EvolutionServerException

LOGGER = logging.getLogger(__name__)
now = datetime.datetime.now()
last = {'date': '', 'temp': ''}

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(self.data_string)
        print("")
        LOGGER.info("---------------------------------------------------")
        if not (data["version"] == Server.version):
            self.send_response(405)
            self.end_headers()
            return
        action = data["action"]

        # calls after trying to fetch room state
        if (action == "TEST"):
            response = []
            response["text"] = "it works!"
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response))

        if (action == "GET_TEMP"):
            response = []
            response["temp"] = last{"temp"}
            response["date"] = last{"date"}
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response))


    def do_POST(self):
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        data = json.loads(self.data_string)
        print("")
        LOGGER.info("---------------------------------------------------")

        if not (data["version"] == Server.version):
            self.send_response(405)
            self.end_headers()
            return
        action = data["action"]

        if (action == "POST_TEMP"):
            temp = data["temp"]
            last = {'date': now.strftime("%Y-%m-%d %H:%M"), 'temp': temp}
            db.insert(last)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()

if __name__ == "__main__":
    db = TinyDB('temp.json')
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('port', type=int, help='Listening port for HTTP Server')
    parser.add_argument('ip', help='HTTP Server IP')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase output sent to stderr')
    args = parser.parse_args()

    init_console_logging(args.verbose)
    LOGGER.info('Listening on {}:{}'.format(args.ip, args.port))
    HTTPserver = HTTPServer((args.ip, args.port), RequestHandler)
    HTTPserver.serve_forever()