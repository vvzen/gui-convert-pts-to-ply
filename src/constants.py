# -*- coding: utf-8 -*-
import re

SUPPORTED_FORMATS = ['.pts' , '.ply']

class CONVERSION_DIRECTION(object):
    PTS_TO_PLY = 0
    PLY_TO_PTS = 1


COORDS_ROW_REGEX = re.compile(
    r'(-)?(\d+\.\d+ \d+\.\d+ \d+\.\d+) (\d+ \d+ \d+ \d+)')

# PLY to PTS
REGEX_NUM_VERTICES = re.compile(r"element vertex (?P<num>\d+)")
REGEX_PLY_PROPERTY = re.compile(r"property (\w+) (?P<pname>[a-zA-z]+)")
REGEX_PLY_LIST_PROPERTY = re.compile(r"property list (\w+) (\w+) (?P<pname>[a-zA-z]+)")
DEFAULT_PTS_INTENSITY_VALUE = "100"
DEFAULT_PTS_PROPERTY_VALUE = "255"

# PTS to PLY
PLY_HEADER_TEMPLATE = """ply
format ascii 1.0
element vertex /total_vertices/
comment /optional_comment/
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
end_header
"""