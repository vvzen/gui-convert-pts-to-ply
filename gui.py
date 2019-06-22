# -*- coding: utf-8 -*-
import os
import re
import sys

from PySide2 import QtCore as qtc
from PySide2 import QtGui as qtg
from PySide2 import QtWidgets as qtw

import conversion

SUPPORTED_FORMATS = ['.pts']

# set correct script dir if it's bundled into an app or run through python
if getattr(sys, 'frozen', False):
    SCRIPT_DIR = os.path.dirname(sys.executable)
elif __file__:
    SCRIPT_DIR = os.path.dirname(__file__)


class ConvertPTSMainWindow(qtw.QMainWindow):

    def __init__(self, version, w=500, h=300):
        super(ConvertPTSMainWindow, self).__init__()

        self.version = version
        self.init_ui(width=w, height=h)

        with open(os.path.join(SCRIPT_DIR, 'data', 'style.css'), 'r') as f:
            self.setStyleSheet(f.read())

        self.input_path = None

    def init_ui(self, width, height):
        self.setAcceptDrops(True)
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

        self.master_layout = qtw.QVBoxLayout()

        self.label_hint = qtw.QLabel('drag a file')
        self.label_hint.setObjectName('drag-hint')
        self.label_hint.setAlignment(qtc.Qt.AlignHCenter)

        self.label_in_path = qtw.QLabel('Input path')
        self.le_input_path = qtw.QLineEdit()

        self.label_asset = qtw.QLabel('Asset name')
        self.le_asset_name = qtw.QLineEdit()
        self.le_asset_name.setValidator(
            qtg.QRegExpValidator(qtc.QRegExp(r'\w')))
        self.le_asset_name.textChanged.connect(self.on_asset_name_edited)
        self.le_input_path.setReadOnly(True)

        self.label_out_path = qtw.QLabel(
            'Export dir (will be created if does not exist)')
        self.le_output_path = qtw.QLineEdit()

        self.convert_layout = qtw.QHBoxLayout()
        self.pb_convert = qtw.QPushButton('Convert!')
        self.pb_convert.setObjectName('convert')
        self.pb_convert.clicked.connect(self.on_convert_pressed)
        self.convert_layout.addWidget(self.pb_convert)

        self.master_layout.addWidget(self.label_hint)
        self.master_layout.addWidget(self.label_in_path)
        self.master_layout.addWidget(self.le_input_path)
        self.master_layout.addWidget(self.label_asset)
        self.master_layout.addWidget(self.le_asset_name)
        self.master_layout.addWidget(self.label_out_path)
        self.master_layout.addWidget(self.le_output_path)
        self.master_layout.addLayout(self.convert_layout)
        self.master_layout.addStretch()

        self.main_widget = qtw.QWidget()
        self.main_widget.setLayout(self.master_layout)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle('Convert Pts to Ply')
        self.statusBar().showMessage(
            'convert-pts-to-ply {version}'.format(version=self.version))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        urls = event.mimeData().urls()

        path = urls[0].path()
        path = os.path.realpath(path)
        print 'dragged path: {}'.format(path)

        # Replace wrong leading slash on windows shares
        if sys.platform == 'win32':
            if path[0] == '/':
                path = path[1:]

        if not path.endswith('.pts') and not urls[0].path().endswith('.ptx'):
            return

        self.input_path = path
        input_file_name, ext = os.path.splitext(
            os.path.basename(self.input_path))

        print 'ext: {}'.format(ext)

        if ext not in SUPPORTED_FORMATS:
            box = qtw.QMessageBox(self)
            box.setIcon(qtw.QMessageBox.Warning)
            box.setText('Unsupported format')
            box.setInformativeText(
                'This application only accepts files with the {} extension!'.
                format(' or '.join(SUPPORTED_FORMATS)))

            box.setWindowTitle('Warning')
            box.exec_()

            return

        self.le_input_path.setText(self.input_path)
        self.le_asset_name.setText(input_file_name)
        self.set_output_dir(self.le_asset_name.text())

    def on_asset_name_edited(self, assetname):

        if self.input_path is None:
            return

        if assetname != '':
            asset_name = assetname
        else:
            asset_name = 'export'

        self.label_hint.setHidden(True)
        self.set_output_dir(asset_name)

    def set_output_dir(self, assetname):

        out_path = os.path.join(
            os.path.dirname(self.input_path),
            '{assetname}.ply'.format(assetname=assetname))

        self.le_output_path.setText(out_path)

    def on_convert_pressed(self):

        # TODO: check input path
        output_path = self.le_output_path.text()
        output_dir = os.path.dirname(output_path)

        if output_dir == '':
            return

        if os.path.exists(output_path):
            box = qtw.QMessageBox(self)
            box.setIcon(qtw.QMessageBox.Warning)
            box.setText('File exists')
            box.setInformativeText(
                'Output file ({}) already exists, please delete it before launching the conversion!'
                .format(output_path))

            box.setWindowTitle('Warning')
            box.exec_()
            return

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        convert_thread = conversion.ConvertPtxThread(self.input_path,
                                                     output_path,
                                                     self.le_asset_name.text())

        self.progress_dialog = qtw.QProgressDialog("Converting", "Abort", 0,
                                                   100, self)
        self.progress_dialog.setWindowModality(qtc.Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.show()

        convert_thread.signals.completed.connect(self.on_convert_completed)
        convert_thread.signals.started.connect(self.on_convert_started)
        convert_thread.signals.progress.connect(self.on_convert_progress)
        convert_thread.signals.failed.connect(self.on_convert_failed)
        qtc.QThreadPool.globalInstance().start(convert_thread)

    def on_convert_started(self, maxvalue):
        print 'setting max value to {}'.format(maxvalue)
        self.progress_dialog.setMaximum(maxvalue)

    def on_convert_progress(self, value):
        self.progress_dialog.setValue(value)

    def on_convert_completed(self):
        self.progress_dialog.close()

        box = qtw.QMessageBox(self)
        box.setIcon(qtw.QMessageBox.Information)
        box.setText('Conversion completed!')
        box.setInformativeText('Everything went smooth. Nice. :)')

        box.setWindowTitle('All good')
        box.exec_()

    def on_convert_failed(self, messag):
        self.progress_dialog.close()

        box = qtw.QMessageBox(self)
        box.setIcon(qtw.QMessageBox.Warning)
        box.setText('Conversion failed!')
        box.setInformativeText(messag)

        box.setWindowTitle('Error')
        box.exec_()
