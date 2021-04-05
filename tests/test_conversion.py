from __future__ import print_function

import os
import sys
import filecmp
from pathlib import Path

import pytest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(CURRENT_DIR, "..", "src"))

from conversion import ply_to_pts, pts_to_ply

@pytest.mark.parametrize("input_file,output_file", [
    pytest.param("diggers.ply", "diggers.pts"),
    pytest.param("rocks_1.ply", "rocks_1.pts"),
    pytest.param("stalagmites_01.ply", "stalagmites_01.pts")
])
def test_ply_to_pts(tmpdir, input_file, output_file):

    input_path = Path(CURRENT_DIR) / "sample_files" / "ply" / input_file
    output_path = Path(tmpdir) / output_file
    ply_to_pts(input_path, output_path)


@pytest.mark.parametrize("input_file,output_file", [
    pytest.param("diggers.ply", "diggers.pts"),
    pytest.param("rocks_1.ply", "rocks_1.pts")
])
def test_ply_to_pts_comparison(tmpdir, input_file, output_file):

    # tmpdir = Path("tmp") / "pytest" / "ply_to_pts_comparison"
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)

    input_path = Path(CURRENT_DIR) / "sample_files" / "ply" / input_file
    output_path = Path(tmpdir) / output_file
    compared_path = Path(CURRENT_DIR) / "sample_files" / "pts" / output_file

    print("compared_path: %s" % compared_path)

    ply_to_pts(input_path, output_path)

    assert filecmp.cmp(output_path, compared_path) is True

@pytest.mark.parametrize("input_file,output_file", [
    pytest.param("diggers.pts", "diggers.ply"),
    pytest.param("rocks_1.pts", "rocks_1.ply"),
    pytest.param("cave.pts", "cave.ply")
])
def test_pts_to_ply(tmpdir, input_file, output_file):

    input_path = Path(CURRENT_DIR) / "sample_files" / "pts" / input_file
    output_path = Path(tmpdir) / output_file
    pts_to_ply(input_path, output_path)

