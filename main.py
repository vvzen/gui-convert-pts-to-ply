#-*- coding: utf-8 -*-
__version__ = '1.0.0'
import os
import sys

from PySide2 import QtWidgets as qtw

import gui


def main():

    app = qtw.QApplication(sys.argv)
    window = gui.ConvertPTSMainWindow(__version__)
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()