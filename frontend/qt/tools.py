from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit

def dialog(selfs, type, title, msg):
    match type:
        case "warning" | "w":
            QMessageBox.warning(selfs, title, msg)
        case "error" | "e":
            QMessageBox.critical(selfs, title, msg)
        case "info" | "i":
            QMessageBox.information(selfs, title, msg)

def yesno(selfs, title, msg):
    resu = QMessageBox.question(selfs, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
    return resu

def dialog_input(selfs, title, msg):
    return QInputDialog.getText(selfs, title, msg, QLineEdit.Normal)

# NetImageLabel
from PyQt5.QtWidgets import QLabel
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QPixmap

class NetImageLabel(QLabel):
    def __init__(self, parent=None, default_text=""):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setText(default_text)
        
        # 1. 创建 Qt 专属的网络管理器
        self.manager = QNetworkAccessManager(self)
        # 2. 绑定信号：当下载完成时，调用 self.on_download_finished
        self.manager.finished.connect(self.on_download_finished)

    def load_from_url(self, url_str, width=80, height=80):
        """外部调用这个方法来传网址"""
        self.target_w = width
        self.target_h = height
        
        # 发起异步网络请求
        request = QNetworkRequest(QUrl(url_str))
        self.manager.get(request)
    
    def load_from_image(self, url_str, width=80, height=80):
        return self.load_from_url(url_str, width, height)
    
    def scale_cut(self, target_w: int, target_h: int):
        scaled_pixmap = self.pixmapa.scaled(
            target_w, target_h,
            Qt.KeepAspectRatioByExpanding,
            Qt.SmoothTransformation  # 👈 必须加这个，开启抗锯齿，防止放大时出现大方块和锯齿
        )
    
        # 3. 【裁剪】计算正中心的坐标 (Center Crop)
        # 算出超出的部分，然后除以 2 得到裁剪起始点
        x = (scaled_pixmap.width() - target_w) // 2
        y = (scaled_pixmap.height() - target_h) // 2
    
        # 使用 .copy(x, y, width, height) 强行抠图
        cropped_pixmap = scaled_pixmap.copy(x, y, target_w, target_h)
    
        # 4. 把裁剪好的精美图片塞进 QLabel，并锁死标签大小
        self.setFixedSize(target_w, target_h)
        self.setPixmap(cropped_pixmap)
    
    def on_download_finished(self, reply):
        """后台下载完成后触发的函数"""
        # 检查有没有网络错误
        if reply.error() == reply.NoError:
            # 读取下载好的二进制数据
            data = reply.readAll() 
            
            # 将二进制数据喂给 QPixmap
            self.pixmapa = QPixmap()
            if self.pixmapa.loadFromData(data):
                # 等比例缩放图片
                scaled_pixmap = self.pixmapa.scaled(
                    self.target_w, self.target_h, 
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.setPixmap(scaled_pixmap)
            else:
                self.setText("图片损坏")
        else:
            self.setText("加载失败")
            print(f"图片下载失败: {reply.errorString()}")
            
        # 释放网络连接内存
        reply.deleteLater()

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QToolTip
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QRectF

class AchievementChart(QWidget):
    def __init__(self, softcore_dict=None, hardcore_dict=None, bin_size=5, parent=None):
        super().__init__(parent)
        self.setMinimumSize(450, 320)
        self.setMouseTracking(True)
        
        self.softcore_dict = softcore_dict
        self.hardcore_dict = hardcore_dict
        self.bin_size = bin_size
        
        self.hovered_index = -1
        self.padding_left = 65  # 略微调大左边距，防止合并后大数字被遮挡
        self.padding_right = 20
        self.padding_top = 90
        self.padding_bottom = 60 # 略微调大底边距，给 "1-5" 这种长标签留出空间

        self.chart_data = []
        self.max_val = 100
        
        QToolTip.setFont(QFont("Arial", 10))
        self.setStyleSheet("""
            QToolTip { 
                background-color: #2b2b2b; 
                color: #ffffff; 
                border: 1px solid #555555;
                padding: 6px;
                border-radius: 4px;
            }
        """)
        
        if softcore_dict or hardcore_dict:
            self.set_data(softcore_dict, hardcore_dict, bin_size)
    
    def update2(self):
        return self.set_data(self.softcore_dict, self.hardcore_dict, self.bin_size)
        
    def set_data(self, softcore_dict, hardcore_dict, bin_size=5):
        """
        🎯 softcore_dict: 软核数据
        🎯 hardcore_dict: 硬核数据
        🎯 bin_size: 合并步长。比如 5 代表 [1-5], [6-10] 合并为一组。如果传 1 则不合并。
        """
        soft_src = softcore_dict if softcore_dict else {}
        hard_src = hardcore_dict if hardcore_dict else {}
        
        # 1. 清洗并提取所有纯数字键名，按数值大小升序排列
        all_keys = set(soft_src.keys()).union(set(hard_src.keys()))
        sorted_keys = sorted([int(k) for k in all_keys if str(k).isdigit()])
        
        if not sorted_keys:
            self.chart_data = []
            self.max_val = 100
            self.update()
            return

        self.chart_data = []
        max_total = 0

        if bin_size <= 1:
            # 💡 步长为 1，保持原样不合并
            for k in sorted_keys:
                soft_val = int(soft_src.get(str(k), 0))
                hard_val = int(hard_src.get(str(k), 0))
                self.chart_data.append((str(k), hard_val, soft_val))
                if (soft_val + hard_val) > max_total:
                    max_total = soft_val + hard_val
        else:
            # 💡 核心：按区间进行聚合分箱
            bins = {}
            for k in sorted_keys:
                # 计算当前关卡属于哪一个区间块 (例如: 1~5 属于块 0, 6~10 属于块 1)
                bin_idx = (k - 1) // bin_size
                
                if bin_idx not in bins:
                    bins[bin_idx] = {'soft': 0, 'hard': 0, 'min': k, 'max': k}
                
                bins[bin_idx]['soft'] += int(soft_src.get(str(k), 0))
                bins[bin_idx]['hard'] += int(hard_src.get(str(k), 0))
                bins[bin_idx]['min'] = min(bins[bin_idx]['min'], k)
                bins[bin_idx]['max'] = max(bins[bin_idx]['max'], k)

            # 将聚合好的分箱数据转为图表渲染格式
            for b_idx in sorted(bins.keys()):
                b_data = bins[b_idx]
                # 生成漂亮的标签，如 "1-5", "6-10"；如果区间内只有单张图则直接显示 "15"
                if b_data['min'] == b_data['max']:
                    lbl = str(b_data['min'])
                else:
                    lbl = f"{b_data['min']}-{b_data['max']}"
                
                soft_val = b_data['soft']
                hard_val = b_data['hard']
                self.chart_data.append((lbl, hard_val, soft_val))
                
                if (soft_val + hard_val) > max_total:
                    max_total = soft_val + hard_val

        # 2. 动态调整 Y 轴最高刻度线
        self.max_val = max(1, int(max_total * 1.15))
        self.hovered_index = -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 背景与标题
        painter.fillRect(self.contentsRect(), QColor("#1a1a1a"))
        blue_accent = QColor("#1e90ff")
        painter.setPen(blue_accent)
        painter.setFont(QFont("Arial", 18, QFont.Medium))
        painter.drawText(20, 40, "分布图")

        painter.setPen(QPen(blue_accent, 2))
        painter.drawLine(20, 52, self.width() - 20, 52)

        graph_w = self.width() - self.padding_left - self.padding_right
        graph_h = self.height() - self.padding_top - self.padding_bottom

        # Y 轴
        step = self.max_val // 5
        if step == 0: step = 1
        y_ticks = [i * step for i in range(6)]
        for tick in y_ticks:
            y_pos = self.padding_top + graph_h - (tick / self.max_val * graph_h)
            painter.setPen(QPen(QColor("#2d2d2d"), 1))
            painter.drawLine(self.padding_left, int(y_pos), self.padding_left + graph_w, int(y_pos))
            painter.setPen(blue_accent)
            painter.setFont(QFont("Arial", 9))
            painter.drawText(15, int(y_pos + 5), str(tick))

        # 绘制堆叠柱状图
        num_bars = len(self.chart_data)
        if num_bars == 0: return

        total_bar_w = graph_w / num_bars
        bar_gap = 6 # 既然合并了，柱子变宽了，可以适当调大缝隙让图表更具呼吸感
        bar_w = max(1, total_bar_w - bar_gap)

        for i, (x_lbl, gold_val, gray_val) in enumerate(self.chart_data):
            x_pos = self.padding_left + i * total_bar_w
            gold_h = (gold_val / self.max_val) * graph_h
            gray_h = (gray_val / self.max_val) * graph_h
            total_h = gold_h + gray_h

            if i == self.hovered_index:
                color_gray = QColor("#8c8c8c")
                color_gold = QColor("#ffcc00")
            else:
                color_gray = QColor("#737373")
                color_gold = QColor("#cca010")

            # 绘制灰色（Softcore）
            gray_y = self.padding_top + graph_h - total_h
            painter.fillRect(QRectF(x_pos, gray_y, bar_w, gray_h), color_gray)

            # 绘制金色（Hardcore）
            gold_y = self.padding_top + graph_h - gold_h
            painter.fillRect(QRectF(x_pos, gold_y, bar_w, gold_h), color_gold)

            # X 轴文字（因为合并了，数据量骤减，现在可以放心大胆展示每一个区间的标签，不再需要抽样）
            painter.save()
            painter.translate(x_pos + bar_w / 2, self.padding_top + graph_h + 10)
            painter.rotate(90)
            painter.setPen(blue_accent)
            painter.setFont(QFont("Arial", 9))
            painter.drawText(0, 5, x_lbl)
            painter.restore()

    def mouseMoveEvent(self, event):
        num_bars = len(self.chart_data)
        if num_bars == 0:
            super().mouseMoveEvent(event)
            return

        graph_w = self.width() - self.padding_left - self.padding_right
        graph_h = self.height() - self.padding_top - self.padding_bottom
        total_bar_w = graph_w / num_bars
        bar_gap = 6
        bar_w = max(1, total_bar_w - bar_gap)

        mouse_x = event.x()
        mouse_y = event.y()
        current_hover = -1

        if self.padding_left <= mouse_x <= self.padding_left + graph_w:
            idx = int((mouse_x - self.padding_left) / total_bar_w)
            if 0 <= idx < num_bars:
                x_lbl, gold_val, gray_val = self.chart_data[idx]
                x_pos = self.padding_left + idx * total_bar_w
                total_h = ((gold_val + gray_val) / self.max_val) * graph_h
                bar_y = self.padding_top + graph_h - total_h
                
                if x_pos <= mouse_x <= x_pos + bar_w and bar_y <= mouse_y <= self.padding_top + graph_h:
                    current_hover = idx

        if current_hover != self.hovered_index:
            self.hovered_index = current_hover
            self.update()

            if self.hovered_index != -1:
                x_lbl, gold_val, gray_val = self.chart_data[self.hovered_index]
                # 提示文字从小关卡升级为显示“区间范围”
                tip_text = (
                    f"<b>获得 </b> {x_lbl} 个成就的人数<br>"
                    f"<span style='color:#ffcc00;'>■</span> <b>硬核:</b> {gold_val} 人<br>"
                    f"<span style='color:#b0b0b0;'>■</span> <b>软核:</b> {gray_val} 人<br>"
                    f"<b>区间总计:</b> {gold_val + gray_val} 人"
                )
                QToolTip.showText(event.globalPos(), tip_text, self)
            else:
                QToolTip.hideText()

    def leaveEvent(self, event):
        self.hovered_index = -1
        self.update()
        QToolTip.hideText()