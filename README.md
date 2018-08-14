PedicleScrewSimulator
=====================

3D Slicer module for pedicle screw insertion training.

Tutorial
========

- Switch to Pedicle Screw Simulator module (in Training category)
- Click "Load sample spine CT" button to load a sample image or import from DICOM or other file formats (.nrrd, .mha, ...)

![](doc\Screenshot-01-LoadImage.png)

- Click-and-drag colored spheres in slice views or 3D view to define region that contains vertebrae to be treated
- Select starting vertebral level and number of treated vertebrae
- Mark insertion point of each screw on the corresponding vertebra surface
- Measure pedicle length and width to help screw size selection in a later step

![](doc\Screenshot-02-Measure.png)

For each insertion site:
- Select screw length and width and click "Load screw"
- Adjust vertical and horizontal angle and click "Insert screw"

![](doc/Screenshot-03-Insertion.png)

Click "Grade screws" to get detailed analysis of bone contact:

![](doc/Screenshot-04-Analysis.png)