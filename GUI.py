from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys, os

# === Load environment variables ===
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Assistant")

# === Directory setup ===
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
TempDirPath = os.path.join(project_root, "Frontend", "Files")
GraphicsDirPath = os.path.join(project_root, "Frontend", "Graphics")
old_chat_message = ""

# === Safe file path helpers ===
def safe_path(base, filename):
    return os.path.join(base, filename)

def safe_read(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""
    except Exception:
        return ""

def safe_write(path, text):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Write error: {e}")

# === Utility functions ===
def GraphicsDirectoryPath(filename): return safe_path(GraphicsDirPath, filename)
def TempDirectoryPath(filename): return safe_path(TempDirPath, filename)
def SetMicrophoneStatus(command): safe_write(TempDirectoryPath("Mic.data"), command)
def GetMicrophoneStatus(): return safe_read(TempDirectoryPath("Mic.data"))
def SetAssistantStatus(status): safe_write(TempDirectoryPath("Status.data"), status)
def GetAssistantStatus(): return safe_read(TempDirectoryPath("Status.data"))
def ShowTextToScreen(text): safe_write(TempDirectoryPath("Responses.data"), text)

# === GUI Classes ===
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        # Text area
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        text_color = QColor(Qt.blue)
        fmt = QTextCharFormat()
        fmt.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(fmt)

        # === Animated GIF (Jinx) ===
        self.gif_label = QLabel()
        gif_path = GraphicsDirectoryPath('Jinx.gif')
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(480, 270))
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setText("[Jinx animation missing]")
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(self.gif_label)

        # === Status label ===
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right:195px; border:none; margin-top:-30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        self.setStyleSheet("background-color:red;")

        # === Auto refresh timer ===
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

    def loadMessages(self):
        global old_chat_message
        messages = safe_read(TempDirectoryPath("Responses.data"))
        if messages and messages != old_chat_message:
            self.addMessage(messages, "white")
            old_chat_message = messages

    def SpeechRecogText(self):
        self.label.setText(GetAssistantStatus())

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        fmt = QTextCharFormat()
        block_fmt = QTextBlockFormat()
        block_fmt.setTopMargin(10)
        block_fmt.setLeftMargin(10)
        fmt.setForeground(QColor(color))
        cursor.setCharFormat(fmt)
        cursor.setBlockFormat(block_fmt)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 150)

        # === Jinx animation ===
        gif_label = QLabel()
        gif_path = GraphicsDirectoryPath('Jinx.gif')
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(screen_width, int(screen_width / 16 * 9)))
            gif_label.setMovie(movie)
            movie.start()
        else:
            gif_label.setText("[Jinx.gif missing]")
        gif_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(gif_label, alignment=Qt.AlignCenter)

        # === Status label ===
        self.label = QLabel("")
        self.label.setStyleSheet("color:white; font-size:16px;")
        layout.addWidget(self.label, alignment=Qt.AlignCenter)

        # === Mic button ===
        self.icon_label = QLabel()
        self.toggled = True
        self.load_icon(GraphicsDirectoryPath("Mic_on.png"))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.mousePressEvent = self.toggle_icon
        layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.setStyleSheet("background-color:red;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

    def SpeechRecogText(self):
        self.label.setText(GetAssistantStatus())

    def load_icon(self, path, width=60, height=60):
        if os.path.exists(path):
            pixmap = QPixmap(path).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText("[Icon missing]")

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("Mic_on.png"))
            SetMicrophoneStatus("False")
        else:
            self.load_icon(GraphicsDirectoryPath("Mic_off.png"))
            SetMicrophoneStatus("True")
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(ChatSection())
        self.setLayout(layout)
        self.setStyleSheet("background-color:red;")


class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)

        title_label = QLabel(f" {Assistantname} AI")
        title_label.setStyleSheet("color:black; font-size:18px; background-color:white")

        def create_btn(icon_name, text="", callback=None):
            btn = QPushButton(text)
            icon_path = GraphicsDirectoryPath(icon_name)
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
            btn.setStyleSheet("background-color:white; color:red; height:40px;")
            if callback:
                btn.clicked.connect(callback)
            return btn

        home_button = create_btn("Home.png", "  Home", lambda: self.stacked_widget.setCurrentIndex(0))
        message_button = create_btn("Chats.png", "  Chat", lambda: self.stacked_widget.setCurrentIndex(1))
        minimize_button = create_btn("Minimize2.png", callback=self.minimizeWindow)
        self.maximize_button = create_btn("Maximize.png", callback=self.maximizeWindow)
        close_button = create_btn("Close.png", callback=self.closeWindow)

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self): self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()

    def closeWindow(self): self.parent().close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        stacked_widget.addWidget(InitialScreen())
        stacked_widget.addWidget(MessageScreen())
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color:red;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()
