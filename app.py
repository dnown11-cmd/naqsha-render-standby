import os,json,time,urllib.request,urllib.error
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
PRIMARY="https://steep-hill-80b3daira.dnown11.workers.dev"
ALLOWED=("/mcp","/.well-known/","/authorize","/token","/register","/oauth/")
HOP={"host","connection","transfer-encoding","content-length","keep-alive","proxy-authenticate","proxy-authorization","te","trailer","upgrade","cf-connecting-ip","cf-ray"}
class Handler(BaseHTTPRequestHandler):
 protocol_version="HTTP/1.0"
 def respond(self,code,obj):
  b=json.dumps(obj).encode();self.send_response(code);self.send_header("Content-Type","application/json");self.send_header("Content-Length",str(len(b)));self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(b)
 def do_GET(self):self.handle_request()
 def do_POST(self):self.handle_request()
 def do_OPTIONS(self):self.handle_request()
 def handle_request(self):
  if self.path.split("?")[0] in ("/","/healthz","/primary-status"):
   if self.path.split("?")[0]=="/healthz":return self.respond(200,{"service":"naqsha-render-gateway","alive":True,"gateway":True})
   try:
    with urllib.request.urlopen(PRIMARY+"/.well-known/oauth-authorization-server",timeout=9) as r:online=r.status==200
   except Exception:online=False
   return self.respond(200,{"service":"naqsha-render-gateway","primary_reachable":online,"independent_mcp":False,"gateway":True})
  if not any(self.path.split("?")[0]==a or (a.endswith("/") and self.path.startswith(a)) for a in ALLOWED):return self.respond(404,{"error":"not_found"})
  try:
   length=int(self.headers.get("Content-Length","0"))
   if length>10485760:return self.respond(413,{"error":"body_too_large"})
   body=self.rfile.read(length) if length else None
   headers={k:v for k,v in self.headers.items() if k.lower() not in HOP}
   headers["Host"]="steep-hill-80b3daira.dnown11.workers.dev"
   req=urllib.request.Request(PRIMARY+self.path,data=body,headers=headers,method=self.command)
   try:r=urllib.request.urlopen(req,timeout=60)
   except urllib.error.HTTPError as e:r=e
   with r:
    self.send_response(r.status)
    for k,v in r.headers.items():
     if k.lower() not in HOP and k.lower() not in ("content-encoding",):self.send_header(k,v)
    self.send_header("Cache-Control","no-store")
    self.end_headers()
    while True:
     chunk=r.read(16384)
     if not chunk:break
     self.wfile.write(chunk);self.wfile.flush()
  except (BrokenPipeError,ConnectionResetError):pass
  except Exception:return self.respond(502,{"error":"upstream_unavailable"})
 def log_message(self,*args):pass
if __name__=="__main__":
 ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT","10000"))),Handler).serve_forever()
