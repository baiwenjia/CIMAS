# CIMAS
Cardiac Image Multi-Atlas Segmentation (CIMAS)

## What is CIMAS
CIMAS is a pipeline for cardiac MR image segmentation using multi-atlas segmentation method. It assumes that the target image (image under segmentation) shares a similar anatomy as the atlas image (image with corresponding segmentation or label map) and the difference between target and atlas can be described by a spatial transformation. To segment the target image, image registration is performed to estimate this spatial transformation and then atlas label map is propagated onto the target image to form the segmentation. To improve robustness and accuracy, multiple atlases can be used in this process. Each atlas acts as an expert and provides a segmentation result. The segmentation results from multiple atlases are combined in a label fusion process.

## Dependencies
We use the [MIRTK](https://github.com/BioMedIA/MIRTK) library for performing image registration and 20 3D MR images acquired from Hammersmith Hospital, Imperial College London as the atlas set. The 20 atlases have been manually segmented by experienced radiologists. To initialise image registration, we use six landmarks and perform point-based registration, which is then followed by image-based registration. The landmarks defined as in the [Placing the landmarks](http://wp.doc.ic.ac.uk/wbai/data) section and they are manually selected using the [rview](https://www.doc.ic.ac.uk/~dr/software/download.html) software.
 
## How to run
To download data ...
Compile MIRTK
Add binaries to path (compiled under Ubuntu 16.04)
To run ...

## How to cite
The pipeline is developed with a collaborative effort by computing people (Dr Wenjia Bai, Dr Wenzhe Shi and Prof. Daniel Rueckert) at Biomedical Image Analysis Group at Department of Computing, Imperial College London and imaging people (Dr Declan O'Regan, Dr Antonio de Marvao, Dr Tim Dawes and Prof. Stuart Cook) at the MRC Clinical Sciences Centre, Hammersmith Hospital, Imperial College London. In the event you find the pipeline or a certain part of it useful, please consider giving appropriate credit to it by citing one or some of the following relevant papers, which describes the segmentation method [1], image registration method [2], the atlas image acquisition protocol and clinical background [3,4]. Thank you.

[1] W. Bai, W. Shi, D.P. O’Regan, T. Tong, H. Wang, S. Jamil-Copley, N.S. Peters and D. Rueckert. A probabilistic patch-based label fusion model for multi-atlas segmentation with registration refinement: Application to cardiac MR images. IEEE Transactions on Medical Imaging, 32(7):1302-1315, 2013.

[2] D. Rueckert, L.I. Sonoda, C. Hayes, D.L.G. Hill, M.O. Leach, and D.J. Hawkes. Non-rigid registration using free-form deformations: Application to breast MR images. IEEE Transactions on Medical Imaging, 18(8):712-721, 1999.

[3] W. Bai, W. Shi, A. de Marvao, T.J.W. Dawes, D.P. O’Regan, S.A. Cook, D. Rueckert. A bi-ventricular cardiac atlas built from 1000+ high resolution MR images of healthy subjects and an analysis of shape and motion. Medical Image Analysis, 26(1):133-145, 2015. doi:10.1016/j.media.2015.08.009

[4] A. de Marvao, T. Dawes, W. Shi, C. Minas, N.G. Keenan, T. Diamond, G. Durighel, G. Montana, D. Rueckert, S.A. Cook, D.P. O'Regan. Population-based studies of myocardial hypertrophy: high resolution cardiovascular magnetic resonance atlases improve statistical power. J Cardiovasc Magn Reson, 16:16, 2014. doi:10.1186/1532-429x-16-16