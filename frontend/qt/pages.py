from PyQt5.QtGui import *
import PyQt5.QtCore as core
from PyQt5.QtWidgets import *

from frontend.qt.tools import *
from PyRACLib.log import log
from PyRACLib.tool import s2hms

# 异步
from PyQt5.QtCore import QThread, pyqtSignal
import traceback

class GenericAsyncWorker(QThread):
    # 🎯 核心：定义一个通用的信号，用来把后台拿到的数据安全地回传给主线程
    callback_signal = pyqtSignal(object)

    def __init__(self, api_function, *args, **kwargs):
        super().__init__()
        self.api_function = api_function  # 目标 API 函数指针
        self.args = args                  # positional 参数
        self.kwargs = kwargs              # keyword 参数

    def run(self):
        try:
            # 🚀 在后台默默执行原本会卡死 UI 的 PyRACLib 请求
            result = self.api_function(*self.args, **self.kwargs)
            # 执行成功后，把结果通过信号发射出去
            self.callback_signal.emit(result)
        except Exception as e:
            log.error(f"async was get Err: {e}")
            log.error(f"The trackback:\n{traceback.format_exc()}")
            self.callback_signal.emit(None)

def run_async(selfs, api_func, args_tuple, callback_func):
    """
    🚀 极简异步发射台
    :param api_func:      你要调用的 self.rac.xxx 函数，千万别带括号！
    :param args_tuple:    传给这个函数的参数，必须是元组，比如 (game_id,)
    :param callback_func: 数据拿回来之后，你要喂给前端的哪个渲染函数
    """
    
    if not hasattr(selfs, "_active_threads"):
        selfs._active_threads = []
    # 实例化。
    worker = GenericAsyncWorker(api_func, *args_tuple)
    
    # 绑定回调
    worker.callback_signal.connect(callback_func)
    
    # 释放。
    worker.finished.connect(lambda: selfs._active_threads.remove(worker) if worker in selfs._active_threads else None)
    worker.finished.connect(worker.deleteLater)
    
    # startwork
    selfs._active_threads.append(worker)
    worker.start()

