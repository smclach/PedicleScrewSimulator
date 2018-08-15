#-----------------------------------------------------------------------------
set(MODULE_NAME PedicleScrewSimulator)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  PedicleScrewSimulatorWizard/__init__.py
  PedicleScrewSimulatorWizard/DefineROIStep.py
  PedicleScrewSimulatorWizard/EndStep.py
  PedicleScrewSimulatorWizard/GradeStep.py
  PedicleScrewSimulatorWizard/Helper.py
  PedicleScrewSimulatorWizard/LandmarksStep.py
  PedicleScrewSimulatorWizard/LoadDataStep.py
  PedicleScrewSimulatorWizard/MeasurementsStep.py
  PedicleScrewSimulatorWizard/PedicleScrewSimulatorStep.py
  PedicleScrewSimulatorWizard/ScrewStep.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/Icons/${MODULE_NAME}.png
  Resources/ScrewModels/scaled_475x30.vtk
  Resources/ScrewModels/scaled_475x35.vtk
  Resources/ScrewModels/scaled_475x40.vtk
  Resources/ScrewModels/scaled_475x45.vtk
  Resources/ScrewModels/scaled_550x30.vtk
  Resources/ScrewModels/scaled_550x40.vtk
  Resources/ScrewModels/scaled_550x45.vtk
  Resources/ScrewModels/scaled_625x35.vtk
  Resources/ScrewModels/scaled_625x40.vtk
  Resources/ScrewModels/scaled_625x45.vtk
  Resources/ScrewModels/scaled_625x50.vtk
  Resources/ScrewModels/scaled_700x35.vtk
  Resources/ScrewModels/scaled_700x40.vtk
  Resources/ScrewModels/scaled_700x45.vtk
  Resources/ScrewModels/scaled_700x50.vtk
  "Resources/ScrewModels/screw head.vtk"
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py)

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
