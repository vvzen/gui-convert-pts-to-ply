#-*- coding: utf-8 -*-
import os
import re
import sys

COORDS_ROW_REGEX = re.compile(
    r'(-)?(\d+\.\d+ \d+\.\d+ \d+\.\d+) (\d+ \d+ \d+ \d+)')

PROGRESS_STEP = 1000

PLY_HEADER = """ply
format ascii 1.0
comment export ply from pts using python (by vvz3n)
element vertex /total_vertices/
comment /asset_name/
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
"""

from PySide2 import QtCore as qtc
from PySide2 import QtGui as qtg
from PySide2 import QtWidgets as qtw


#----------------- SIGNALS -----------------
class ConvertPtxSignals(qtc.QObject):
    started = qtc.Signal(int)
    completed = qtc.Signal()
    progress = qtc.Signal(int)
    failed = qtc.Signal(str)


#----------------- THREADS -----------------
class ConvertPtxThread(qtc.QRunnable):

    def __init__(self, inpath, outpath, assetname):
        super(ConvertPtxThread, self).__init__()

        self.in_path = inpath
        self.out_path = outpath
        self.asset_name = assetname
        self.signals = ConvertPtxSignals()

    def run(self):

        i = 0

        lines_in_buffer = []
        total_lines_num = None

        output_file = open(self.out_path, 'a')

        with open(self.in_path, 'r') as f:
            for line in f:

                if i % PROGRESS_STEP == 0:
                    self.signals.progress.emit(i)

                # First line contains number of points
                if i == 0:
                    total_lines = str(line)

                    print 'total lines: {}\n'.format(total_lines)

                    header = PLY_HEADER.replace('/total_vertices/', total_lines)
                    header = header.replace('/asset_name/', self.asset_name)

                    # Write the header for the ply file
                    output_file.write(header)

                    try:
                        total_lines_num = int(total_lines.strip().replace(
                            '\n', ''))

                        self.signals.started.emit(total_lines_num)

                    except ValueError:
                        self.signals.failed.emit(
                            'Header of file does not contain total vertices number'
                        )
                        return
                else:

                    if i % PROGRESS_STEP == 0:
                        sys.stdout.write('\r{} / {}'.format(i, total_lines))

                    xyz_values = ' '.join(line.split(' ')[:3])
                    rgb_values = ' '.join(line.split(' ')[4:])

                    new_ply_line = '{xyz} {rgb}'.format(
                        xyz=xyz_values, rgb=rgb_values)

                    output_file.write(new_ply_line)

                i += 1

            print 'written {} lines!\n'.format(i)
            output_file.close()

        self.signals.completed.emit()