# 页面 =============================
class PageProfile(QWidget):
    open_game_page = core.pyqtSignal(int, str)
    
    def __init__(self, rac, username="", parent=None):
        super().__init__(parent)
        self.data = ""
        self.username = username
        run_async(self, rac.user_sum, (self.username, ), self.init_ui)
        # self.init_ui()
    
    def open_game(self, item):
        game_id = item.data(core.Qt.UserRole)["id"]
        game_title = item.data(core.Qt.UserRole)["title"]
        self.open_game_page.emit(game_id, game_title)
    
    def init_ui(self, data):
        self.data = data
        
        qvbox = QVBoxLayout(self)
        qvbox.setSpacing(10)
        qvbox.setContentsMargins(13, 13, 13, 13)
        
        try:
            ab = self.data['LastActivity']
        except:
            errText = QLabel(f"没有找到用户 {self.username}")
            qvbox.addWidget(errText)
            return
        
        # 头部信息 ======================================
        headerbox = QHBoxLayout()
        
        info_layout = QVBoxLayout()
        self.name_label = QLabel(self.username)
        font_name = QFont()
        font_name.setPointSize(18)
        font_name.setBold(True)
        self.name_label.setFont(font_name)
        info_layout.addWidget(self.name_label)
        
        # moto
        self.info_moto = QLabel("iam Moto")
        font = QFont()
        font.setPointSize(16)
        font.setItalic(True)
        self.info_moto.setFont(font)
        self.info_moto.setText(self.data["Motto"])
        self.info_moto.setWordWrap(True)
        info_layout.addWidget(self.info_moto)
        
        # 简短的 info
        info_text=f"加入时间: {self.data['MemberSince']}\n最后上线: {self.data['LastActivity']['lastupdate']}\n实际分数: {self.data['TotalTruePoints']} (排名 {self.data['Rank']})"
        self.info = QLabel("各种info")
        font = QFont()
        font.setItalic(True)
        self.info.setFont(font)
        self.info.setText(info_text)
        info_layout.addWidget(self.info)
        
        info_layout.addStretch()
        headerbox.addLayout(info_layout)
        
        # 头像部分
        self.head = NetImageLabel(self, default_text="我是\n头像")
        self.head.setStyleSheet("border: 2px solid #555; background-color: #ddd; border-radius: 10px;")
        self.head.load_from_url(self.data["UserPic"], 100, 100)
        self.head.setFixedSize(100, 100)
        headerbox.addWidget(self.head)
        qvbox.addLayout(headerbox)
        
        # 头部信息 End ================================
        
        # 最后游玩 ====================================
        recent_played = QHBoxLayout()
        recent_group = QGroupBox(title="最后游玩")
        last = self.data["RecentlyPlayed"][0]
        #icon
        gameico = NetImageLabel(self, default_text="我是游戏图标")
        gameico.load_from_url(last["ImageIcon"], 80, 80)
        gameico.setFixedSize(80, 80)
        recent_played.addWidget(gameico)
        
        # info
        infoL = QVBoxLayout()
        title = QLabel(last["Title"])
        title.setStyleSheet("color: blue; font-weight: bold; font-size: 19px;")
        infoL.addWidget(title)
        
        lastplayed = QLabel(f"最后游玩: {last['LastPlayed']}")
        lastplayed.setStyleSheet("color: grey; font-style: italic; font-size: 13px;")
        infoL.addWidget(lastplayed)
        
        richtext = QLabel(self.data["RichPresenceMsg"])
        richtext.setStyleSheet("font-size: 16px; font-style: italic;")
        infoL.addWidget(richtext)
        
        recent_played.addLayout(infoL)
        recent_group.setLayout(recent_played)
        qvbox.addWidget(recent_group)
        
        # 分割线 ======================================
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #ccc;")
        qvbox.addWidget(line)
        
        # 最近游玩游戏 =================================
        recent_game = QGroupBox("近期游玩游戏")
        recent_game.setObjectName("recentgame")
        recent_game.setStyleSheet("QGroupBox#recentgame{ background-color: #bcbcbc; border-radius: 5px; margin-top: 21px;}")
        rglayout = QVBoxLayout()
        recent_game.setFixedHeight(300)
        
        self.lists_rp = QListWidget()
        self.lists_rp.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        rglayout.addWidget(self.lists_rp)
        
        for x in self.data["RecentlyPlayed"]:
            items = QListWidgetItem(self.lists_rp)
            tmpw = QWidget()
            gameid = str(x["GameID"])
            award = self.data["Awarded"][gameid]
            singleL = QHBoxLayout()
            softcore = award["NumAchieved"] - award["NumAchievedHardcore"]
            
            # icons
            icons = NetImageLabel(self)
            icons.load_from_url(x["ImageIcon"])
            if softcore == 0:
                icons.setStyleSheet("border: 5px soild #fcd337")
            singleL.addWidget(icons)
            
            infoLrec = QVBoxLayout()
            # Title
            title = QLabel(x["Title"])
            title.setStyleSheet("color: blue; font-weight: bold; font-size: 18px;")
            infoLrec.addWidget(title)
            
            # infolabel
            info_label = QLabel(f"{x['ConsoleName']}, 最后游玩: {x['LastPlayed']}\n已解锁 {award['NumAchieved']}/{award['NumPossibleAchievements']} 个成就 ({softcore} 软核, 全共 {award['ScoreAchieved']} 分)")
            info_label.setStyleSheet("color: #2367a5; font-size: 13px;")
            infoLrec.addWidget(info_label)
            
            # progress
            prog = QProgressBar(self)
            prog.setRange(0, award["NumPossibleAchievements"])
            prog.setValue(award["NumAchieved"])
            infoLrec.addWidget(prog)
            
            singleL.addLayout(infoLrec)
            tmpw.setLayout(singleL)
            
            items.setSizeHint(tmpw.sizeHint())
            items.setData(core.Qt.UserRole, {"id": int(gameid), "title": title.text()})
            self.lists_rp.itemDoubleClicked.connect(self.open_game)
            self.lists_rp.addItem(items)
            self.lists_rp.setItemWidget(items, tmpw)
        
        recent_game.setLayout(rglayout)
        qvbox.addWidget(recent_game)

