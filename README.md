# PyRAClient
简易的跨平台 Retroachievements 客户端，基于 RAWebAPi 文档构建
## Feature
 - 登录。。（登出没做）
 - 用户界面
   - 近期游玩的5个游戏
   - 最后活跃情况
 - 游戏界面
   - 所有成就列表（包括本人账号进度）
   - 游戏信息
   - 成就分布图
 - 用户关注列表
 - 标签页式布局
 - 多前端支持
   - PyQt5 (开发中)
   - PyTQt3 (未开始，关于 TQt3 的内容请查看 [https://www.trinitydesktop.org/docs/qt3/abouttqt.html](https://www.trinitydesktop.org/docs/qt3/abouttqt.html) )
   - Rich (未开始)
 - 以及 PyQt5 特有的跨平台，支持Win/Mac and Linux
## 安装/使用
```bash
git clone https://github.com/Toad114514/PyRAClient --depth 1
cd PyRAClient
pip install -r requirements.txt
python ./main.py
```
然后通过菜单栏的 系统 -> 登录 登录你的RA账号，需要输入你的用户名和你的 WebAPI Key
## 鸣谢/其他
感谢神秘 AI 帮我查资料。  
本项目使用 MIT Licence 开源协议。