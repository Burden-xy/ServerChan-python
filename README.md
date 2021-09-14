# ServerChan-python
python版server酱
# 部署
1、修改server.py中的botskey、key参数，支持添加多个企微机器人（企微应用）。参考企微机器人配置  
2、修改接口访问key
# 使用
## 主动发送消息
1、get方式  
http://IP:PORT/key/?text=发送的信息&botID=机器人ID  
2、post方式  
http://IP:PORT/key/?botID=机器人ID  
body:text=发送的信息
## 从企微接收发送的消息并回复  
1、首先登录企微后台配置企微应用的接收API，配置方式百度企微API官方文档  
2、修改server.py中的respkey参数  
3、修改server.py中的resp函数内容，根据收到的信息进行回复  
# 备注
1、发送的信息支持URL编码和BASE64编码  
2、当botID为空或不存在时默认使用ID为default的机器人发送  
3、可不配置respkey参数，但此时无法从企微接收发送的消息  
# 更新日志
## V0.2  
1、现支持多个企微机器人并通过URL参数控制  
2、使用多线程，修复拒绝服务漏洞  
3、修复XSS漏洞  
4、修改返回内容为JSON格式  
5、修复若干BUG
## V0.3
1、新增从企微接收发送的消息并回复功能  
2、修复若干BUG  
