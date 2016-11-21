"""
Cardiac image multi-atlas segmentation pipeline

Author: Wenjia Bai
First created: 2015.03.31
Last modified: 2016.11.21 by wbai
"""

import sys
import cimas, config


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage: {0} image(.nii.gz) landmarks(.vtk) output_dir'.format(sys.argv[0]))
        exit(1)

    image_name = sys.argv[1]
    landmarks_name = sys.argv[2]
    output_dir = sys.argv[3]
    cimas.segment_data(image_name, landmarks_name, output_dir, \
                       config.atlas_root, config.atlas_list, config.template_dir, config.par_dir)

    # # For debug
    # n_atlas = 5
    # cimas.segment_data(image_name, landmarks_name, output_dir, \
    #                    config.atlas_root, config.atlas_list[:n_atlas], config.template_dir, config.par_dir, remove_temp=False)
