"""
Cardiac multi-atlas segmentation pipeline

Author: Wenjia Bai
First created: 2015.03.31
Last modified: 2016.11.21 by wbai
"""

import os


# Download data ...

# Run it
os.system('python seg.py test_data/sa.nii.gz test_data/lm.vtk test_data/')
