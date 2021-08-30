# server
python版server酱
# 部署
1、修改send_to_wecom1中的几个XXX参数，参考企微机器人配置
2、修改key
# 使用
1、get方式
http://IP:PORT/key?text=发送的信息
2、post方式
http://IP:PORT/key
body:
text=发送的信息
# 备注
发送的信息支持URL编码和BASE64编码
