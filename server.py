#!/usr/bin/env python
# -*- conding:utf-8 -*-
from http.server import HTTPServer, BaseHTTPRequestHandler
import re,time,os,base64
import json,requests
from urllib.parse import unquote

host = ('0.0.0.0', 9001)
length=1000
key="XXX"

def send_to_wecom(text):
    if len(text)>length:
        while True:
            cutA = text[:length]
            cutB = text[length:]
            send_to_wecom1(cutA)
            if len(cutB)>length:
                text = cutB
            else:
                send_to_wecom1(cutB)
                break
    else:
        send_to_wecom1(text)    
        
def send_to_wecom1(text,wecom_touid='@all'):
    get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=XXXX&corpsecret=XXXXX"
    response = requests.get(get_token_url).content
    access_token = json.loads(response).get('access_token')
    if access_token and len(access_token) > 0:
        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        data = {
            "touser":wecom_touid,
            "agentid":XXXX,
            "msgtype":"text",
            "text":{
                "content":text
            },
            "duplicate_check_interval":600
        }
        response = requests.post(send_msg_url,data=json.dumps(data)).content
        return response
    else:
        return False

class Resquest(BaseHTTPRequestHandler):
    def handler(self):
        print("data:", self.rfile.readline().decode())
        self.wfile.write(self.rfile.readline())
        
    def do_GET(self):
        if (key in self.path) != True :
            data = '''<script>window.location.href='https://www.baidu.com';</script>'''
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(data.encode())
            return
        temp = re.search('text=(.*?)$',self.path)
        if(temp==None):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            str1="error:text is empty"
            self.wfile.write(str1.encode())
            return
        try:
            text=base64.b64decode(temp.group(1))
            print(text.decode('utf8'))
            send_to_wecom(text.decode('utf8'))
        except:
            text=unquote(temp.group(1),'utf-8')
            print(text)
            send_to_wecom(text)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.end_headers()
        str1="success:"
        try:
            self.wfile.write(str1.encode()+text)
        except:
            self.wfile.write(str1.encode()+text.encode())

    def do_POST(self):
        if (key in self.path) != True :
            data = '''<script>window.location.href='https://www.baidu.com';</script>'''
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(data.encode())
            return
        if(self.headers['content-length']==None):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            str1="error:POST data is empty"
            self.wfile.write(str1.encode())
            return            
        req_datas = self.rfile.read(int(self.headers['content-length']))
        req_datas = req_datas.decode()
        temp =  re.search('text=(.*?)$',req_datas)
        if(temp==None):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            str1="error:text is empty"
            self.wfile.write(str1.encode())
            return
        try:
            text=base64.b64decode(temp.group(1))
            print(text.decode('utf8'))
            send_to_wecom(text.decode('utf8'))
        except:
            text=unquote(temp.group(1),'utf-8')
            print(text)
            send_to_wecom(text)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.end_headers()
        str1="success:"
        try:
            self.wfile.write(str1.encode()+text)
        except:
            self.wfile.write(str1.encode()+text.encode())

if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
