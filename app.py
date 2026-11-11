import os, time, json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PRIMARY = "https://steep-hill-80b3daira.dnown11.workers.dev"
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/healthz", "/primary-status"):
            self.send_error(404)
            return
        if self.path == "/healthz":
            return self.respond(200, {"service":"naqsha-render-standby-monitor","alive":True})
        try:
            req=Request(PRIMARY+"/.well-known/oauth-authorization-server",headers={"User-Agent":"NAQSHA-Standby-Monitor/1.0"})
            with urlopen(req, timeout=8) as r:
                code=r.status
            online=(code==200)
            error=None
        except Exception as e:
            online=False
            error=type(e).__name__
        self.respond(200,{"service":"naqsha-render-standby-monitor","primary_reachable":online,"primary_http_status":200 if online else None,"error":error,"independent_mcp":False,"note":"Monitoring only; phone-dependent MCP is not mirrored"})
    def respond(self,code,data):
        body=json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self,*args): pass

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT","10000"))),Handler).serve_forever()