class PageFollow(QWidget):
    open_user_sign = core.pyqtSignal(str)
    
    def __init__(self, rac, parent=None):
        super().__init__(parent)
        self.data = {}
        self.rac = rac
        run_async(self, rac.user_follow, (), self.init_ui)
    
    def open_user_profile(self, item):
        uname = item.data(core.Qt.UserRole)
        self.open_user_sign.emit(uname)
        
    def init_ui(self, data):
        self.data = {}
        qvbox = QVBoxLayout(self)
        lists = QListWidget()
        qvbox.addWidget(lists)
        lists.itemDoubleClicked.connect(self.open_user_profile)
        
        for x in data["Results"]:
            listw = QListWidgetItem(lists)
            widget = QWidget()
            qhbox = QHBoxLayout()
            # UserPic
            ico = NetImageLabel(self)
            ico.load_from_url(x['UserPic'], 35, 35)
            ico.setAlignment(core.Qt.AlignLeft)
            # rightInfo
            qhbox.addWidget(ico)
            
            # label
            label = QLabel(x["User"])
            label.setStyleSheet("font-weight: bold; font-size: 21px;")
            qhbox.addWidget(label)
            label.setAlignment(core.Qt.AlignLeft)
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            # point
            points = QLabel(f"{x['Points']} 点数 ({x['PointsSoftcore']} 软核点数)")
            points.setStyleSheet("font-size: 15px; font-style: italic;")
            qhbox.addWidget(points)
            points.setAlignment(core.Qt.AlignLeft)
            
            if x["IsFollowingMe"] == True:
                fback = QLabel("他也回关了你")
                fback.setStyleSheet("font-size: 15px; color: blue;")
                qhbox.addWidget(fback)
                fback.setAlignment(core.Qt.AlignLeft)
            
            widget.setLayout(qhbox)
            listw.setData(core.Qt.UserRole, x["User"])
            listw.setSizeHint(widget.sizeHint())
            lists.addItem(listw)
            lists.setItemWidget(listw, widget)
        
        

