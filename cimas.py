"""
Cardiac image multi-atlas segmentation pipeline

Author: Wenjia Bai
First created: 2015.03.31
Last modified: 2016.11.21 by wbai
"""

import os


def segment_data(image_name, landmarks_name, output_dir, atlas_root, atlas_list, template_dir, par_dir, remove_temp=True):
    # Check files
    if not os.path.exists(image_name):
        print('Error: no image. Please provide the cardiac image.')
        return

    if not os.path.exists(landmarks_name):
        print('Error: no landmarks. Please provide the landmarks.')
        return

    # Create temporary directory for intermediate results in multi-atlas segmentation
    temp_dir = os.path.join(output_dir, 'temp')
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)

    dof_dir = os.path.join(output_dir, 'dof')
    if not os.path.exists(dof_dir):
        os.mkdir(dof_dir)

    # Split temporal sequence and pick the ED and ES time frames
    os.system('splitvolume {0} {1}/sa_fr -sequence'.format(image_name, temp_dir))
    ES = int(os.popen('detect_ES_frame {0}'.format(image_name)).read())
    os.system('cp {0}/sa_fr00.nii.gz {0}/sa_ED.nii.gz'.format(temp_dir))
    os.system('cp {0}/sa_fr{1:02d}.nii.gz {0}/sa_ES.nii.gz'.format(temp_dir, ES))

    # Check the number of atlases
    n_atlas = len(atlas_list)

    # Step 1: multi-atlas segmentation using point-based registration at the ED frame
    # The landmarks can also be automatically detected using Ozan Oktak's method
    image_props = ''
    label_props = ''

    for atlas in atlas_list:
        atlas_dir = os.path.join(atlas_root, atlas)
        os.system('prreg {0} {1}/landmarks.vtk -dofout {2}/prreg_{3}.dof.gz'.format(landmarks_name, atlas_dir, temp_dir, atlas))
        os.system('mirtk transform-image {0}/lvsa_ED.nii.gz {1}/image_ED_prreg_from_{2}.nii.gz \
                -dofin {1}/prreg_{2}.dof.gz -target {1}/sa_ED.nii.gz -interp Linear'.format(atlas_dir, temp_dir, atlas))
        os.system('mirtk transform-image {0}/segmentation_ED.nii.gz {1}/label_ED_prreg_from_{2}.nii.gz \
                -dofin {1}/prreg_{2}.dof.gz -target {1}/sa_ED.nii.gz -interp NN'.format(atlas_dir, temp_dir, atlas))
        image_props += ' {0}/image_ED_prreg_from_{1}.nii.gz'.format(temp_dir, atlas)
        label_props += ' {0}/label_ED_prreg_from_{1}.nii.gz'.format(temp_dir, atlas)

    if not os.path.exists('{0}/seg_ED_prreg_mv.nii.gz'.format(temp_dir)):
        os.system('label_fusion {0}/sa_ED.nii.gz {1} {2} {3} {0}/seg_ED_prreg_mv.nii.gz -method MV'.format( \
                temp_dir, n_atlas, image_props, label_props))

    # Step 2: Pre-processing, including cropping the region of the heart and stretching the intensity histogram
    # Crop the image for two purposes:
    # (1) Save computation time
    # (2) Non-rigid registration can be more accurate since the cost function will focus on the region of interest
    os.system('auto_crop_image {0}/seg_ED_prreg_mv.nii.gz {0}/seg_ED_prreg_mv_crop.nii.gz -reserve 20'.format(temp_dir))
    os.system('region {0}/sa_ED.nii.gz {0}/sa_ED_crop.nii.gz -ref {0}/seg_ED_prreg_mv_crop.nii.gz'.format(temp_dir))
    os.system('region {0}/sa_ES.nii.gz {0}/sa_ES_crop.nii.gz -ref {0}/seg_ED_prreg_mv_crop.nii.gz'.format(temp_dir))

    # Stretch the intensity histogram
    # This step will reduce the intensity range of the image so that in the following image registrations,
    # the bin width of normalised mutual information (NMI) will be smaller and represent the intensities more accurately.
    os.system('stretch_contrast {0}/sa_ED_crop.nii.gz {0}/sa_ED_crop.nii.gz'.format(temp_dir))
    os.system('stretch_contrast {0}/sa_ES_crop.nii.gz {0}/sa_ES_crop.nii.gz'.format(temp_dir))

    # Step 3: multi-atlas segmentation using affine image registration at the ED frame
    target = '{0}/sa_ED_crop.nii.gz'.format(temp_dir)
    image_props = ''
    label_props = ''

    for atlas in atlas_list:
        atlas_dir = os.path.join(atlas_root, atlas)
        if not os.path.exists('{0}/affine_init_ED_{1}.dof.gz'.format(temp_dir, atlas)):
            os.system('mirtk register {0} {1}/lvsa_ED.nii.gz -parin {2}/affine.cfg \
                    -dofin {3}/prreg_{4}.dof.gz -dofout {3}/affine_init_ED_{4}.dof.gz'.format( \
                    target, atlas_dir, par_dir, temp_dir, atlas))
        os.system('mirtk transform-image {0}/lvsa_ED.nii.gz {1}/image_ED_affine_init_from_{2}.nii.gz \
                -dofin {1}/affine_init_ED_{2}.dof.gz -target {3} -interp Linear'.format(atlas_dir, temp_dir, atlas, target))
        os.system('mirtk transform-image {0}/segmentation_ED.nii.gz {1}/label_ED_affine_init_from_{2}.nii.gz \
                -dofin {1}/affine_init_ED_{2}.dof.gz -target {3} -interp NN'.format(atlas_dir, temp_dir, atlas, target))
        image_props += ' {0}/image_ED_affine_init_from_{1}.nii.gz'.format(temp_dir, atlas)
        label_props += ' {0}/label_ED_affine_init_from_{1}.nii.gz'.format(temp_dir, atlas)

    # Cross correlation is used by default as similarity metric in label fusion in case the target image
    # has a different intensity distribution from the atlas image. However, if the target image is acquired
    # using the same protocol as the atlas image, mean squared difference can be a better similarity metric.
    seg = '{0}/seg_ED_affine_init_pbcc.nii.gz'.format(temp_dir)
    if not os.path.exists(seg):
        os.system('label_fusion {0} {1} {2} {3} {4} -method PBCC -par {5}/pbcc.cfg'.format( \
                target, n_atlas, image_props, label_props, seg, par_dir))

    # Step 4: Register label maps to refine affine registration in case landmarks are not detected accurately
    target_seg = seg

    for atlas in atlas_list:
        atlas_dir = os.path.join(atlas_root, atlas)
        if not os.path.exists('{0}/affine_label_ED_{1}.dof.gz'.format(temp_dir, atlas)):
            os.system('mirtk register {0} {1}/segmentation_ED.nii.gz -parin {2}/affine_label.cfg -dofin {3}/prreg_{4}.dof.gz \
                    -dofout {3}/affine_label_ED_{4}.dof.gz'.format(target_seg, atlas_dir, par_dir, temp_dir, atlas))

    # For each time frame
    for fr in ['ED', 'ES']:
        # Image to be segmented
        target = '{0}/sa_{1}_crop.nii.gz'.format(temp_dir, fr)

        # Step 5: multi-atlas segmentation based on non-rigid image registration
        image_props = ''
        label_props = ''

        for atlas in atlas_list:
            atlas_dir = os.path.join(atlas_root, atlas)
            if not os.path.exists('{0}/ffd_{1}_{2}.dof.gz'.format(temp_dir, fr, atlas)):
                os.system('mirtk register {0} {1}/lvsa_{2}.nii.gz -parin {3}/ffd.cfg \
                        -dofin {4}/affine_label_ED_{5}.dof.gz -dofout {4}/ffd_{2}_{5}.dof.gz'.format( \
                        target, atlas_dir, fr, par_dir, temp_dir, atlas))
            os.system('mirtk transform-image {0}/lvsa_{2}.nii.gz {1}/image_{2}_ffd_from_{3}.nii.gz \
                    -dofin {1}/ffd_{2}_{3}.dof.gz -target {4} -interp Linear'.format(atlas_dir, temp_dir, fr, atlas, target))
            os.system('mirtk transform-image {0}/segmentation_{2}.nii.gz {1}/label_{2}_ffd_from_{3}.nii.gz \
                    -dofin {1}/ffd_{2}_{3}.dof.gz -target {4} -interp NN'.format(atlas_dir, temp_dir, fr, atlas, target))
            image_props += ' {0}/image_{1}_ffd_from_{2}.nii.gz'.format(temp_dir, fr, atlas)
            label_props += ' {0}/label_{1}_ffd_from_{2}.nii.gz'.format(temp_dir, fr, atlas)


        # Cross correlation is used by default as similarity metric in label fusion in case the target image
        # has a different intensity distribution from the atlas image. However, if the target image is acquired
        # using the same protocol as the atlas image, mean squared difference can be a better similarity metric.
        seg = '{0}/seg_{1}_ffd_pbcc_{2}a.nii.gz'.format(temp_dir, fr, n_atlas)
        if not os.path.exists(seg):
            os.system('label_fusion {0} {1} {2} {3} {4} -method PBCC -par {5}/pbcc.cfg'.format( \
                target, n_atlas, image_props, label_props, seg, par_dir))

        # Step 6: Refine image registration based on the segmentation
        target_seg = seg
        image_props = ''
        label_props = ''

        for atlas in atlas_list:
            atlas_dir = os.path.join(atlas_root, atlas)
            if not os.path.exists('{0}/ffd_label_{1}_{2}.dof.gz'.format(temp_dir, fr, atlas)):
                os.system('mirtk register {0} {1}/segmentation_{2}.nii.gz -parin {3}/ffd_label.cfg \
                        -dofin {4}/affine_label_ED_{5}.dof.gz -dofout {4}/ffd_label_{2}_{5}.dof.gz'.format( \
                        target_seg, atlas_dir, fr, par_dir, temp_dir, atlas))
            os.system('mirtk transform-image {0}/lvsa_{2}.nii.gz {1}/image_{2}_ffd_label_from_{3}.nii.gz \
                    -dofin {1}/ffd_label_{2}_{3}.dof.gz -target {4} -interp Linear'.format(atlas_dir, temp_dir, fr, atlas, target))
            os.system('mirtk transform-image {0}/segmentation_{2}.nii.gz {1}/label_{2}_ffd_label_from_{3}.nii.gz \
                    -dofin {1}/ffd_label_{2}_{3}.dof.gz -target {4} -interp NN'.format(atlas_dir, temp_dir, fr, atlas, target))
            image_props += ' {0}/image_{1}_ffd_label_from_{2}.nii.gz'.format(temp_dir, fr, atlas)
            label_props += ' {0}/label_{1}_ffd_label_from_{2}.nii.gz'.format(temp_dir, fr, atlas)

        # Multi-atlas segmentation
        seg = '{0}/seg_{1}_ffd_label_pbcc_{2}a.nii.gz'.format(temp_dir, fr, n_atlas)
        if not os.path.exists(seg):
            os.system('label_fusion {0} {1} {2} {3} {4} -method PBCC -par {5}/pbcc.cfg'.format( \
                target, n_atlas, image_props, label_props, seg, par_dir))

        # Step 7: Estimate transformation from target to template
        # This will be used for propagating the template segmentation onto the target image
        os.system('prreg {0} {1}/landmarks_ED.vtk -dofout {2}/prreg_template.dof.gz'.format(landmarks_name, template_dir, temp_dir))
        os.system('mirtk invert-dof {0}/prreg_template.dof.gz {0}/prreg_inv_template.dof.gz'.format(temp_dir))

        target_seg = seg
        template_label = '{0}/label_map_{1}.nii.gz'.format(template_dir, fr)

        # Use rigid + ffd
        # If I use affine in between, sometimes affine registration may create very strange transformation results,
        # which moves source image out of the FOV.
        if not os.path.exists('{0}/rigid_label_{1}_template.dof.gz'.format(temp_dir, fr)):
            os.system('mirtk register {0} {1} -parin {2}/rigid_label.cfg -dofin {3}/prreg_template.dof.gz \
                    -dofout {3}/rigid_label_{4}_template.dof.gz'.format(target_seg, template_label, par_dir, temp_dir, fr))
        if not os.path.exists('{0}/ffd_label_{1}_template.dof.gz'.format(temp_dir, fr)):
            os.system('mirtk register {0} {1} -parin {2}/ffd_label_fine.cfg -dofin {3}/rigid_label_{4}_template.dof.gz \
                    -dofout {3}/ffd_label_{4}_template.dof.gz'.format(target_seg, template_label, par_dir, temp_dir, fr))

        seg_fit = '{0}/seg_{1}.nii.gz'.format(temp_dir, fr)
        os.system('mirtk transform-image {0} {1} -dofin {2}/ffd_label_{3}_template.dof.gz \
                -target {2}/sa_{3}.nii.gz -interp NN'.format(template_label, seg_fit, temp_dir, fr))

        # Fit the AHA 17-segment model for the ED phase only
        if fr == 'ED':
            aha_label = '{0}/myo_{1}_AHA17.nii.gz'.format(template_dir, fr)
            aha_fit = '{0}/myo_{1}_AHA17.nii.gz'.format(temp_dir, fr)
            os.system('mirtk transform-image {0} {1} -dofin {2}/ffd_label_{3}_template.dof.gz \
                    -target {2}/sa_{3}.nii.gz -interp NN'.format(aha_label, aha_fit, temp_dir, fr))

        # Step 8: Estimate transformation from template to target
        # This will be used for propagating mesh onto the target image
        # I have found that it can be numerically very unstable to invert a non-rigid transformation,
        # no matter how much care you have taken in performing the registration. So the best solution
        # to propagate the mesh is to perfrom registration from template to target.

        # To ensure the low-resolution segmentation is not too bad for using as a target image in subsequent registration,
        # we upsample the segmentation.
        os.system('resample {0}/sa_{1}.nii.gz {0}/sa_{1}_up.nii.gz -size 1.25 1.25 2 -linear'.format(temp_dir, fr))
        os.system('mirtk transform-image {0}/label_map_{1}.nii.gz {2}/seg_{1}_up.nii.gz \
                -dofin {2}/ffd_label_{1}_template.dof.gz -target {2}/sa_{1}_up.nii.gz -interp NN'.format(template_dir, fr, temp_dir))

        template_label = '{0}/label_map_{1}.nii.gz'.format(template_dir, fr)
        target_seg = '{0}/seg_{1}_up.nii.gz'.format(temp_dir, fr)

        # Use rigid + ffd
        # If I use affine in between, sometimes affine registration may create very strange transformation results,
        # which moves source image out of the FOV.
        if not os.path.exists('{0}/rigid_label_inv_{1}_template.dof.gz'.format(temp_dir, fr)):
            os.system('mirtk register {0} {1} -parin {2}/rigid_label.cfg -dofin {3}/prreg_inv_template.dof.gz \
                    -dofout {3}/rigid_label_inv_{4}_template.dof.gz'.format(template_label, target_seg, par_dir, temp_dir, fr))
        if not os.path.exists('{0}/ffd_label_inv_{1}_template.dof.gz'.format(temp_dir, fr)):
            os.system('mirtk register {0} {1} -parin {2}/ffd_label_fine.cfg -dofin {3}/rigid_label_inv_{4}_template.dof.gz \
                    -dofout {3}/ffd_label_inv_{4}_template.dof.gz'.format(template_label, target_seg, par_dir, temp_dir, fr))

        # Fit the meshes
        for part in ['myo', 'endo', 'epi', 'rv', 'heart']:
            template_mesh = '{0}/{1}_{2}.vtk'.format(template_dir, part, fr)
            mesh_fit = '{0}/{1}_{2}.vtk'.format(temp_dir, part, fr)
            os.system('mirtk transform-points {0} {1} -dofin {2}/ffd_label_inv_{3}_template.dof.gz'.format(template_mesh, mesh_fit, temp_dir, fr))
            os.system('surface_smooth {0} {0} 500 -relaxation 0.01'.format(mesh_fit))

        # Step 8: copy results to the output directory
        os.system('cp {0}/sa_{1}.nii.gz {2}'.format(temp_dir, fr, output_dir))
        os.system('cp {0}/seg_{1}.nii.gz {2}'.format(temp_dir, fr, output_dir))
        os.system('cp {0}/seg_{1}_up.nii.gz {2}'.format(temp_dir, fr, output_dir))
        if fr == 'ED':
            os.system('cp {0}/myo_{1}_AHA17.nii.gz {2}'.format(temp_dir, fr, output_dir))
        for part in ['myo', 'endo', 'epi', 'rv', 'heart']:
            os.system('cp {0}/{1}_{2}.vtk {3}'.format(temp_dir, part, fr, output_dir))
        os.system('cp {0}/rigid_label_{1}_template.dof.gz {2}'.format(temp_dir, fr, dof_dir))
        os.system('cp {0}/rigid_label_inv_{1}_template.dof.gz {2}'.format(temp_dir, fr, dof_dir))
        os.system('cp {0}/ffd_label_{1}_template.dof.gz {2}'.format(temp_dir, fr, dof_dir))
        os.system('cp {0}/ffd_label_inv_{1}_template.dof.gz {2}'.format(temp_dir, fr, dof_dir))

    # Remove temporary directory
    if remove_temp:
        os.system('rm -rf {0}'.format(temp_dir))