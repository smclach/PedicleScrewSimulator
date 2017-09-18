cmake_minimum_required(VERSION 3.5)

project(PedicleScrewSimulator)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/PedicleScrewSimulator")
set(EXTENSION_CATEGORY "Training")
set(EXTENSION_CONTRIBUTORS "Brendan Polley (University of Toronto), Stewart McLachlin (Sunnybrook Research Institute), Cari Whyne (Sunnybrook Research Institute)")
set(EXTENSION_DESCRIPTION "3D Slicer module for pedicle screw insertion training")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/PedicleScrewSimulator.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/PedicleScrewSimulator/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(PedicleScrewSimulator)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
