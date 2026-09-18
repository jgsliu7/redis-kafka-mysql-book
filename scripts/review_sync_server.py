#!/usr/bin/env python3
"""审阅页本地同步服务。

用途：0917/ 下的审阅报告页在每次编辑"我的定稿"后自动 POST /sync，
把该页全部条目（定稿/建议稿/原文/选择/备注）落到 0917/finals/<标题>.json。
Claude 只读 finals/ 下的 JSON，用户不需要复制任何内容。

启动：python3 scripts/review_sync_server.py [端口]   （默认 127.0.0.1:8734）
打开：http://127.0.0.1:8734/  （目录列表，点开任意审阅页）
"""
import datetime
import json
import os
import re
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '0917'))
FINALS = os.path.join(ROOT, 'finals')
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8734


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        # 页面可能从 file:// 直接打开，跨源同步必须放行
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        if self.path.split('?')[0] != '/sync':
            self.send_error(404)
            return
        try:
            length = int(self.headers.get('Content-Length') or 0)
            data = json.loads(self.rfile.read(length) or b'{}')
            title = str(data.get('title') or '未命名')
            safe = re.sub(r'[^\w一-鿿.-]+', '_', title)[:60] or '未命名'
            os.makedirs(FINALS, exist_ok=True)
            out = os.path.join(FINALS, safe + '.json')
            tmp = out + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, out)
            n = len(data.get('items') or {})
            with open(os.path.join(FINALS, 'sync.log'), 'a', encoding='utf-8') as f:
                f.write('%s %s items=%d bytes=%d\n'
                        % (datetime.datetime.now().strftime('%F %T'), safe, n, length))
            body = json.dumps({'ok': True, 'items': n}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:  # noqa: BLE001
            self.send_error(400, str(e))

    def log_message(self, fmt, *args):
        sys.stderr.write('%s %s\n' % (self.address_string(), fmt % args))


if __name__ == '__main__':
    os.makedirs(FINALS, exist_ok=True)
    try:
        srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
    except OSError as e:
        print('端口 %d 占用（服务可能已在运行）：%s' % (PORT, e))
        sys.exit(1)
    print('审阅同步服务已启动：http://127.0.0.1:%d/  （服务目录 %s）' % (PORT, ROOT))
    print('定稿落盘目录：%s' % FINALS)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
