from __main__ import vtk, qt, ctk, slicer

import PedicleScrewSimulatorWizard_v3

#
# Pedicle Screw Simulator
#

class PedicleScrewSimulator_v3:
  def __init__(self, parent):
    parent.title = "Pedicle Screw Simulator v3"
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Brendan Polley (University of Toronto)",
                           "Stewart McLachlin (Sunnybrook Research Institute)",
                           "Cari Whyne (Sunnybrook Research Institute)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Pedicle Screw Simulator
    """
    parent.acknowledgementText = """
    replace with organization, grant and thanks.""" # replace with organization, grant and thanks.
    self.parent = parent

#
# qSpineGeneratorWidget
#

class PedicleScrewSimulator_v3Widget:
  def __init__( self, parent=None ):
    print "running pedicle sim v3"  
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout( qt.QVBoxLayout() )
      self.parent.setMRMLScene( slicer.mrmlScene )
    else:
      self.parent = parent
    self.layout = self.parent.layout()

    if not parent:
      self.setup()
      self.parent.show()
      
    if slicer.mrmlScene.GetTagByClassName( "vtkMRMLScriptedModuleNode" ) != 'ScriptedModule':
      slicer.mrmlScene.RegisterNodeClass(vtkMRMLScriptedModuleNode())

  def setup( self ):
    '''
    Create and start the workflow.
    '''
    self.workflow = ctk.ctkWorkflow()

    workflowWidget = ctk.ctkWorkflowStackedWidget()
    workflowWidget.setWorkflow( self.workflow )

    # create all wizard steps
    self.loadDataStep = PedicleScrewSimulatorWizard_v3.LoadDataStep( 'LoadData'  )
    self.defineROIStep = PedicleScrewSimulatorWizard_v3.DefineROIStep( 'DefineROI'  )
    self.measurementsStep = PedicleScrewSimulatorWizard_v3.MeasurementsStep( 'Measurements'  )
    self.landmarksStep = PedicleScrewSimulatorWizard_v3.LandmarksStep( 'Landmarks' )
    self.screwStep = PedicleScrewSimulatorWizard_v3.ScrewStep( 'Screw' )
    self.gradeStep = PedicleScrewSimulatorWizard_v3.GradeStep( 'Grade' )
    self.endStep = PedicleScrewSimulatorWizard_v3.EndStep( 'Final'  )
    
    # add the wizard steps to an array for convenience
    allSteps = []

    allSteps.append( self.loadDataStep )
    allSteps.append( self.defineROIStep )
    allSteps.append( self.landmarksStep)
    allSteps.append( self.measurementsStep )
    allSteps.append( self.screwStep)
    allSteps.append( self.gradeStep)
    allSteps.append( self.endStep )
    
    
    # Add transition 
    # Check if volume is loaded
    self.workflow.addTransition( self.loadDataStep, self.defineROIStep )
    
    self.workflow.addTransition( self.defineROIStep, self.landmarksStep, 'pass', ctk.ctkWorkflow.Bidirectional )
    self.workflow.addTransition( self.defineROIStep, self.loadDataStep, 'fail', ctk.ctkWorkflow.Bidirectional  )
    
    self.workflow.addTransition( self.landmarksStep, self.measurementsStep, 'pass', ctk.ctkWorkflow.Bidirectional )
    self.workflow.addTransition( self.landmarksStep, self.measurementsStep, 'fail', ctk.ctkWorkflow.Bidirectional )
    
    self.workflow.addTransition( self.measurementsStep, self.screwStep, 'pass', ctk.ctkWorkflow.Bidirectional )
    self.workflow.addTransition( self.measurementsStep, self.screwStep, 'fail', ctk.ctkWorkflow.Bidirectional )
    
    self.workflow.addTransition( self.screwStep, self.gradeStep, 'pass', ctk.ctkWorkflow.Bidirectional )
    self.workflow.addTransition( self.screwStep, self.gradeStep, 'fail', ctk.ctkWorkflow.Bidirectional )
          
    self.workflow.addTransition( self.gradeStep, self.endStep )
           
    nNodes = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLScriptedModuleNode')

    self.parameterNode = None
    for n in xrange(nNodes):
      compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLScriptedModuleNode')
      nodeid = None
      if compNode.GetModuleName() == 'PedicleScrewSimulator_v3':
        self.parameterNode = compNode
        print 'Found existing PedicleScrewSimulator_v3 parameter node'
        break
    if self.parameterNode == None:
      self.parameterNode = slicer.vtkMRMLScriptedModuleNode()
      self.parameterNode.SetModuleName('PedicleScrewSimulator_v3')
      slicer.mrmlScene.AddNode(self.parameterNode)
 
    for s in allSteps:
        s.setParameterNode (self.parameterNode)
    
    
    # restore workflow step
    currentStep = self.parameterNode.GetParameter('currentStep')
    
    if currentStep != '':
      print 'Restoring workflow step to ', currentStep
      if currentStep == 'LoadData':
        self.workflow.setInitialStep(self.loadDataStep)
      if currentStep == 'DefineROI':
        self.workflow.setInitialStep(self.defineROIStep)
      if currentStep == 'Measurements':
        self.workflow.setInitialStep(self.measurementsStep)
      if currentStep == 'Landmarks':
        self.workflow.setInitialStep(self.landmarksStep)
      if currentStep == 'Screw':
        self.workflow.setInitialStep(self.screwStep) 
      if currentStep == 'Grade':
        self.workflow.setInitialStep(self.gradeStep)   
      if currentStep == 'Final':
        self.workflow.setInitialStep(self.endStep)
    else:
      print 'currentStep in parameter node is empty!'
    
    
    # start the workflow and show the widget
    self.workflow.start()
    workflowWidget.visible = True
    self.layout.addWidget( workflowWidget )

    # compress the layout
      #self.layout.addStretch(1)        
 
  def enter(self):
    print "PedicleScrewSimulator_v3: enter() called"
