import os
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging

import PedicleScrewSimulatorWizard
import PedicleScrewPlannerWizard
#from PedicleScrewPlannerWizard import *

#
# PedicleScrewPlanner
#

class PedicleScrewPlanner(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Pedicle Screw Planner"
    self.parent.categories = ["Training"]
    self.parent.dependencies = []
    self.parent.contributors = ["Brendan Polley (University of Toronto)",
      "Stewart McLachlin (Sunnybrook Research Institute)",
      "Cari Whyne (Sunnybrook Research Institute)",
      "Jumbo Jing"]
    self.parent.helpText = """
Pedicle Screw Simulator. See more details here: https://github.com/lassoan/PedicleScrewSimulator
"""
    self.parent.acknowledgementText = """
Orthopaedic Biomechanics Laboratory, Sunnybrook Health Sciences Centre.
""" # replace with organization, grant and thanks.

#
# PedicleScrewPlannerWidget
#

class PedicleScrewPlannerWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    self.workflow = ctk.ctkWorkflow()

    workflowWidget = ctk.ctkWorkflowStackedWidget()
    workflowWidget.setWorkflow( self.workflow )

    # create all wizard steps
    self.loadDataStep = PedicleScrewSimulatorWizard.LoadDataStep( 'LoadData'  )
    self.defineROIStep = PedicleScrewSimulatorWizard.DefineROIStep( 'DefineROI', showSidesSelector=True )
    self.measurementsStep = PedicleScrewPlannerWizard.PlanningMeasurementsStep( 'Measurements'  )
    self.landmarksStep = PedicleScrewPlannerWizard.PlanningLandmarksStep( 'Landmarks' )
    # self.screwStep = PedicleScrewSimulatorWizard.ScrewStep( 'Screw' )
    self.gradeStep = PedicleScrewPlannerWizard.PlanningGradeStep( 'Grade' )
    self.endStep = PedicleScrewSimulatorWizard.EndStep( 'Final'  )
    
    # add the wizard steps to an array for convenience
    allSteps = []

    allSteps.append( self.loadDataStep )
    allSteps.append( self.defineROIStep )
    allSteps.append( self.landmarksStep)
    allSteps.append( self.measurementsStep )
    # allSteps.append( self.screwStep)
    allSteps.append( self.gradeStep)
    allSteps.append( self.endStep )
    
    
    # Add transition 
    # Check if volume is loaded
    self.workflow.addTransition( self.loadDataStep, self.defineROIStep )
    
    self.workflow.addTransition( self.defineROIStep, self.landmarksStep, 'pass', ctk.ctkWorkflow.Bidirectional )
    self.workflow.addTransition( self.defineROIStep, self.loadDataStep, 'fail', ctk.ctkWorkflow.Bidirectional  )
    
    self.workflow.addTransition( self.landmarksStep, self.measurementsStep, 'pass', ctk.ctkWorkflow.Bidirectional )
    self.workflow.addTransition( self.landmarksStep, self.measurementsStep, 'fail', ctk.ctkWorkflow.Bidirectional )
    
    # self.workflow.addTransition( self.measurementsStep, self.screwStep, 'pass', ctk.ctkWorkflow.Bidirectional )
    # self.workflow.addTransition( self.measurementsStep, self.screwStep, 'fail', ctk.ctkWorkflow.Bidirectional )
    #
    # self.workflow.addTransition( self.screwStep, self.gradeStep, 'pass', ctk.ctkWorkflow.Bidirectional )
    # self.workflow.addTransition( self.screwStep, self.gradeStep, 'fail', ctk.ctkWorkflow.Bidirectional )
    self.workflow.addTransition( self.measurementsStep, self.gradeStep, 'pass', ctk.ctkWorkflow.Bidirectional )
    self.workflow.addTransition( self.measurementsStep, self.gradeStep, 'fail', ctk.ctkWorkflow.Bidirectional )

    self.workflow.addTransition( self.gradeStep, self.endStep )
           
    nNodes = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLScriptedModuleNode')

    self.parameterNode = None
    for n in range(nNodes):
      compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLScriptedModuleNode')
      nodeid = None
      if compNode.GetModuleName() == 'PedicleScrewPlanner':
        self.parameterNode = compNode
        logging.debug('Found existing PedicleScrewPlanner parameter node')
        break
    if self.parameterNode == None:
      self.parameterNode = slicer.vtkMRMLScriptedModuleNode()
      self.parameterNode.SetModuleName('PedicleScrewPlanner')
      slicer.mrmlScene.AddNode(self.parameterNode)
 
    for s in allSteps:
        s.setParameterNode (self.parameterNode)
    
    
    # restore workflow step
    currentStep = self.parameterNode.GetParameter('currentStep')
    
    if currentStep != '':
      logging.debug('Restoring workflow step to ' + currentStep)
      if currentStep == 'LoadData':
        self.workflow.setInitialStep(self.loadDataStep)
      if currentStep == 'DefineROI':
        self.workflow.setInitialStep(self.defineROIStep)
      if currentStep == 'Measurements':
        self.workflow.setInitialStep(self.measurementsStep)
      if currentStep == 'Landmarks':
        self.workflow.setInitialStep(self.landmarksStep)
      # if currentStep == 'Screw':
      #   self.workflow.setInitialStep(self.screwStep)
      if currentStep == 'Grade':
        self.workflow.setInitialStep(self.gradeStep)   
      if currentStep == 'Final':
        self.workflow.setInitialStep(self.endStep)
    else:
      logging.debug('currentStep in parameter node is empty')
    
    
    # start the workflow and show the widget
    self.workflow.start()
    workflowWidget.visible = True
    self.layout.addWidget( workflowWidget )

    # compress the layout
    #self.layout.addStretch(1)        

  def cleanup(self):
    pass

  def onReload(self):
    logging.debug("Reloading PedicleScrewPlanner")

    packageName='PedicleScrewSimulatorWizard'
    submoduleNames=['PedicleScrewSimulatorStep',
      'DefineROIStep',
      'EndStep',
      'GradeStep',
      'Helper',
      'LandmarksStep',
      'LoadDataStep',
      'MeasurementsStep']

    import imp
    f, filename, description = imp.find_module(packageName)
    package = imp.load_module(packageName, f, filename, description)
    for submoduleName in submoduleNames:
      f, filename, description = imp.find_module(submoduleName, package.__path__)
      try:
          imp.load_module(packageName+'.'+submoduleName, f, filename, description)
      finally:
          f.close()
          
    ScriptedLoadableModuleWidget.onReload(self)

class PedicleScrewPlannerTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_PedicleScrewPlanner1()

  def test_PedicleScrewPlanner1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay('No test is implemented.')
