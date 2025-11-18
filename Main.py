from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys, os

# --------- Env & Paths ---------
env_vars = dotenv_values(".env") or {}
Assistantname = env_vars.get("Assistantname", "Assistant")

PROJECT_ROOT = os.getcwd()
TempDirPath = os.path.join(PROJECT_ROOT, "Frontend", "Files")
GraphicsDirPath = os.path.join(PROJECT_ROOT, "Frontend", "Graphics")

os.makedirs(TempDirPath, exist_ok=True)
for fname, default in [("Mic.data","False"),("Status.data",""),("Responses.data","")]:
    f = os.path.join(TempDirPath, fname)
    if not os.path.exists(f):
        with open(f, "w", encoding="utf-8") as fp: fp.write(default)

def GraphicsDirectoryPath(name): return os.path.join(GraphicsDirPath, name)
def TempDirectoryPath(name): return os.path.join(TempDirPath, name)

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    if not new_query:
        return "?"
    words = new_query.split()
    qwords = ["how","what","who","where","when","why","which","whose","whom","can you","what's","where's","how's"]
    if any(new_query.startswith(w+" ") for w in qwords):
        new_query = (new_query[:-1] if words[-1][-1] in ['.','?','!'] else new_query) + "?"
    else:
        new_query = (new_query[:-1] if words[-1][-1] in ['.','?','!'] else new_query) + "."
    return new_query.capitalize()

def SetMicrophoneStatus(v):
    with open(TempDirectoryPath("Mic.data"), "w", encoding="utf-8") as f: f.write(v)
def GetMicrophoneStatus():
    with open(TempDirectoryPath("Mic.data"), "r", encoding="utf-8") as f: return f.read()
def SetAssistantStatus(v):
    with open(TempDirectoryPath("Status.data"), "w", encoding="utf-8") as f: f.write(v)
def GetAssistantStatus():
    with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as f: return f.read()
def ShowTextToScreen(text):
    with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as f: f.write(text)

def MicButtonInitialed(): SetMicrophoneStatus("False")
def MicButtonClosed(): SetMicrophoneStatus("True")

old_chat_message = ""

