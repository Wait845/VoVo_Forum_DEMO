# VoVo Forum
一个基于Python/Flask的前后端分离论坛系统
# 介绍
该论坛系统是一个前后端分离的项目。与普通论坛系统不同的是，该论坛系统侧重于极简，适用于中小型的论坛系统搭建. 该系统抛弃了普通论坛的 '签到', '板块', '积分' 等非必要功能，注重于论坛的本质 '交流'. 前端使用HTML，CSS，VUE 等, 包括登录注册, 论坛主页, 消息通知, 等页面. 后端使用Python, Flask, Mysql 等开发. 大幅度降低了运维人员搭建环境的压力, 并且有很好的扩展性.

# 亮点: 
* 使用前后端分离的结构，降低服务器压力，减少不必要的流量
* 通过对SQL操作的优化，数据的整合，实现了一次请求即可获取完整数据。减少HTTP请求，加快网页的响应时间
* 对请求的加密&解密, 授权等进行模块化处理,提高了处理效率及降低服务器压力

# 开发初衷
本人原先打算为自己所在的学校开设一个论坛,参考了各大开源论坛系统。因为有太多的不必要功能反而缩小的论坛的本质'交流', 于是便自己开始了这个项目。 本人之前只有过python和java的开发经历，对前端一窍不通。该项目的所有前端代码几乎都是现学现敲的，略显粗糙。在后续的版本中我也会不断的更新使该系统更加的完善

# 安装
```
git clone https://github.com/Wait845/VoVo_Forum_DEMO.git
cd VoVo_Forum_DEMO
nano config.ini
python3 vovo.py
```

# 提示
该论坛系统目前只是一个DEMO项目，请不要用于生产环境

# 已知BUG
* 在移动端上的时间显示功能不正常
* 该系统占未对用户输入的数据进行过滤，可能导致服务端收到攻击

# 截图
![home](https://github.com/Wait845/VoVo_Forum_DEMO/blob/master/home.png?raw=true)
![post](https://github.com/Wait845/VoVo_Forum_DEMO/blob/master/post.png?raw=true)
