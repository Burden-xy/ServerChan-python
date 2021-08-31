#!/usr/bin/env python
# -*- conding:utf-8 -*-
from http.server import HTTPServer, BaseHTTPRequestHandler
import re,time,os,base64
import json,requests
from urllib.parse import unquote
from urllib import parse
from socketserver  import ThreadingMixIn

#监听IP、端口
host = ('0.0.0.0', 9001)
#自动分段长度
length=1000
#企业微信应用key
botskey={"default":[企业ID1,Secret1,AgentID1],"bot2":[企业ID2,Secret2,AgentID2]}
#接口访问key
key=""
#返回报文格式
result={"result":"","text":"","botID":""}

#自动分段
def send_to_wecom(text,botID): 
    if len(text)>length:
        while True:
            cutA = text[:length]
            cutB = text[length:]
            send_to_wecom1(cutA,botID)
            if len(cutB)>length:
                text = cutB
            else:
                send_to_wecom1(cutB,botID)
                break
    else:
        send_to_wecom1(text,botID)    

#发送消息        
def send_to_wecom1(text,botID,wecom_touid='@all'): 
    get_token_url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={botskey[botID][0]}&corpsecret={botskey[botID][1]}"
    response = requests.get(get_token_url).content
    access_token = json.loads(response).get('access_token')
    if access_token and len(access_token) > 0:
        send_msg_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        data = {
            "touser":wecom_touid,
            "agentid":botskey[botID][2],
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
    def do_GET(self):
        #验证访问KEY
        if (key in self.path) != True :
            data = '''<script>window.location.href='https://www.baidu.com';</script>'''
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(data.encode())
            return
        #获取botID
        path= parse.urlparse(self.path)
        query=parse.parse_qs(path.query)
        if("botID" in query) == True:
            botID = query["botID"][0]
            if(botID in botskey) == False:
                botID = "default" 
        else:
            botID = "default"
        #判断发送内容是否为空
        if("text" in query) == False:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            result={"result":"error! text is empty","text":"","botID":""}
            self.wfile.write(json.dumps(result).encode())
            return
        temp = query["text"][0].replace(" ","+")
        #使用base64及URL编码方式解码并发送
        try:
            text=base64.b64decode(temp).decode('utf8')
            print(text)
            send_to_wecom(text,botID)
        except:
            text=unquote(temp,'utf-8')
            print(text)
            send_to_wecom(text,botID)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        result={"result":"success","text":text,"botID":botID}
        self.wfile.write(json.dumps(result).encode())

    def do_POST(self):
        #验证访问KEY
        if (key in self.path) != True :
            data = '''<script>window.location.href='https://www.baidu.com';</script>'''
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(data.encode())
            return
        #获取botID
        path= parse.urlparse(self.path)
        query=parse.parse_qs(path.query)
        if("botID" in query) == True:
            botID = query["botID"][0]
            if(botID in botskey) == False:
                botID = "default" 
        else:
            botID = "default"
        #判断body是否为空
        if(self.headers['content-length']==None):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            result={"result":"error! POST data is empty","text":"","botID":""}
            self.wfile.write(json.dumps(result).encode())
            self.wfile.write(str1.encode())
            return            
        req_datas = self.rfile.read(int(self.headers['content-length']))
        req_datas = req_datas.decode()
        temp =  re.search('text=(.*?)$',req_datas)
        #判断发送内容是否为空
        if(temp==None):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            result={"result":"error! text is empty","text":"","botID":""}
            self.wfile.write(json.dumps(result).encode())
            return
        #使用base64及URL编码方式解码并发送
        try:
            text=base64.b64decode(temp.group(1)).decode('utf8')
            print(text)
            send_to_wecom(text,botID)
        except:
            text=unquote(temp.group(1),'utf-8')
            print(text)
            send_to_wecom(text,botID)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        result={"result":"success","text":text,"botID":botID}
        self.wfile.write(json.dumps(result).encode())

#多线程，解决拒绝服务漏洞            
class ThreadingHttpServer (ThreadingMixIn,HTTPServer):
    pass
    
if __name__ == '__main__':
    server = ThreadingHttpServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
    server.server_close()
