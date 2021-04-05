#-*- coding: utf-8 -*-
from __future__ import print_function

import os
import re
import sys

from PySide2 import QtCore as qtc
from PySide2 import QtGui as qtg
from PySide2 import QtWidgets as qtw

from constants import (
                CONVERSION_DIRECTION, COORDS_ROW_REGEX,
                REGEX_NUM_VERTICES, REGEX_PLY_PROPERTY,
                REGEX_PLY_LIST_PROPERTY, DEFAULT_PTS_INTENSITY_VALUE,
                DEFAULT_PTS_PROPERTY_VALUE, PLY_HEADER_TEMPLATE)

PROGRESS_STEP = 1000

def pts_to_ply(in_path, out_path, comment, signals):

    i = 0

    total_lines_num = None

    output_file = open(out_path, 'a')

    with open(in_path, 'r') as f:
        for line in f:

            if i % PROGRESS_STEP == 0:
                signals.progress.emit(i)

            # First line contains number of points
            if i == 0:
                total_lines = str(line)

                print('total lines: {}\n'.format(total_lines))

                header = PLY_HEADER_TEMPLATE.replace('/total_vertices/', total_lines)
                if comment:
                    header = header.replace('/optional_comment/', comment)
                else:
                    header = header.replace('/optional_comment/',
                                            "export ply from pts "
                                            "using python (by vvz3n)")

                output_file.write(header)

                try:
                    total_lines_num = int(total_lines.strip().replace(
                        '\n', ''))

                    signals.started.emit(total_lines_num)

                except ValueError:
                    signals.failed.emit(
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

        sys.stdout.write('written {} lines!\n'.format(i))
        output_file.close()

def ply_to_pts(source_file, target_file, signals):

    sys.stdout.write("Starting..")

    should_parse_header = True
    reached_end_of_header = False
    found_num_vertices = False
    total_vertices = None
    vertices_lines_written = 0

    ply_properties_map = {
        "x": False,
        "y": False,
        "z": False,
        "red": False,
        "green": False,
        "blue": False,
        "nx": False,
        "ny": False,
        "nz": False,
    }
    pts_properties_source_order = {
        "x": -1,
        "y": -1,
        "z": -1,
        "intensity": -1,
        "red": -1,
        "green": -1,
        "blue": -1
    }
    pts_properties_target_order = [
        "x", "y", "z", "intensity", "red", "green", "blue"
    ]

    source_buffer = open(source_file, "r")

    if not os.path.exists(os.path.dirname(target_file)):
        os.makedirs(os.path.dirname(target_file))

    target_buffer = open(target_file, "w")

    property_index = -1

    try:
        # TODO: based on the header, bail out if it's not a ASCII ply
        print("Parsing header..")

        line = True
        lines_read = 0
        while line:
            line = source_buffer.readline()
            lines_read += 1

            # if lines_read > 23:
            #     print("property_index: %s", property_index)
            #     break

            reached_end_of_header = "end_header" in line
            if reached_end_of_header:
                print("Reached end of header, parsing file content..")
                # print("pts_properties_source_order: %s", pts_properties_source_order)
                should_parse_header = False
                continue

            # Parse the header -------------------------------------------------
            if should_parse_header:
                total_vertices = REGEX_NUM_VERTICES.match(line)
                if total_vertices:
                    total_vertices = total_vertices.group("num")
                    print("Found vertices num: %s", total_vertices)
                    found_num_vertices = True
                    target_buffer.write(total_vertices)
                    target_buffer.write("\n")
                    signals.started.emit(total_vertices)
                    continue

                # We don't care for List properties
                if REGEX_PLY_LIST_PROPERTY.match(line):
                    continue

                property_description = REGEX_PLY_PROPERTY.match(line)
                if property_description:
                    property_name = property_description.group("pname")
                    property_index += 1
                    try:
                        ply_properties_map[property_name] = True
                    except KeyError:
                        sys.stderr.write("Non supported PLY property "
                                         "detected: %s\n" % property_name)
                        continue

                    print("property name: %s", property_name)
                    if pts_properties_source_order.get(property_name):
                        pts_properties_source_order[property_name] = property_index
                        continue

            if not should_parse_header and not found_num_vertices:
                # TODO: the header is over, but haven't found the
                # line containing the num of vertices.. bail out!
                raise RuntimeError(
                    "Didn't find the 'element vertex' directive "
                    "in the header of the source .ply , but this is a required "
                    "property! Please double check the source file is "
                    "formatted properly.")

            # Append the actual values -----------------------------------------
            if should_parse_header:
                continue

            current_values = [v for v in line.split(" ") if v != "\n"]
            if not current_values or current_values == [""]:
                continue
            # print("current_values: %s", current_values)

            if vertices_lines_written % PROGRESS_STEP == 0:
                    sys.stdout.write('\r%s / %s' % (vertices_lines_written,
                                                    total_vertices))

            # Read properties using the original ordering
            # but write them in the pts expected order
            # If there PTS properties that we need to fill in but were not
            # not found in our source PLY, we set them to a default value
            line_to_write = []
            for _, pts_prop in enumerate(pts_properties_target_order):
                source_index = pts_properties_source_order.get(pts_prop)
                # print("pts_prop: %s, source_index: %s", pts_prop, source_index)

                if source_index == -1:
                    if pts_prop == "intensity":
                        line_to_write.append(DEFAULT_PTS_INTENSITY_VALUE)
                    else:
                        line_to_write.append(DEFAULT_PTS_PROPERTY_VALUE)
                    continue

                try:
                    prop_value = current_values[source_index]
                    # print("prop_value: %s", prop_value)
                except IndexError as err:
                    sys.stderr.write(err + "\n")
                    sys.stderr.write("source index: %s\n", source_index)
                    sys.stderr.write("lines_read: %i\n", lines_read)
                    raise

                line_to_write.append(prop_value)

            # print("line_to_write: %s\n", line_to_write)
            target_buffer.write(" ".join(line_to_write))
            target_buffer.write("\n")
            vertices_lines_written += 1

        detected_ply_props = sorted([
            k for k,v in ply_properties_map.items()
            if v
        ])
        detected_pts_props = sorted([
            k for k,v in ply_properties_map.items()
            if v and k in pts_properties_target_order
        ])
        print("Detected PLY properties: %s" % detected_ply_props)
        print("Detected PTS properties: %s" % detected_pts_props)

    finally:
        source_buffer.close()
        target_buffer.close()

# SIGNALS ----------------------------------------------------------------------
class ConvertPtxSignals(qtc.QObject):
    started = qtc.Signal(int)
    completed = qtc.Signal()
    progress = qtc.Signal(int)
    failed = qtc.Signal(str)

# THREADS ----------------------------------------------------------------------
class ConvertPtxThread(qtc.QRunnable):

    def __init__(self, inpath, outpath, direction, comment=""):
        super(ConvertPtxThread, self).__init__()

        self.in_path = inpath
        self.out_path = outpath
        self.comment = comment
        self.signals = ConvertPtxSignals()
        self.direction = direction
        self.pts_to_ply = pts_to_ply

    def run(self):

        try:
            if self.direction == CONVERSION_DIRECTION.PTS_TO_PLY:
                print("converting from PTS to PLY..")
                pts_to_ply(self.in_path, self.out_path, self.comment, self.signals)

            elif self.direction == CONVERSION_DIRECTION.PLY_TO_PTS:
                print("converting from PLY to PTS..")
                ply_to_pts(self.in_path, self.out_path, self.signals)

        except Exception as err:
            sys.stderr.write("Exception encountered!\n")
            sys.stderr.write(err)
            self.signals.failed.emit(err)

        self.signals.completed.emit()