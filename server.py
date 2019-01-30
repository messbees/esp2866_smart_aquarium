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
db = TinyDB('temp.json')
last = {'date': '', 'temp': ''}
version = '0.0'

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        request_string = self.rfile.read(int(self.headers.getheader('content-length', 0)))
        LOGGER.debug(request_string)
        request_string = str(request_string)
        data = json.loads(request_string)

        LOGGER.info("---------------------------------------------------")
        if not (data["version"] == version):
            self.send_response(405)
            self.end_headers()
            return
        action = data["action"]

        if (action == "TEST"):
            response = []
            response["text"] = "it works!"
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response))

        elif (action == "GET_TEMP"):
            LOGGER.info("Someone asks for the last temperature value!")
            response = []
            table = db.table('temp')
            last = table.get(doc_id=len(table))
            print(last)
            response["value"] = last["value"]
            response["date"] = last["date"]
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response))

        elif (action == "POST_TEMP"):
            LOGGER.info("ESP2866 says: temperature is {}°С".format(value))
            value = data["value"]
            last = {'date': now.strftime("%Y-%m-%d %H:%M"), 'value': value}
            db.insert(last)
            self.send_response(200)
            self.end_headers()
            LOGGER.info("Value saved.")
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='HTTP Server')
    parser.add_argument('port', type=int, help='Listening port for HTTP Server')
    parser.add_argument('ip', help='HTTP Server IP')
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase output sent to stderr')
    args = parser.parse_args()

    init_console_logging(args.verbose)
    LOGGER.info('Listening on {}:{}'.format(args.ip, args.port))
    HTTPserver = HTTPServer((args.ip, args.port), RequestHandler)
    HTTPserver.serve_forever()