# --------- Widgets ---------
class ChatSection(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 20, 20)
        layout.setSpacing(10)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat.setFrameStyle(QFrame.NoFrame)
        font = QFont(); font.setPointSize(13)
        self.chat.setFont(font)
        layout.addWidget(self.chat)

        cf = QTextCharFormat(); cf.setForeground(QColor(Qt.blue))
        self.chat.setCurrentCharFormat(cf)

        self.gif_label = QLabel(); self.gif_label.setStyleSheet("border:none;")
        gif_path = GraphicsDirectoryPath("Jinx.gif")
        self.movie = QMovie(gif_path) if os.path.exists(gif_path) else None
        if self.movie and self.movie.isValid():
            self.movie.setScaledSize(QSize(480, 270))
            self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.gif_label.setMovie(self.movie)
            self.movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color:white; font-size:16px; margin-right:195px; border:none;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        self.setStyleSheet("""
            QWidget{background-color:black;}
            QScrollBar:vertical { border:none; background:black; width:10px; margin:0; }
            QScrollBar::handle:vertical { background:white; min-height:20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { background:black; height:10px; }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background:none; }
        """)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)

    def loadMessages(self):
        global old_chat_message
        try:
            with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as f:
                messages = f.read()
        except FileNotFoundError:
            return
        if not messages or len(messages) <= 1 or messages == old_chat_message:
            return
        self.addMessage(messages, "White")
        old_chat_message = messages

    def updateStatus(self):
        try:
            with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as f:
                self.label.setText(f.read())
        except FileNotFoundError:
            self.label.setText("")

    def addMessage(self, message, color):
        cur = self.chat.textCursor()
        fmt = QTextCharFormat(); fmt.setForeground(QColor(color))
        b = QTextBlockFormat(); b.setTopMargin(10); b.setLeftMargin(10)
        cur.setCharFormat(fmt); cur.setBlockFormat(b)
        cur.insertText(message + "\n")
        self.chat.setTextCursor(cur)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            desktop = QApplication.desktop()
            rect = desktop.screenGeometry()
            sw, sh = rect.width(), rect.height()
        except Exception:
            sw, sh = 1280, 720

        lay = QVBoxLayout(); lay.setContentsMargins(0,0,0,150)

        gif_label = QLabel()
        gif_path = GraphicsDirectoryPath("Jinx.gif")
        movie = QMovie(gif_path) if os.path.exists(gif_path) else None
        if movie and movie.isValid():
            max_h = int(sw/16*9)
            movie.setScaledSize(QSize(sw, max_h))
            gif_label.setMovie(movie)
            gif_label.setAlignment(Qt.AlignCenter)
            movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.icon = QLabel(); self.icon.setFixedSize(150,150); self.icon.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon.mousePressEvent = self.toggle_icon

        self.label = QLabel(""); self.label.setStyleSheet("color:white; font-size:16px; margin-bottom:0;")

        lay.addWidget(gif_label, alignment=Qt.AlignCenter)
        lay.addWidget(self.label, alignment=Qt.AlignCenter)
        lay.addWidget(self.icon, alignment=Qt.AlignCenter)
        self.setLayout(lay)
        self.setFixedSize(sw, sh)
        self.setStyleSheet("background-color:black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateStatus)
        self.timer.start(100)

    def updateStatus(self, *args):
        try:
            with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as f:
                self.label.setText(f.read())
        except FileNotFoundError:
            self.label.setText("")

    def _load_icon(self, name, w=60, h=60):
        p = QPixmap(GraphicsDirectoryPath(name))
        if p.isNull(): return
        self.icon.setPixmap(p.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def toggle_icon(self, event=None):
        if self.toggled:
            self._load_icon('Mic_on.png', 60, 60)
            MicButtonInitialed()
        else:
            self._load_icon('Mic_off.png', 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            desktop = QApplication.desktop()
            rect = desktop.screenGeometry()
            sw, sh = rect.width(), rect.height()
        except Exception:
            sw, sh = 1280, 720
        layout = QVBoxLayout()
        layout.addWidget(QLabel(""))
        layout.addWidget(ChatSection())
        self.setLayout(layout)
        self.setStyleSheet("background-color:black;")
        self.setFixedSize(sw, sh)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked = stacked_widget
        self._init()

    def _init(self):
        self.setFixedHeight(50)
        bar = QHBoxLayout(self); bar.setAlignment(Qt.AlignRight)

        home = QPushButton(); home.setIcon(QIcon(GraphicsDirectoryPath("Home.png"))); home.setText("  Home")
        home.setStyleSheet("height:40px; line-height:40px; background-color:white; color:black")

        chat = QPushButton(); chat.setIcon(QIcon(GraphicsDirectoryPath("Chats.png"))); chat.setText("  Chat")
        chat.setStyleSheet("height:40px; line-height:40px; background-color:white; color:black")

        minb = QPushButton(); minb.setIcon(QIcon(GraphicsDirectoryPath("Minimize2.png"))); minb.setStyleSheet("background-color:white")
        minb.clicked.connect(self.parent().showMinimized)

        self.maxb = QPushButton()
        self.icon_max = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.icon_restore = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maxb.setIcon(self.icon_max); self.maxb.setFlat(True); self.maxb.setStyleSheet("background-color:white")
        self.maxb.clicked.connect(self.toggleMax)

        closeb = QPushButton(); closeb.setIcon(QIcon(GraphicsDirectoryPath("Close.png"))); closeb.setStyleSheet("background-color:white")
        closeb.clicked.connect(self.parent().close)

        title = QLabel(f" {str(Assistantname).capitalize()} AI")
        title.setStyleSheet("color:black; font-size:18px; background-color:white")

        home.clicked.connect(lambda: self.stacked.setCurrentIndex(0))
        chat.clicked.connect(lambda: self.stacked.setCurrentIndex(1))

        bar.addWidget(title); bar.addStretch(1)
        bar.addWidget(home); bar.addWidget(chat); bar.addStretch(1)
        bar.addWidget(minb); bar.addWidget(self.maxb); bar.addWidget(closeb)

        self.draggable = True
        self.offset = None

    def paintEvent(self, e):
        QPainter(self).fillRect(self.rect(), Qt.white)
        super().paintEvent(e)

    def toggleMax(self):
        if self.parent().isMaximized():
            self.parent().showNormal(); self.maxb.setIcon(self.icon_max)
        else:
            self.parent().showMaximized(); self.maxb.setIcon(self.icon_restore)

    def mousePressEvent(self, ev):
        if self.draggable: self.offset = ev.pos()
    def mouseMoveEvent(self, ev):
        if self.draggable and self.offset:
            self.parent().move(ev.globalPos() - self.offset)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._init()

    def _init(self):
        try:
            desktop = QApplication.desktop()
            rect = desktop.screenGeometry()
            sw, sh = rect.width(), rect.height()
        except Exception:
            sw, sh = 1280, 720
        stacked = QStackedWidget(self)
        stacked.addWidget(InitialScreen())
        stacked.addWidget(MessageScreen())
        self.setGeometry(0, 0, sw, sh)
        self.setStyleSheet("background-color:black;")
        self.setMenuWidget(CustomTopBar(self, stacked))
        self.setCentralWidget(stacked)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()
