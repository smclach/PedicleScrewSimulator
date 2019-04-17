from __main__ import qt, ctk, vtk, slicer

from .PedicleScrewSimulatorStep import *
from .Helper import *
import DICOM

class LoadDataStep(PedicleScrewSimulatorStep):
    
    def __init__( self, stepid ):
      self.initialize( stepid )
      self.setName( '1. Load Image Volume' )
      self.setDescription( "Load a volume into the scene. Click 'Load spine CT from DICOM' to open the DICOM browser window. Click 'Load spine CT from other file' to import other file types, including .nrrd" )

      self.__parent = super( LoadDataStep, self )
    
    def killButton(self):
      # hide useless button
      bl = slicer.util.findChildren(text='Final')
      if len(bl):
        bl[0].hide()
    
    def createUserInterface( self ):

      self.__layout = self.__parent.createUserInterface()  

      #load sample data
      self.__loadSampleCtDataButton = qt.QPushButton("Load sample spine CT")
      self.__layout.addRow(self.__loadSampleCtDataButton)
      self.__loadSampleCtDataButton.connect('clicked(bool)', self.loadSampleVolume)

      
      #clones DICOM scriptable module
      self.__dicomWidget = slicer.modules.dicom.widgetRepresentation()
      
      #extract button that launches DICOM browser from widget
      colButtons = self.__dicomWidget.findChildren('ctkCollapsibleButton')
      dicomButton = colButtons[1].findChild('QPushButton')
      dicomButton.setText('Load spine CT from DICOM')
      self.__layout.addRow(dicomButton)
      
      #open load data dialog for adding nrrd files
      self.__loadScrewButton = qt.QPushButton("Load spine CT from other file")
      self.__layout.addRow(self.__loadScrewButton)
      self.__loadScrewButton.connect('clicked(bool)', self.loadVolume)

      #Active Volume text
      self.activeText = qt.QLabel("Active Volume Data:")
      self.__layout.addRow(self.activeText)

      #select volume
      #creates combobox and populates it with all vtkMRMLScalarVolumeNodes in the scene
      self.__inputSelector = slicer.qMRMLNodeComboBox()
      self.__inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
      self.__inputSelector.addEnabled = False
      self.__inputSelector.removeEnabled = False
      self.__inputSelector.setMRMLScene( slicer.mrmlScene )
      self.__layout.addRow(self.__inputSelector )

      # self.updateWidgetFromParameters(self.parameterNode())
      qt.QTimer.singleShot(0, self.killButton)

      transform = slicer.vtkMRMLLinearTransformNode()
      transform.SetName("Camera Transform")
      slicer.mrmlScene.AddNode(transform)

      cam = slicer.mrmlScene.GetNodeByID('vtkMRMLCameraNode1')
      cam.SetAndObserveTransformNodeID('vtkMRMLLinearTransformNode4')

      
    def loadVolume(self):

        slicer.util.openAddDataDialog()
    
    
    def loadSampleVolume(self):
      import SampleData
      sampleDataLogic = SampleData.SampleDataLogic()
      sampleDataLogic.downloadCTChest()

    
    #called when entering step
    def onEntry(self, comingFrom, transitionType):

      super(LoadDataStep, self).onEntry(comingFrom, transitionType)

      # setup the interface
      lm = slicer.app.layoutManager()
      lm.setLayout(3)
      
      qt.QTimer.singleShot(0, self.killButton)
      
    
    #check that conditions have been met before proceeding to next step
    def validate( self, desiredBranchId ):

      self.__parent.validate( desiredBranchId )
      
      #read current scalar volume node
      self.__baseline = self.__inputSelector.currentNode()  
     
      #if scalar volume exists proceed to next step and save node ID as 'baselineVolumeID'
      pNode = self.parameterNode()
      if self.__baseline != None:
        baselineID = self.__baseline.GetID()
        if baselineID != '':
          pNode = self.parameterNode()
          pNode.SetParameter('baselineVolumeID', baselineID)
          self.__parent.validationSucceeded(desiredBranchId)
      else:
        self.__parent.validationFailed(desiredBranchId, 'Error','Please load a volume before proceeding')
        
    #called when exiting step         
    def onExit(self, goingTo, transitionType):
      
      #check to make sure going to correct step
      if goingTo.id() == 'DefineROI':
        self.doStepProcessing();
      
      if goingTo.id() != 'DefineROI':
        return

      super(LoadDataStep, self).onExit(goingTo, transitionType)
                 
    def doStepProcessing(self):
        #transforms center of imported volume to world origin
        coords = [0,0,0]
        coords = self.__baseline.GetOrigin()
        
        transformVolmat = vtk.vtkMatrix4x4()
        transformVolmat.SetElement(0,3,coords[0]*-1)
        transformVolmat.SetElement(1,3,coords[1]*-1)
        transformVolmat.SetElement(2,3,coords[2]*-1)
        
        transformVol = slicer.vtkMRMLLinearTransformNode()
        slicer.mrmlScene.AddNode(transformVol)
        transformVol.ApplyTransformMatrix(transformVolmat)
        
        #harden transform
        self.__baseline.SetAndObserveTransformNodeID(transformVol.GetID())
        slicer.vtkSlicerTransformLogic.hardenTransform(self.__baseline)
        
        #offsets volume so its center is registered to world origin
        newCoords = [0,0,0,0,0,0]
        self.__baseline.GetRASBounds(newCoords)
        logging.debug(newCoords)
        shift = [0,0,0]
        shift[0] = 0.5*(newCoords[1] - newCoords[0])
        shift[1] = 0.5*(newCoords[3] - newCoords[2])
        shift[2] = 0.5*(newCoords[4] - newCoords[5])
        
        transformVolmat2 = vtk.vtkMatrix4x4()
        transformVolmat2.SetElement(0,3,shift[0])
        transformVolmat2.SetElement(1,3,shift[1])
        transformVolmat2.SetElement(2,3,shift[2])
        
        transformVol2 = slicer.vtkMRMLLinearTransformNode()
        slicer.mrmlScene.AddNode(transformVol2)
        transformVol2.ApplyTransformMatrix(transformVolmat2)
        
        #harden transform
        self.__baseline.SetAndObserveTransformNodeID(transformVol2.GetID())
        slicer.vtkSlicerTransformLogic.hardenTransform(self.__baseline)
        
        #remove transformations from scene
        slicer.mrmlScene.RemoveNode(transformVol)
        slicer.mrmlScene.RemoveNode(transformVol2)
        
        logging.debug('Done')