class PageGameInfo(QWidget):
    def __init__(self, rac, gameid="", parent=None):
        super().__init__(parent)
        self.data = {}
        # self.dist = rac.game_ach_dist(self.data["ID"])
        # self.hardcore_dist = rac.game_ach_dist(self.data["ID"], hardcore=True)
        # self.init_ui()
        self.achchart = AchievementChart() # 成就分布图 
        self.gamehash_list = QListWidget() # gamehash
        self.list_ach = QListWidget() # Achievements List
        self.rac = rac
        run_async(self, rac.game_info, (gameid, True), self.init_ui)
        run_async(self, rac.game_ach_dist, (gameid, ), self.set_soft)
        run_async(self, rac.game_ach_dist, (gameid, True), self.set_hard)
        run_async(self, rac.game_achievement, (gameid, ), self.update_achievement)
        run_async(self, rac.game_hashes, (gameid, ), self.update_support)
    
    def init_ui(self, data):
        # Original
        self.data = data
        self.ach = self.data["Achievements"]
        qvbox = QVBoxLayout(self)
        qvbox.setSpacing(10)
        
        # header =====================
        header = QVBoxLayout()
        
        # icons
        icons = NetImageLabel(self)
        icons.load_from_url(self.data["ImageIcon"], 70, 70)
        icons.setAlignment(core.Qt.AlignLeft)
        header.addWidget(icons)
        
        # Title
        title = QLabel(self.data["Title"])
        title.setStyleSheet("font-weight: bold; font-size: 20px;")
        header.addWidget(title)
        
        # consoleName
        consoleName = QLabel(self.data["ConsoleName"])
        consoleName.setStyleSheet("font-style: italic; font-size: 15px;")
        header.addWidget(consoleName)
        
        qvbox.addLayout(header)
        # Achievements List =======================
        
        achievements = QWidget()
        ach_layout = QVBoxLayout()
        self.status_ach = QLabel("加载中...")
        self.status_mine = QHBoxLayout()
        
        # 数据放在下面更新
        ach_layout.addWidget(self.status_ach)
        ach_layout.addLayout(self.status_mine)
        ach_layout.addWidget(self.list_ach)
        
        self.list_ach.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        achievements.setLayout(ach_layout)
        # 支持的游戏 Hashes ======================
        gamehash = QWidget()
        gamehashL = QVBoxLayout()
        
        gamehashL.addWidget(self.gamehash_list)
        gamehash.setLayout(gamehashL)
        # Game Info ========================
        gameinfo = QWidget()
        grids = QGridLayout(gameinfo)
        
        # titleArt
        titleArt = NetImageLabel(self)
        titleArt.load_from_image(self.data["ImageTitle"], 200, 200)
        grids.addWidget(titleArt, 2, 0)
        titleArt.setScaledContents(True)
        
        boxArt = NetImageLabel(self)
        boxArt.load_from_image(self.data["ImageBoxArt"], 200, 200)
        grids.addWidget(boxArt, 2, 1)
        boxArt.setScaledContents(True)
        
        ingameArt = NetImageLabel(self)
        ingameArt.load_from_url(self.data["ImageIngame"], 400, 400)
        ingameArt.setAlignment(core.Qt.AlignCenter)
        grids.addWidget(ingameArt, 0, 0, 2, 2, alignment=core.Qt.AlignCenter)
        ingameArt.setScaledContents(True)
        
        table = QTableWidget()
        table.setColumnCount(1)
        table.setRowCount(9)
        
        table.setVerticalHeaderLabels(["游戏ID", "游戏名", "平台", "作者", "发布时间", "分类", "成就数", "合集", "最后更新"])
        table.horizontalHeader().setVisible(False)
        details = [str(self.data["ID"]), self.data["Title"], self.data["ConsoleName"], self.data["Developer"], self.data["Released"], self.data["Genre"], str(self.data["NumAchievements"]), self.data["Publisher"], self.data["Updated"]]
        
        for row_idx, detail_text in enumerate(details):
            item = QTableWidgetItem(detail_text)
            item.setTextAlignment(core.Qt.AlignLeft | core.Qt.AlignVCenter)
            table.setItem(row_idx, 0, item)
        
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.setFixedHeight(205)
        
        grids.addWidget(table, 0, 3, 3, 3, alignment=core.Qt.AlignVCenter)
        
        # QTabs ===========================
        tabs = QTabWidget()
        # tabs.setTabPosition(QTabWidget.South)
        tabs.tabBar().setExpanding(True)
        tabs.setDocumentMode(True)
        qvbox.addWidget(tabs)
        
        default = tabs.addTab(achievements, "成就")
        tabs.addTab(gameinfo, "游戏信息")
        tabs.addTab(self.achchart, "成就分布图")
        tabs.addTab(gamehash, "支持的哈希值")
        tabs.setCurrentIndex(default)
        
        qvbox.addWidget(tabs)
    
    def set_soft(self, data):
        self.achchart.softcore_dict=data
        self.achchart.update2()
    
    def set_hard(self, data):
        self.achchart.hardcore_dict=data
        self.achchart.update2()
    
    def update_support(self, data):
        for x in data["Results"]:
            widget = QWidget()
            qvbox = QVBoxLayout()
            item = QListWidgetItem(self.gamehash_list)
            
            # Name
            nameL = QHBoxLayout()
            name = QLabel(x["Name"])
            name.setStyleSheet("color: #2367a5; font-size: 18px; font-weight: bold;")
            nameL.addWidget(name)
            
            # LabelUrl
            for b in x["LabelUrl"]:
                img = NetImageLabel(self)
                img.load_from_url(b, 70, 20)
                nameL.addWidget(img)
                img.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            qvbox.addLayout(nameL)
            
            # info
            patch_text = ""
            if not x['PatchUrl'] is None:
                patch_text=f"<br>  <a href={x['PatchUrl']}>下载可用补丁</a>"
            info = QLabel(f"  <i>MD5: {x['MD5']}</i>"+patch_text)
            info.setOpenExternalLinks(True)
            info.setCursor(core.Qt.PointingHandCursor)
            qvbox.addWidget(info)
            widget.setLayout(qvbox)
            
            item.setSizeHint(widget.sizeHint()) 
            widget.setLayout(qvbox)
            self.gamehash_list.addItem(item)
            self.gamehash_list.setItemWidget(item, widget)
    
    def update_achievement(self, data):
        ach_infoText = f"成就数 {data['NumAchievements']} | {data['NumDistinctPlayers']} 人游玩/玩过\n"
        ach_infoText += f"通关时间 {s2hms(data['MedianTimeToBeat'])} | 硬核 {s2hms(data['MedianTimeToBeatHardcore'])} | 精通 {s2hms(data['MedianTimeToComplete'])} | 硬核精通 {s2hms(data['MedianTimeToMaster'])} (中位数)"
        self.status_ach.setText(ach_infoText)
        
        status_mprog = QProgressBar()
        status_minfol = QLabel("你的进度: ")
        status_minfor = QLabel()
        
        status_mprog.setRange(0, data["NumAchievements"])
        status_mprog.setValue(data["NumAwardedToUser"])
        status_mprog.setFixedHeight(15)
        status_minfor.setText(f"{data['NumAwardedToUser']}/{data['NumAchievements']} ({data['NumAwardedToUserHardcore']} 硬核, {data['UserCompletionHardcore']} 占比)")
        
        self.status_mine.addWidget(status_minfol)
        self.status_mine.addWidget(status_mprog)
        self.status_mine.addWidget(status_minfor)
        
        # Status
        for x in data["Achievements"]:
            widget = QWidget()
            item = QListWidgetItem(self.list_ach)
            singleL = QHBoxLayout()
            
            item_data = x
            
            # 左边写图标
            icon = NetImageLabel(self)
            icon.load_from_url(x["BadgeUrl"], 80, 80)
            singleL.addWidget(icon)
            
            # Info
            infoL = QVBoxLayout()
            
            # Achtitle
            title = QLabel(x["Title"])
            title.setStyleSheet("font-size: 18px; font-weight: bold;")
            infoL.addWidget(title)
            # infos
            info_msg = f"{x['Description']}\nId: {x['ID']} | {x['Points']} 积分"
            info_label = QLabel(info_msg)
            info_label.setStyleSheet("font-size: 14px; font-style:italic;color; grey")
            infoL.addWidget(info_label)
            
            # prog
            prog = QProgressBar()
            prog.setRange(0, data["NumDistinctPlayers"])
            prog.setValue(int(x["NumAwardedHardcore"]))
            prog.setStyleSheet("""
            QProgressBar {
                border: 1px solid #B0B0B0;
                border-radius: 6px;
                text-align: center;
                background-color: #E5E5E5;
                color: black;
            }
            
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #FFE066,   /* 顶部高亮淡黄 */
                    stop: 0.5 #FFCC00, /* 中间标准黄 */
                    stop: 1.0 #D9A300  /* 底部饱满深黄 */
                );
                border-radius: 5px;
            }
            """)
            infoL.addWidget(prog)
            
            singleL.addLayout(infoL)
            widget.setLayout(singleL)
            item.setSizeHint(widget.sizeHint())
            
            self.list_ach.addItem(item)
            self.list_ach.setItemWidget(item, widget)