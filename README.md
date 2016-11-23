# CIMAS
Cardiac Image Multi-Atlas Segmentation pipeline (CIMAS)

## What is CIMAS
CIMAS is a pipeline for cardiac MR image segmentation using multi-atlas segmentation method. It assumes that the target image (image under segmentation) shares a similar anatomy as the atlas image (image with corresponding segmentation or label map) and the difference between target and atlas can be described by a spatial transformation. To segment the target image, image registration is performed to estimate this spatial transformation and then atlas label map is propagated onto the target image to form the segmentation. To improve robustness and accuracy, multiple atlases are used in this process. Each atlas acts as an expert and provides a segmentation result. The segmentation results from multiple atlases are combined in a label fusion process.

## System requirements

There are a few binary files which are pre-compiled on Ubuntu 16.04. So it is recommended to run the pipeline on a Ubuntu 16.04 machine. I have also tested that these binaries work on Ubuntu 14.04. 

## Software and data dependencies
We use the [MIRTK](https://github.com/BioMedIA/MIRTK) library for performing image registration and 20 3D MR images acquired from Hammersmith Hospital, Imperial College London as the atlas set. The 20 atlases have been manually segmented by experienced radiologists.

To initialise image registration, we use six landmarks and perform point-based registration, which is then followed by image-based registration. The landmarks are defined as in the [placing the landmarks](http://wp.doc.ic.ac.uk/wbai/data) section and they are manually selected using the [rview](https://www.doc.ic.ac.uk/~dr/software/download.html) software. Alternatively, the landmarks can be automatically detected using [stratified decision forests](https://www.doc.ic.ac.uk/~oo2113/publication/TMI_stratified/) developed by Ozan Oktay.

## Installation steps

1. git clone this repository
 
2. Download and install [MIRTK](https://github.com/BioMedIA/MIRTK).

3. Download the binary file [rview](https://www.doc.ic.ac.uk/~dr/software/download.html).

4. Download some binary programmes [bin](https://drive.google.com/open?id=0B9KJVuWe-M2oU1ZEbzh0TEJvd28) for image processing. These binaries are compiled for *Ubuntu 16.04*. I plan to replace them using Python in the future.

5. Download data, including the [atlas set](https://drive.google.com/open?id=0B9KJVuWe-M2oeHBIX19UYjY2c0k), the [mean template](https://drive.google.com/open?id=0B9KJVuWe-M2oNHpTR2xGQ3M2MEU) and the [test data](https://drive.google.com/open?id=0B9KJVuWe-M2oWnhydEhGQzNqdWM).

## How to run
Set the environment variable $PATH for MIRTK, rview and bin. Decompress the atlas set, mean template and test data and put them in the same directory as the git repository. Set the data path in config.py. Go to the git repository. Then simply run the following command to segment the test data:

```
python seg.py test_data/sa.nii.gz test_data/lm.vtk test_data/
```

The output of the segmentation pipeline is stored in test_data directory, including segmentation results and fitted meshes.

## How to cite
The pipeline is developed with a collaborative effort by computing people (Dr Wenjia Bai, Dr Wenzhe Shi, Ozan Oktay and Prof. Daniel Rueckert) at Biomedical Image Analysis Group at Department of Computing, Imperial College London and imaging people (Dr Declan O'Regan, Dr Antonio de Marvao, Dr Tim Dawes and Prof. Stuart Cook) at the MRC Clinical Sciences Centre, Hammersmith Hospital, Imperial College London. In the event you find the pipeline or a certain part of it useful, please consider giving appropriate credit to it by citing one or some of the following relevant papers, which respectively describes the segmentation method [1], image registration method [2], landmark detection algorithm [3], the mean template [4] and the image acquisition protocol and clinical background [5]. Thank you.

[1] W. Bai, W. Shi, D.P. O’Regan, T. Tong, H. Wang, S. Jamil-Copley, N.S. Peters and D. Rueckert. A probabilistic patch-based label fusion model for multi-atlas segmentation with registration refinement: Application to cardiac MR images. IEEE Transactions on Medical Imaging, 32(7):1302-1315, 2013. [[doi]](http://dx.doi.org/10.1109/TMI.2013.2256922)

[2] D. Rueckert, L.I. Sonoda, C. Hayes, D.L.G. Hill, M.O. Leach, and D.J. Hawkes. Non-rigid registration using free-form deformations: Application to breast MR images. IEEE Transactions on Medical Imaging, 18(8):712-721, 1999. [[doi]](http://dx.doi.org/10.1109/42.796284)

[3] O. Oktay, W. Bai, R. Guerrero, M. Rajchl, A. de Marvao, D. O’Regan, S. Cook, M. Heinrich, B. Glocker, and D. Rueckert. Stratified decision forests for accurate anatomical landmark localization in cardiac images. IEEE Transactions on Medical Imaging, 2016. [[doi]](http://dx.doi.org/10.1109/TMI.2016.2597270) 

[4] W. Bai, W. Shi, A. de Marvao, T.J.W. Dawes, D.P. O’Regan, S.A. Cook, D. Rueckert. A bi-ventricular cardiac atlas built from 1000+ high resolution MR images of healthy subjects and an analysis of shape and motion. Medical Image Analysis, 26(1):133-145, 2015. [[doi]](http://dx.doi.org/10.1016/j.media.2015.08.009)

[5] A. de Marvao, T. Dawes, W. Shi, C. Minas, N.G. Keenan, T. Diamond, G. Durighel, G. Montana, D. Rueckert, S.A. Cook, D.P. O'Regan. Population-based studies of myocardial hypertrophy: high resolution cardiovascular magnetic resonance atlases improve statistical power. J Cardiovasc Magn Reson, 16:16, 2014. [[doi]](http://dx.doi.org/10.1186/1532-429x-16-16)