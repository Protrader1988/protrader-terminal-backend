import os, time, hmac, hashlib, base64, json, requests
GEMINI_BASE = os.getenv("GEMINI_BASE_URL","https://api.sandbox.gemini.com")

class GeminiClient:
    def __init__(self): 
        self.key=os.getenv("GEMINI_API_KEY",""); self.secret=os.getenv("GEMINI_API_SECRET","").encode(); self.sess=requests.Session()
    def _headers(self, path, payload):
        p64=base64.b64encode(json.dumps(payload).encode()); sig=hmac.new(self.secret,p64,hashlib.sha384).hexdigest()
        return {"Content-Type":"text/plain","X-GEMINI-APIKEY":self.key,"X-GEMINI-PAYLOAD":p64.decode(),"X-GEMINI-SIGNATURE":sig}
    def submit_order(self, side, symbol, qty, order_type="market", price=None):
        sym = symbol.replace("/","").lower()
        path="/v1/order/new"; payload={"request":path,"nonce":str(int(time.time()*1000)),"symbol":sym,"amount":str(qty),"side":side,"type":f"exchange {order_type}"}
        if price is not None: payload["price"]=str(price)
        r=self.sess.post(GEMINI_BASE+path,headers=self._headers(path,payload),timeout=15)
        try:
            resp=r.json()
        except Exception:
            resp={"text":r.text}
        return {"ok": r.ok, "status": r.status_code, "resp": resp}
