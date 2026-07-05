# 参数封装
from PyRACLib.pyraclib import RAClient

# 前端
from PyQt5.QtWidgets import QMainWindow
import PyQt5.QtGui as gui
import PyQt5.QtWidgets as wg
import PyQt5.QtCore as core
from frontend.qt.tools import *
from frontend.qt.login import LoginDialog
from frontend.qt.pages import *
from PyRACLib.log import log

class Client(QMainWindow):
    def __init__(self, parent = None, version="0.1"):
        super(Client, self).__init__(parent)
        self.rac = RAClient() # RAC 封装
        self.mainUi()
    
    def setmsg(self, msg):
        log.info(f"[PyQt5]: statusBar update: {msg}")
        self.statusBar().showMessage(msg)
    
    def mainUi(self):
        self.setWindowTitle(f"PyRAClient")
        self.resize(900, 750)
        self.setMinimumSize(750,600)
        
        # 菜单
        mb = self.menuBar()
        
        # TabBar
        act = mb.addMenu("系统")
        self.actLogin = wg.QAction("登录", self)
        self.actLogin.triggered.connect(self.login)
        self.actLogout = wg.QAction("登出", self)
        actExit = wg.QAction("退出程序", self)
        actExit.triggered.connect(wg.qApp.quit)
        act.addAction(self.actLogin)
        act.addAction(self.actLogout)
        act.addAction(actExit)
        
        self.actUser = mb.addMenu("用户")
        actMyhome = wg.QAction("我的主页", self)
        actMyhome.triggered.connect(lambda: self.profile_page(self.rac.uname, title="个人主页"))
        actJumptouser = wg.QAction("查看用户 (通过用户名跳转)...", self)
        actJumptouser.triggered.connect(lambda: self.jumptouser())
        actFollow = wg.QAction("查看关注列表", self)
        actFollow.triggered.connect(lambda: self.follow_page())
        self.actUser.addAction(actMyhome)
        self.actUser.addAction(actJumptouser)
        self.actUser.addAction(actFollow)
        
        # MainWidget
        self.MainWidget = wg.QWidget()
        self.setCentralWidget(self.MainWidget)
        self.MainQV = wg.QVBoxLayout(self.MainWidget)
        # 标签页
        self.MainTab = wg.QTabWidget()
        self.MainTab.setTabsClosable(True)
        self.MainTab.tabCloseRequested.connect(self.close_tab)
        self.MainQV.addWidget(self.MainTab)
        # 空白页提示
        self.emLabel = wg.QLabel("这里啥都没有~")
        self.emLabel.setAlignment(core.Qt.AlignCenter)
        self.MainQV.addWidget(self.emLabel)
        
        self.check_empty_status()
        self.check_login()
        
        if self.rac.login_status == True:
            self.profile_page(self.rac.uname, title="个人主页")
            # self.follow_page()
            # self.new_tab("GamePageTest", PageGameInfo(self.rac, "36973")) # ~ Hack ~ Transcending The Rainbow 
        self.setmsg("Ready")
        self.show()
    
    # 标签页逻辑
    def new_tab(self, title=None, widget=wg.QWidget(), scroll=True):
        log.info(f"[PyQt5]: New Tab Creating... (title: {title}, scroll {scroll}")
        if title == None: title = "无标题"
        if self.rac.login_status == False: return
        if scroll == True:
            scroll = QScrollArea()
            scroll.setWidget(widget)
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            newIndex = self.MainTab.addTab(scroll, title)
        else:
            newIndex = self.MainTab.addTab(widget, title)
        
        self.setmsg(title)
        self.MainTab.setCurrentIndex(newIndex)
        self.check_empty_status()
    
    def check_empty_status(self):
        if self.MainTab.count() == 0:
            self.MainTab.hide()
            self.emLabel.show()
        else:
            self.MainTab.show()
            self.emLabel.hide()
        
    def close_tab(self, index):
        self.MainTab.removeTab(index)
        self.check_empty_status()
    
    def check_login(self):
        log.info("[PyQt5]: check self.rac.login_status")
        if self.rac.login_status == False:
            self.emLabel.setText("当前没有登录，请点击左上角菜单登录")
        self.actLogout.setEnabled(self.rac.login_status)
        self.actLogin.setEnabled(not self.rac.login_status)
        self.actUser.setEnabled(self.rac.login_status)
    
    # 登录
    def login(self):
        log.info("[PyQt5]: start login account")
        dialogd = LoginDialog(self)
        if dialogd.exec_() == wg.QDialog.Accepted:
            uname, apikey = dialogd.get_credentials()
            log.info(f"[PyQt5]: Get {uname}, try logging..")
            if self.rac.login(uname, apikey) == True:
                log.info("login success")
                dialog(self, "i", "登录成功！", f"欢迎您回来, {uname}")
                self.emLabel.setText("这里啥也没有~")
            else:
                log.info("login failed")
                dialog(self, "e", "登录失败", "请检查网络，用户名和Web APIKey 是否正确")
    
    # 跳转到用户
    def jumptouser(self):
        text, ok = dialog_input(self, "跳转到用户", "输入用户名...")
        if ok and text:
            self.profile_page(text)
    
    def follow_page(self):
        widget = PageFollow(self.rac)
        widget.open_user_sign.connect(self.profile_page)
        self.new_tab("关注的用户", widget)
    
    def profile_page(self, uname, title=None):
        title = f"{uname} 的主页"  
        if not title is None:
            title = title
        widget = PageProfile(self.rac, uname)
        widget.open_game_page.connect(self.game_page)
        self.new_tab(title, widget)
    
    def game_page(self, ida, title):
        for index in range(self.MainTab.count()):
            existing_widget = self.MainTab.widget(index)
            
            # ⚠️ 注意：因为你的 new_tab 可能会用 QScrollArea 包裹组件
            # 如果外层是滚动区域，我们需要“穿透”进去拿你真正的游戏窗口
            if isinstance(existing_widget, QScrollArea):
                existing_widget = existing_widget.widget()
                
            # 对暗号：如果这个页面的 game_id 和我们双击的一致
            if getattr(existing_widget, "game_id", None) == ida:
                # 找到了！直接切换过去，打道回府，不再重复新建
                self.MainTab.setCurrentIndex(index)
                return

        # 2. 🚀 如果没打开过，开始创建你刚才想做的“右边是具体数据的表格/面板”
        # 假设你写好了一个叫 GameDetailTable 的表格类
        widget = PageGameInfo(self.rac, ida)
        
        widget.game_id = ida
        self.new_tab(title=title, widget=widget)