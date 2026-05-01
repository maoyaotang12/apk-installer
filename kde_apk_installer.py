#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QTextEdit, QComboBox, QMessageBox, QProgressBar)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class AdbThread(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool)

    def __init__(self, device, apk_path):
        super().__init__()
        self.device = device
        self.apk_path = apk_path

    def run(self):
        try:
            self.log_signal.emit(f"开始安装：{self.apk_path}")
            cmd = ["adb", "-s", self.device, "install", "-r", self.apk_path]
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
            for line in proc.stdout:
                self.log_signal.emit(line.strip())
            proc.wait()
            if proc.returncode == 0:
                self.log_signal.emit("✅ 安装成功")
                self.finished_signal.emit(True)
            else:
                self.log_signal.emit("❌ 安装失败")
                self.finished_signal.emit(False)
        except Exception as e:
            self.log_signal.emit(f"错误：{e}")
            self.finished_signal.emit(False)

class ApkInstaller(QMainWindow):
    def __init__(self, apk_path=None):
        super().__init__()
        self.setWindowTitle("APK 安装器")
        self.setFixedSize(650, 500)

        # ====================== 【关键修复】强制窗口归属 desktop ======================
        self.setProperty("class", "apk-installer")
        self.setObjectName("apk-installer")

        self.center()
        self.apk_path = apk_path if apk_path else ""
        self.device_list = []

        self.ui_setup()
        self.refresh_devices()

        if self.apk_path and os.path.isfile(self.apk_path):
            self.apk_label.setText(os.path.basename(self.apk_path))
            self.log_text.append(f"✅ 已载入APK：{self.apk_path}")

    def ui_setup(self):
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)

        h1 = QHBoxLayout()
        self.dev_combo = QComboBox()
        btn_refresh = QPushButton("🔄 刷新设备")
        btn_refresh.clicked.connect(self.refresh_devices)
        h1.addWidget(QLabel("选择设备："))
        h1.addWidget(self.dev_combo)
        h1.addWidget(btn_refresh)
        lay.addLayout(h1)

        h2 = QHBoxLayout()
        self.apk_label = QLabel("未选择 APK")
        btn_sel = QPushButton("📂 选择APK文件")
        btn_sel.clicked.connect(self.choose_apk)
        h2.addWidget(btn_sel)
        h2.addWidget(self.apk_label)
        lay.addLayout(h2)

        self.btn_install = QPushButton("🚀 开始安装到设备")
        self.btn_install.setStyleSheet("font-size:14px; padding:6px;")
        self.btn_install.clicked.connect(self.do_install)
        lay.addWidget(self.btn_install)

        self.progress = QProgressBar()
        self.progress.setRange(0,0)
        self.progress.hide()
        lay.addWidget(self.progress)

        lay.addWidget(QLabel("安装日志："))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        lay.addWidget(self.log_text)

    def center(self):
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def refresh_devices(self):
        self.dev_combo.clear()
        self.device_list = []
        try:
            out = subprocess.check_output(["adb","devices"], text=True)
            for line in out.splitlines():
                if "\tdevice" in line:
                    dev = line.split("\t")[0]
                    self.device_list.append(dev)
                    self.dev_combo.addItem(dev)
        except:
            self.log_text.append("❌ 未找到ADB")

    def choose_apk(self):
        p, _ = QFileDialog.getOpenFileName(self, "选择APK", "", "APK (*.apk)")
        if p:
            self.apk_path = p
            self.apk_label.setText(os.path.basename(p))
            self.log_text.append(f"✅ 已选择：{p}")

    def do_install(self):
        if not self.device_list:
            QMessageBox.warning(self, "提示", "未检测到设备！")
            return
        if not self.apk_path or not os.path.isfile(self.apk_path):
            QMessageBox.warning(self, "提示", "请选择APK文件！")
            return

        self.btn_install.setEnabled(False)
        self.progress.show()
        dev = self.dev_combo.currentText()
        self.worker = AdbThread(dev, self.apk_path)
        self.worker.log_signal.connect(self.log_text.append)
        self.worker.finished_signal.connect(self.install_end)
        self.worker.start()

    def install_end(self, ok):
        self.btn_install.setEnabled(True)
        self.progress.hide()
        if ok:
            QMessageBox.information(self, "完成", "✅ 安装成功！")
        else:
            QMessageBox.critical(self, "失败", "❌ 安装失败！")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ====================== 【关键】强制应用程序标识 ======================
    app.setDesktopFileName("apk-installer.desktop")
    app.setApplicationName("APK Installer")

    apk_file = sys.argv[1] if len(sys.argv) > 1 else None
    win = ApkInstaller(apk_file)
    win.show()
    sys.exit(app.exec())
