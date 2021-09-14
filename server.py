#!/usr/bin/env python
# -*- conding:utf-8 -*-
from http.server import HTTPServer, BaseHTTPRequestHandler
import re,time,os,base64
import json,requests
from urllib.parse import unquote
from urllib import parse
from socketserver  import ThreadingMixIn
from WXBizMsgCrypt3 import WXBizMsgCrypt
import xml.etree.cElementTree as ET
import sys

#监听IP、端口
host = ('0.0.0.0', 9001)
#自动分段长度
length=1000
#企业微信应用key
#可在url中指定botID=botskey的key值的方式来选择向哪个BOT发送信息，第一个botskey的key必须为default，即默认bot，当url中不包含该参数默认使用该bot
botskey={"default":["企业ID","应用key","应用ID"],"应用名称":["企业ID","应用key","应用ID"]}
#接口访问key
key=""
#返回报文格式
result={"result":"","text":"","botID":""}
#企业微信后台上设置参数，用于解密用户发送的消息
#在企微应用后台设置回复API地址为http://IP:PORT/key/respkey的key/,程序根据respkey的key值判断使用哪个bot的解密参数
respkey={"机器人ID":["token","AES KEY","企业ID"],"机器人ID":["token","AES KEY","企业ID"]}

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

#对发送的消息进行处理
def resp(message,bot_id):
    return "发送的消息是："+message+"\nbotID为："+bot_id

#获取botID
def get_botID(agentid):
    for item in botskey.items():
        if (item[1][2]==agentid):
            return item[0]

#获取应答bot            
def get_resp_bot(path):
    for item in respkey.items():
        if (item[0] in path) == True:
            return item[0]
    
class Resquest(BaseHTTPRequestHandler):   
    def do_GET(self):
        #判断key是否正确
        if (key in self.path) != True :
            data = '''<script>window.location.href='https://www.baidu.com';</script>'''
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(data.encode())
            return
        #企微URL验证
        if("msg_signature" in self.path) == True:
            bot=get_resp_bot(self.path)
            wxcpt=WXBizMsgCrypt(respkey[bot][0],respkey[bot][1],respkey[bot][2])
            path= parse.urlparse(self.path)
            query=parse.parse_qs(path.query)
            sVerifyMsgSig = query["msg_signature"][0]
            sVerifyTimeStamp = query["timestamp"][0]
            sVerifyNonce = query["nonce"][0]
            sVerifyEchoStr = query["echostr"][0]
            ret,sEchoStr=wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,sVerifyEchoStr)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(sEchoStr)
            print("[DEBUG]企微URL验证")
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
            print("[DEBUG]GET方式发送消息："+text)
            send_to_wecom(text,botID)
        except:
            text=unquote(temp,'utf-8')
            print("[DEBUG]GET方式发送消息："+text)
            send_to_wecom(text,botID)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        result={"result":"success","text":text,"botID":botID}
        self.wfile.write(json.dumps(result).encode())

    def do_POST(self):
        #判断key是否正确
        if (key in self.path) != True :
            data = '''<script>window.location.href='https://www.baidu.com';</script>'''
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(data.encode())
            return
        #处理企微发送的消息
        if("msg_signature" in self.path) == True:
            bot=get_resp_bot(self.path)
            wxcpt=WXBizMsgCrypt(respkey[bot][0],respkey[bot][1],respkey[bot][2])
            path= parse.urlparse(self.path)
            query=parse.parse_qs(path.query)
            sReqMsgSig = query["msg_signature"][0]
            sReqTimeStamp = query["timestamp"][0]
            sReqNonce = query["nonce"][0]
            sReqData = self.rfile.read(int(self.headers['content-length']))
            ret,sMsg=wxcpt.DecryptMsg( sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
            xml_tree = ET.fromstring(sMsg)
            content = xml_tree.find("Content").text
            agnetid = xml_tree.find("AgentID").text
            print("[DEBUG]企微接收消息："+content+" 应用ID："+agnetid)
            #直接回复企微200，异步回复用户信息
            self.send_response(200)
            self.end_headers()
            bot_id=get_botID(agnetid)
            send_to_wecom(resp(content,bot_id),bot_id)
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
            print("[DEBUG]POST方式发送消息："+text)
            send_to_wecom(text,botID)
        except:
            text=unquote(temp.group(1),'utf-8')
            print("[DEBUG]POST方式发送消息："+text)
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
