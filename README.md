# Guabot 使用指南
依赖于[mai-bot](https://github.com/Diving-Fish/mai-bot)开源项目，基于[Nonebot2](https://github.com/nonebot/nonebot2)，以**舞萌DX**查询为主的多功能~~(自用)~~QQbot

项目地址：https://github.com/Linxaee/Guabot

## 开始

详细可参考[mai-bot](https://github.com/Diving-Fish/mai-bot)开源项目

通过(指定清华镜像源)

```
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

安装依赖，随后运行

```
python bot.py
```

指令相关可以使用 "瓜瓜 help" 或者 "/help" 调出帮助文档

bug有点多，测试修改ing

## 指令列表 

例子中<>中内容代表需要填入项，[]中内容代表选择其中一项,(）中内容代表可选项，输入指令时均不需要携带括号本身，同时请注意指令是否需要空格

### maimai相关

---------------------

#### 1. 今日运势

查看今日舞萌运势

例：今日运势



#### 2. XXXmaimaiXXX什么

随机一首歌

例：maimai什么歌最难



#### 3. 随个[dx/标准] [绿黄红紫白]<难度> 

随机一首指定条件的乐曲

例：随个红13



#### 4. 查歌 <乐曲标题的一部分> 

查询符合条件的乐曲

例：查歌 奏者



#### 5. [绿黄红紫白]id<歌曲编号>

查询乐曲信息或谱面信息

例：红id823



#### 6. 定数查歌 <定数> 

查询定数对应的乐曲

例：定数查歌 13



#### 7. 定数查歌 <定数下限> <定数上限>

查询定数处于给定范围的乐曲

例：定数查歌 13.0 13.2



#### 8. 分数线 <难度+歌曲id> <分数线> 

详情请输入“分数线 帮助”查看



#### 9. 瓜瓜 b40/b40/查<用户名>成分

查看自己或者某位用户的b40

例：查Linxae成分



#### 10. 瓜瓜 底分分析/底分分析

查看乐曲推荐和底分分析



#### 11. <歌曲别名>是什么歌

查询乐曲别名对应的乐曲

例：太空熊是什么歌



#### 12. <歌曲别名>有什么别名

查询乐曲的其它别名

例：太空熊有什么别名



#### 13. 添加别名 <歌曲id> <歌曲别名>

为指定id的歌曲添加别名

例：添加别名 823 奏者背中提琴语



#### 14. <标级>定数表    (仅支持8-15）

查看某标级定数表

例：14+定数表



#### 15. <标级>完成表    需登录查分器后使用 (仅支持8-15）

查看某标级rank完成表

例：14+完成表



#### 6. <标级>分数列表 (页号)     需登录查分器后使用(仅支持8-15）

查看某标级分数列表

例：13分数列表 / 14+分数列表 



#### 17. 查分器登录 <查分器账号> <查分器密码> (仅支持8-15）

登录查分器用于后续使用

例：查分器登录 123 456



### 娱乐相关

---------------------------

#### 1. 瓜瓜 来点龙 / 来点龙图 / /dragon /随个龙

随机一张龙图



#### 2. 瓜瓜 来点fu / 来点fufu / /fufu /随个fu

随机一张fufu



#### 3. 群友圣经

随机一份群友圣经



#### 4. 瓜瓜 添加圣经 <需添加内容> 

为本群添加圣经

例：瓜瓜 添加圣经 哦哦哦哦哦哦 / 一张图片



### 疫情相关

-------------------------

#### 1. 疫情动态 <市名/国内>

查看某市或者国内疫情动态

例：疫情动态 成都 / 疫情动态 国内



#### 2. 风险区 <市名> <区名/关键字> (页码)

查看某地区风险区列表

例：风险区 成都 新都 / 风险区 成都 / 风险区 成都 2



### 鸣谢

-------------

感谢 [Diving-Fish](https://github.com/Diving-Fish) 提供的源码支持





