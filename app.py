import os,json,time,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
START=time.monotonic()
URLS={'cloudflare':'https://steep-hill-80b3daira.dnown11.workers.dev','render':'https://naqsha-mcp-backup-gateway.onrender.com'}
def check():
 out={}
 for name,url in URLS.items():
  try:
   with urllib.request.urlopen(url+'/.well-known/oauth-authorization-server',timeout=8) as r:out[name]={'status':r.status,'ok':r.status==200}
  except Exception as e:out[name]={'ok':False,'error':type(e).__name__}
 return out
def status():return {'server':'naqsha-independent-mcp','independent':True,'phone_required':False,'uptime':int(time.monotonic()-START)}
class Handler(BaseHTTPRequestHandler):
 def sendj(self,n,obj):
  b=json.dumps(obj).encode();self.send_response(n);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_GET(self):
  if self.path in ('/','/healthz'):return self.sendj(200,status())
  return self.sendj(405 if self.path=='/mcp' else 404,{'error':'use POST /mcp'})
 def do_POST(self):
  if self.path!='/mcp':return self.sendj(404,{'error':'not_found'})
  try:
   n=int(self.headers.get('Content-Length','0'))
   if n<1 or n>65536:return self.sendj(413,{'error':'size'})
   q=json.loads(self.rfile.read(n));m=q.get('method');i=q.get('id')
   if m=='notifications/initialized':self.send_response(202);self.end_headers();return
   if m=='initialize':r={'protocolVersion':'2025-03-26','capabilities':{'tools':{}},'serverInfo':{'name':'naqsha-independent-mcp','version':'1.0'}}
   elif m=='ping':r={}
   elif m=='tools/list':r={'tools':[{'name':x,'description':d,'inputSchema':{'type':'object','properties':{}}} for x,d in [('server_status','Independent server status'),('check_public_routes','Read-only public route diagnostics')]]}
   elif m=='tools/call':
    name=q.get('params',{}).get('name')
    if name not in ('server_status','check_public_routes'):return self.sendj(200,{'jsonrpc':'2.0','id':i,'error':{'code':-32602,'message':'Unknown tool'}})
    r={'content':[{'type':'text','text':json.dumps(status() if name=='server_status' else check())}]}
   else:return self.sendj(200,{'jsonrpc':'2.0','id':i,'error':{'code':-32601,'message':'Method not found'}})
   return self.sendj(200,{'jsonrpc':'2.0','id':i,'result':r})
  except Exception:return self.sendj(400,{'error':'bad_request'})
 def log_message(self,*args):pass
if __name__=='__main__':ThreadingHTTPServer(('0.0.0.0',int(os.getenv('PORT','10000'))),Handler).serve_forever()
