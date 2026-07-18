import json
import time
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

ADMIN_PASSWORD = "15889340084"  # เปลี่ยนรหัสผ่านแอดมินตามใจชอบ

system_data = {
    "announcement": "ยินดีต้อนรับสู่ HYPER! X SYSTEM ระบบพร้อมใช้งานแล้ว",
    "guest_account_info": {
        "com.garena.msdk.guest_uid": "4234768721",
        "com.garena.msdk.guest_password": "mazdamodsGJCDDRHNHGEXNYLPTTAZ3DQFVBFUT7B1M0QRXNY6PQASVBWOT"
    }
}

ip_request_history = {}
RATE_LIMIT_SECONDS = 2 

def is_rate_limited(ip_address):
    current_time = time.time()
    if ip_address in ip_request_history:
        last_request_time = ip_request_history[ip_address]
        if current_time - last_request_time < RATE_LIMIT_SECONDS:
            return True
    ip_request_history[ip_address] = current_time
    return False

class AdvancedProxyServer(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        if is_rate_limited(self.client_address[0]):
            self._set_headers(429)
            self.wfile.write(json.dumps({"error": "Too Many Requests (กดถี่เกินไป)"}).encode())
            return
        if self.path == "/api/get_system_data" or self.path == "/":
            self._set_headers(200)
            self.wfile.write(json.dumps(system_data).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    def do_POST(self):
        if is_rate_limited(self.client_address[0]):
            self._set_headers(429)
            self.wfile.write(json.dumps({"status": "error", "message": "Slow down! (กรุณารอ 2 วินาที)"}).encode())
            return

        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 50000:
            self._set_headers(413)
            self.wfile.write(json.dumps({"status": "error", "message": "Payload Too Large"}).encode())
            return

        post_data = self.rfile.read(content_length)
        try:
            req_json = json.loads(post_data.decode('utf-8'))
        except:
            self._set_headers(400)
            self.wfile.write(json.dumps({"status": "error", "message": "Invalid JSON"}).encode())
            return

        if self.path == "/api/set_account":
            if "guest_account_info" in req_json:
                system_data["guest_account_info"] = req_json["guest_account_info"]
                self._set_headers(200)
                self.wfile.write(json.dumps({"status": "success"}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"status": "error", "message": "รูปแบบข้อมูลไม่ถูกต้อง"}).encode())

        elif self.path == "/api/admin/update":
            password = req_json.get("password")
            if password != ADMIN_PASSWORD:
                self._set_headers(401)
                self.wfile.write(json.dumps({"status": "error", "message": "รหัสผ่านแอดมินไม่ถูกต้อง"}).encode())
                return
            if "announcement" in req_json:
                system_data["announcement"] = req_json["announcement"]
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "success", "message": "อัปเดตสำเร็จ"}).encode())

def run():
    # ดึงพอร์ตที่ Render กำหนดให้อัตโนมัติ ป้องกันการเปิดไม่ติด
    port = int(os.environ.get("PORT", 20825))
    server_address = ('', port)
    httpd = HTTPServer(server_address, AdvancedProxyServer)
    print(f"[+] Server running on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
