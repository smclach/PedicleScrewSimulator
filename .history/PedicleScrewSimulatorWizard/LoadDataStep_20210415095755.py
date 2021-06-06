from __main__ import qt, ctk, vtk, slicer

from .PedicleScrewSimulatorStep import *
from .Helper import *
import DICOM

class LoadDataStep(PedicleScrewSimulatorStep):

    def __init__( self, stepid ):
      self.initialize( stepid )
      self.setName( '1. 加载图卷' )
      self.setDescription( "加载图卷“到当前场景。点击“从DICOM加载CT”以打开DICOM浏览窗口。“加载其他文件”导入其他格式，如 .nrrd。.Load a volume into the scene. Click 'Load spine CT from DICOM' to open the DICOM browser window. Click 'Load spine CT from other file' to import other file types, including .nrrd" )

      self.__parent = super( LoadDataStep, self )

    def killButton(self):
      # hide useless button
      bl = slicer.util.findChildren(text='Final')
      if len(bl):
        bl[0].hide()

    def createUserInterface( self ):

      self.__layout = self.__parent.createUserInterface()

      #import DICOM folder button
      self.__importDICOMBrowser = qt.QPushButton("Import DICOM folder")
      self.__layout.addRow(self.__importDICOMBrowser)
      self.__importDICOMBrowser.connect('clicked(bool)', self.importDICOMBrowser)

      #show DICOM browser button
      self.__showDICOMBrowserButton = qt.QPushButton("Show DICOM browser")
      self.__layout.addRow(self.__showDICOMBrowserButton)
      self.__showDICOMBrowserButton.connect('clicked(bool)', self.showDICOMBrowser)

      #open load data dialog for adding nrrd files
      self.__loadScrewButton = qt.QPushButton("Load spine CT from other file")
      self.__layout.addRow(self.__loadScrewButton)
      self.__loadScrewButton.connect('clicked(bool)', self.loadVolume)

      #load sample data
      self.__loadSampleCtDataButton = qt.QPushButton("Load sample spine CT")
      self.__layout.addRow(self.__loadSampleCtDataButton)
      self.__loadSampleCtDataButton.connect('clicked(bool)', self.loadSampleVolume)

      #Active Volume text
      self.activeText = qt.QLabel("Spine CT:")
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

    def importDICOMBrowser(self):
      """If DICOM database is invalid then try to create a default one. If fails then show an error message.
      """
      if slicer.modules.DICOMInstance.browserWidget is None:
        slicer.util.selectModule('DICOM')
        slicer.util.selectModule('PedicleScrewSimulator')
      # Make the DICOM browser disappear after loading data
      slicer.modules.DICOMInstance.browserWidget.browserPersistent = False
      if not slicer.dicomDatabase or not slicer.dicomDatabase.isOpen:
        # Try to create a database with default settings
        slicer.modules.DICOMInstance.browserWidget.dicomBrowser.createNewDatabaseDirectory()
        if not slicer.dicomDatabase or not slicer.dicomDatabase.isOpen:
          # Failed to create database
          # Show DICOM browser then display error message
          slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutDicomBrowserView)
          slicer.util.warningDisplay("Could not create a DICOM database with default settings. Please create a new database or"
            " update the existing incompatible database using options shown in DICOM browser.")
          return

      slicer.modules.dicom.widgetRepresentation().self().browserWidget.dicomBrowser.openImportDialog()
      slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutDicomBrowserView)

    def showDICOMBrowser(self):
      if slicer.modules.DICOMInstance.browserWidget is None:
        slicer.util.selectModule('DICOM')
        slicer.util.selectModule('PedicleScrewSimulator')
      # Make the DICOM browser disappear after loading data
      slicer.modules.DICOMInstance.browserWidget.browserPersistent = False
      slicer.app.layoutManager().setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutDicomBrowserView)

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

      #if scalar volume exists proceed to next step and save node ID as 'baselineVolume'
      pNode = self.parameterNode()
      if self.__baseline:
        baselineID = self.__baseline.GetID()
        if baselineID:
          pNode = self.parameterNode()
          pNode.SetNodeReferenceID('baselineVolume', baselineID)
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
