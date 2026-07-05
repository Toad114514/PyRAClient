# frontend/qt/login_dialog.py
import sys
from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("登录到 RetroAchievements")
        self.resize(350, 180)
        # 设置为模态窗口，弹窗时不允许操作背后的主窗口
        self.setModal(True) 

        # 主布局：垂直排列
        main_layout = QVBoxLayout(self)

        # 1. 顶部提示文字
        self.title_label = QLabel("请输入您的 RetroAchievements 账号信息")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 13px; margin-bottom: 5px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        # 2. 中间表单区域：自动帮你把“标签”和“输入框”对齐
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入 RA 用户名")
        form_layout.addRow("用户名:", self.username_input)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("请输入密码 或 Web API Key")
        # 将输入框设置为密码模式（显示为圆点）[cite: 2]
        self.token_input.setEchoMode(QLineEdit.Password) 
        form_layout.addRow("Web API Key:", self.token_input)

        main_layout.addLayout(form_layout)

        # 3. 底部按钮区域：水平排列[cite: 2]
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("登录")
        self.cancel_btn = QPushButton("取消")
        
        # 设置“登录”为默认按钮（按回车键直接触发）
        self.login_btn.setDefault(True)

        btn_layout.addWidget(self.login_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(btn_layout)

        # 4. 信号连接：点击接受或拒绝[cite: 2]
        self.login_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_credentials(self):
        """
        供主窗口调用的公开方法。
        返回一个元组: (用户名, 密码/Token)
        """
        username = self.username_input.text().strip()
        token = self.token_input.text().strip()
        return username, token