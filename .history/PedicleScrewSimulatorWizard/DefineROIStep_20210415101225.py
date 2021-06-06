from __main__ import qt, ctk, slicer

from .PedicleScrewSimulatorStep import *
from .Helper import *
import PythonQt

class DefineROIStep( PedicleScrewSimulatorStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( '2. 定义关注区(ROI)' )
    self.setDescription( """步骤：\n  1、定义ROI\n  2、选择起始椎体和# 左右及Steps:\n  1. Define ROI (click and drag dotted colour box)\n  2. Select starting vertebrae and # to instrument""" )

    self.__parent = super( DefineROIStep, self )

    self.reset()

    qt.QTimer.singleShot(0, self.killButton)


  def reset(self):
    self.__vrDisplayNode = None

    self.__roiTransformNode = None
    self.__baselineVolume = None

    self.__roi = None
    self.__roiObserverTag = None


  def killButton(self):
    # hide useless button
    bl = slicer.util.findChildren(text='Final')
    if len(bl):
      bl[0].hide()


  def createUserInterface( self ):

    self.__layout = self.__parent.createUserInterface()

    vText = qt.QLabel("1st Instrumented Level:")
    iText = qt.QLabel("# to Instrument:")
    aText = qt.QLabel("Approach Direction:")
    self.vSelector = qt.QComboBox()
    self.vSelector.setMaximumWidth(120)
    self.levels = ("C1","C2","C3","C4","C5","C6","C7","T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12","L1", "L2", "L3", "L4", "L5","S1")
    self.vSelector.addItems(self.levels)
    self.iSelector = qt.QComboBox()
    self.iSelector.setMaximumWidth(120)
    self.iSelector.addItems(['1','2','3','4','5','6','7','8','9','10','11','12'])
    self.aSelector = qt.QComboBox()
    self.aSelector.setMaximumWidth(120)
    self.aSelector.addItems(['Posterior','Anterior','Left','Right'])
    blank = qt.QLabel("  ")
    blank.setMaximumWidth(30)
    #self.__layout.addWidget(vText)
    #self.__layout.addWidget(self.vSelector)
    #self.__layout.addWidget(iText)
    #self.__layout.addWidget(self.iSelector)

    self.vertebraeGridBox = qt.QGridLayout()
    self.vertebraeGridBox.addWidget(vText,0,0)
    self.vertebraeGridBox.addWidget(self.vSelector,1,0)
    self.vertebraeGridBox.addWidget(blank,0,1)
    self.vertebraeGridBox.addWidget(iText,0,2)
    self.vertebraeGridBox.addWidget(blank,1,1)
    self.vertebraeGridBox.addWidget(self.iSelector,1,2)
    self.vertebraeGridBox.addWidget(blank,0,3)
    self.vertebraeGridBox.addWidget(aText,0,4)
    self.vertebraeGridBox.addWidget(blank,1,3)
    self.vertebraeGridBox.addWidget(self.aSelector,1,4)
    self.__layout.addRow(self.vertebraeGridBox)

    #self.__layout.addRow("Starting Instrumented Vertebra:",self.vSelector)
    #self.__layout.addRow("Number of Vertebrae to Instrument:",self.iSelector)

    # Hide ROI Details
    roiCollapsibleButton = ctk.ctkCollapsibleButton()
    #roiCollapsibleButton.setMaximumWidth(320)
    roiCollapsibleButton.text = "ROI Details"
    self.__layout.addWidget(roiCollapsibleButton)
    roiCollapsibleButton.collapsed = True

    # Layout
    roiLayout = qt.QFormLayout(roiCollapsibleButton)

    #label for ROI selector
    roiLabel = qt.QLabel( 'Select ROI:' )
    font = roiLabel.font
    font.setBold(True)
    roiLabel.setFont(font)


    #creates combobox and populates it with all vtkMRMLAnnotationROINodes in the scene
    self.__roiSelector = slicer.qMRMLNodeComboBox()
    self.__roiSelector.nodeTypes = ['vtkMRMLAnnotationROINode']
    self.__roiSelector.toolTip = "ROI defining the structure of interest"
    self.__roiSelector.setMRMLScene(slicer.mrmlScene)
    self.__roiSelector.addEnabled = 1

    #add label + combobox
    roiLayout.addRow( roiLabel, self.__roiSelector )

    self.__roiSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onROIChanged)

    # the ROI parameters
    # GroupBox to hold ROI Widget
    voiGroupBox = qt.QGroupBox()
    voiGroupBox.setTitle( 'Define VOI' )
    roiLayout.addRow( voiGroupBox )

    # create form layout for GroupBox
    voiGroupBoxLayout = qt.QFormLayout( voiGroupBox )

    # create ROI Widget and add it to the form layout of the GroupBox
    self.__roiWidget = PythonQt.qSlicerAnnotationsModuleWidgets.qMRMLAnnotationROIWidget()
    voiGroupBoxLayout.addRow( self.__roiWidget )

    # # Hide VR Details
    # vrCollapsibleButton = ctk.ctkCollapsibleButton()
    # #roiCollapsibleButton.setMaximumWidth(320)
    # vrCollapsibleButton.text = "Rendering Details"
    # self.__layout.addWidget(vrCollapsibleButton)
    # vrCollapsibleButton.collapsed = True

    # # Layout
    # vrLayout = qt.QFormLayout(vrCollapsibleButton)

    # # the ROI parameters
    # # GroupBox to hold ROI Widget
    # vrGroupBox = qt.QGroupBox()
    # vrGroupBox.setTitle( 'Define Rendering' )
    # vrLayout.addRow( vrGroupBox )

    # # create form layout for GroupBox
    # vrGroupBoxLayout = qt.QFormLayout( vrGroupBox )

    # # create ROI Widget and add it to the form layout of the GroupBox
    # self.__vrWidget = PythonQt.qSlicerVolumeRenderingModuleWidgets.qSlicerPresetComboBox()
    # #self.__vrWidget = PythonQt.qSlicerVolumeRenderingModuleWidgets.qMRMLVolumePropertyNodeWidget()
    # vrGroupBoxLayout.addRow( self.__vrWidget )

    # # initialize VR
    # self.__vrLogic = slicer.modules.volumerendering.logic()

    # self.updateWidgetFromParameters(self.parameterNode())
    qt.QTimer.singleShot(0, self.killButton)


  #called when ROI bounding box is altered
  def onROIChanged(self):
    #read ROI node from combobox
    roi = self.__roiSelector.currentNode()

    if roi != None:
      self.__roi = roi

      # create VR node first time a valid ROI is selected
      self.InitVRDisplayNode()

      # update VR settings each time ROI changes
      pNode = self.parameterNode()
      # get scalar volume node loaded in previous step
      v = pNode.GetNodeReference('baselineVolume')

      #set parameters for VR display node
      self.__vrDisplayNode.SetAndObserveROINodeID(roi.GetID())
      self.__vrDisplayNode.SetCroppingEnabled(1)
      self.__vrDisplayNode.VisibilityOn()

      #transform ROI
      roi.SetAndObserveTransformNodeID(self.__roiTransformNode.GetID())


      if self.__roiObserverTag != None:
        self.__roi.RemoveObserver(self.__roiObserverTag)

      #add observer to ROI. call self.processROIEvents if ROI is altered
      self.__roiObserverTag = self.__roi.AddObserver('ModifiedEvent', self.processROIEvents)

      #enable click and drag functions on ROI
      roi.SetInteractiveMode(1)

      #connect ROI widget to ROI
      self.__roiWidget.setMRMLAnnotationROINode(roi)
      self.__roi.SetDisplayVisibility(1)

  def processROIEvents(self,node=None,event=None):
    # get the range of intensities inside the ROI

    # Make updates faster and prevent flickering (due to transfer function editing)
    slicer.app.pauseRender()

    # get the IJK bounding box of the voxels inside ROI
    roiCenter = [0,0,0]
    roiRadius = [0,0,0]

    #get center coordinate
    self.__roi.GetXYZ(roiCenter)
    logging.debug(roiCenter)

    #change slices to center of ROI
    lm = slicer.app.layoutManager()
    redWidget = lm.sliceWidget('Red')
    redController = redWidget.sliceController()

    yellowWidget = lm.sliceWidget('Yellow')
    yellowController = yellowWidget.sliceController()

    greenWidget = lm.sliceWidget('Green')
    greenController = greenWidget.sliceController()

    yellowController.setSliceOffsetValue(roiCenter[0])
    greenController.setSliceOffsetValue(roiCenter[1])
    redController.setSliceOffsetValue(roiCenter[2])

    #get radius
    self.__roi.GetRadiusXYZ(roiRadius)

    #get IJK coordinates of 8 corners of ROI
    roiCorner1 = [roiCenter[0]+roiRadius[0],roiCenter[1]+roiRadius[1],roiCenter[2]+roiRadius[2],1]
    roiCorner2 = [roiCenter[0]+roiRadius[0],roiCenter[1]+roiRadius[1],roiCenter[2]-roiRadius[2],1]
    roiCorner3 = [roiCenter[0]+roiRadius[0],roiCenter[1]-roiRadius[1],roiCenter[2]+roiRadius[2],1]
    roiCorner4 = [roiCenter[0]+roiRadius[0],roiCenter[1]-roiRadius[1],roiCenter[2]-roiRadius[2],1]
    roiCorner5 = [roiCenter[0]-roiRadius[0],roiCenter[1]+roiRadius[1],roiCenter[2]+roiRadius[2],1]
    roiCorner6 = [roiCenter[0]-roiRadius[0],roiCenter[1]+roiRadius[1],roiCenter[2]-roiRadius[2],1]
    roiCorner7 = [roiCenter[0]-roiRadius[0],roiCenter[1]-roiRadius[1],roiCenter[2]+roiRadius[2],1]
    roiCorner8 = [roiCenter[0]-roiRadius[0],roiCenter[1]-roiRadius[1],roiCenter[2]-roiRadius[2],1]

    #get RAS transformation matrix of scalar volume and convert it to IJK matrix
    ras2ijk = vtk.vtkMatrix4x4()
    self.__baselineVolume.GetRASToIJKMatrix(ras2ijk)

    roiCorner1ijk = ras2ijk.MultiplyPoint(roiCorner1)
    roiCorner2ijk = ras2ijk.MultiplyPoint(roiCorner2)
    roiCorner3ijk = ras2ijk.MultiplyPoint(roiCorner3)
    roiCorner4ijk = ras2ijk.MultiplyPoint(roiCorner4)
    roiCorner5ijk = ras2ijk.MultiplyPoint(roiCorner5)
    roiCorner6ijk = ras2ijk.MultiplyPoint(roiCorner6)
    roiCorner7ijk = ras2ijk.MultiplyPoint(roiCorner7)
    roiCorner8ijk = ras2ijk.MultiplyPoint(roiCorner8)

    lowerIJK = [0, 0, 0]
    upperIJK = [0, 0, 0]

    lowerIJK[0] = min(roiCorner1ijk[0],roiCorner2ijk[0],roiCorner3ijk[0],roiCorner4ijk[0],roiCorner5ijk[0],roiCorner6ijk[0],roiCorner7ijk[0],roiCorner8ijk[0])
    lowerIJK[1] = min(roiCorner1ijk[1],roiCorner2ijk[1],roiCorner3ijk[1],roiCorner4ijk[1],roiCorner5ijk[1],roiCorner6ijk[1],roiCorner7ijk[1],roiCorner8ijk[1])
    lowerIJK[2] = min(roiCorner1ijk[2],roiCorner2ijk[2],roiCorner3ijk[2],roiCorner4ijk[2],roiCorner5ijk[2],roiCorner6ijk[2],roiCorner7ijk[2],roiCorner8ijk[2])

    upperIJK[0] = max(roiCorner1ijk[0],roiCorner2ijk[0],roiCorner3ijk[0],roiCorner4ijk[0],roiCorner5ijk[0],roiCorner6ijk[0],roiCorner7ijk[0],roiCorner8ijk[0])
    upperIJK[1] = max(roiCorner1ijk[1],roiCorner2ijk[1],roiCorner3ijk[1],roiCorner4ijk[1],roiCorner5ijk[1],roiCorner6ijk[1],roiCorner7ijk[1],roiCorner8ijk[1])
    upperIJK[2] = max(roiCorner1ijk[2],roiCorner2ijk[2],roiCorner3ijk[2],roiCorner4ijk[2],roiCorner5ijk[2],roiCorner6ijk[2],roiCorner7ijk[2],roiCorner8ijk[2])

    #get image data of scalar volume
    image = self.__baselineVolume.GetImageData()

    #create image clipper
    clipper = vtk.vtkImageClip()
    clipper.ClipDataOn()
    clipper.SetOutputWholeExtent(int(lowerIJK[0]),int(upperIJK[0]),int(lowerIJK[1]),int(upperIJK[1]),int(lowerIJK[2]),int(upperIJK[2]))
    clipper.SetInputData(image)
    clipper.Update()

    #read upper and lower threshold values from clipped volume
    roiImageRegion = clipper.GetOutput()
    intRange = roiImageRegion.GetScalarRange()
    lThresh = 0.4*(intRange[0]+intRange[1])
    uThresh = intRange[1]

    #create new opacity map with voxels falling between upper and lower threshold values at 100% opacity. All others at 0%
    self.__vrOpacityMap.RemoveAllPoints()
    self.__vrOpacityMap.AddPoint(0,0)
    self.__vrOpacityMap.AddPoint(lThresh-1,0)
    self.__vrOpacityMap.AddPoint(lThresh,1)
    self.__vrOpacityMap.AddPoint(uThresh,1)
    self.__vrOpacityMap.AddPoint(uThresh+1,0)

    # finally, update the focal point to be the center of ROI
    camera = slicer.mrmlScene.GetNodeByID('vtkMRMLCameraNode1')
    camera.SetFocalPoint(roiCenter)
    camera.SetPosition(roiCenter[0],-600,roiCenter[2])
    camera.SetViewUp([0,0,1])

    slicer.app.resumeRender()

  #set up VR
  def InitVRDisplayNode(self):
    #If VR node exists, load it from saved ID
    if self.__vrDisplayNode == None:
      pNode = self.parameterNode()
      self.__vrDisplayNode = pNode.GetNodeReference('vrDisplayNode')
      if not self.__vrDisplayNode:
        v = pNode.GetNodeReference('baselineVolume')
        logging.debug('PedicleScrewSimulator VR: will observe ID '+v.GetID())
        vrLogic = slicer.modules.volumerendering.logic()
        self.__vrDisplayNode = vrLogic.CreateDefaultVolumeRenderingNodes(v)

        propNode = self.__vrDisplayNode.GetVolumePropertyNode()
        logging.debug('Property node: '+propNode.GetID())

        defaultRoiNode = self.__vrDisplayNode.GetROINode()
        if defaultRoiNode != self.__roi:
          self.__vrDisplayNode.SetAndObserveROINodeID(self.__roi.GetID())
          slicer.mrmlScene.RemoveNode(defaultRoiNode)

        vrLogic.CopyDisplayToVolumeRenderingDisplayNode(self.__vrDisplayNode)

        # Workaround: depth peeling must be disabled for volume rendering to appear properly
        viewNode = slicer.mrmlScene.GetNodeByID('vtkMRMLViewNode1')
        viewNode.SetUseDepthPeeling(False)

    viewNode = slicer.mrmlScene.GetNodeByID('vtkMRMLViewNode1')
    self.__vrDisplayNode.AddViewNodeID(viewNode.GetID())

    slicer.modules.volumerendering.logic().CopyDisplayToVolumeRenderingDisplayNode(self.__vrDisplayNode)

    #update opacity and color map
    self.__vrOpacityMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
    self.__vrColorMap = self.__vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetRGBTransferFunction()

    # setup color transfer function once
    # two points at 0 and 500 force all voxels to be same color (any two points will work)
    self.__vrColorMap.RemoveAllPoints()
    self.__vrColorMap.AddRGBPoint(0, 0.95,0.84,0.57)
    self.__vrColorMap.AddRGBPoint(500, 0.95,0.84,0.57)

    # Update transfer function based on ROI
    self.processROIEvents()



  def onEntry(self,comingFrom,transitionType):
    super(DefineROIStep, self).onEntry(comingFrom, transitionType)

    # setup the interface
    lm = slicer.app.layoutManager()
    lm.setLayout(3)

    #create progress bar dialog
    self.progress = qt.QProgressDialog(slicer.util.mainWindow())
    self.progress.minimumDuration = 0
    self.progress.show()
    self.progress.setValue(0)
    self.progress.setMaximum(0)
    self.progress.setCancelButton(0)
    self.progress.setMinimumWidth(500)
    self.progress.setWindowModality(2)

    self.progress.setLabelText('Generating Volume Rendering...')
    slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
    self.progress.repaint()

    #read scalar volume node ID from previous step
    pNode = self.parameterNode()
    self.__baselineVolume = pNode.GetNodeReference('baselineVolume')

    #if ROI was created previously, get its transformation matrix and update current ROI
    roiTransformNode = pNode.GetNodeReference('roiTransform')
    if not roiTransformNode:
      roiTransformNode = slicer.vtkMRMLLinearTransformNode()
      slicer.mrmlScene.AddNode(roiTransformNode)
      pNode.SetNodeReferenceID('roiTransform', roiTransformNode.GetID())

    dm = vtk.vtkMatrix4x4()
    self.__baselineVolume.GetIJKToRASDirectionMatrix(dm)
    dm.SetElement(0,3,0)
    dm.SetElement(1,3,0)
    dm.SetElement(2,3,0)
    dm.SetElement(0,0,abs(dm.GetElement(0,0)))
    dm.SetElement(1,1,abs(dm.GetElement(1,1)))
    dm.SetElement(2,2,abs(dm.GetElement(2,2)))
    roiTransformNode.SetMatrixTransformToParent(dm)


    Helper.SetBgFgVolumes(self.__baselineVolume.GetID())
    Helper.SetLabelVolume(None)

    # use this transform node to align ROI with the axes of the baseline
    # volume
    self.__roiTransformNode = pNode.GetNodeReference('roiTransform')
    if not self.__roiTransformNode:
      Helper.Error('Internal error! Error code CT-S2-NRT, please report!')

    # get the roiNode from parameters node, if it exists, and initialize the
    # GUI
    self.updateWidgetFromParameterNode(pNode)

    # start VR
    if self.__roi != None:
      self.__roi.SetDisplayVisibility(1)
      # Make sure the GUI is fully initilized because user will see it for a few seconds, while VR is being set up
      slicer.app.processEvents()
      self.InitVRDisplayNode()

    #close progress bar
    self.progress.setValue(2)
    self.progress.repaint()
    slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
    self.progress.close()
    self.progress = None

    #pNode.SetParameter('currentStep', self.stepid)

    qt.QTimer.singleShot(0, self.killButton)


  def validate( self, desiredBranchId ):

    self.__parent.validate( desiredBranchId )
    roi = self.__roiSelector.currentNode()
    if roi == None:
      self.__parent.validationFailed(desiredBranchId, 'Error', 'Please define ROI!')

    volCheck = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLScalarVolumeNode')
    if volCheck != None:
      self.__parent.validationSucceeded('pass')
    else:
      self.__parent.validationSucceeded('fail')
      slicer.mrmlScene.Clear(0)


  def onExit(self, goingTo, transitionType):

    if goingTo.id() != 'Landmarks' and goingTo.id() != 'LoadData': # Change to next step
      return

    pNode = self.parameterNode()
    # TODO: add storeWidgetStateToParameterNode() -- move all pNode-related stuff
    # there?
    if self.__roi != None:
        self.__roi.RemoveObserver(self.__roiObserverTag)
        self.__roi.SetDisplayVisibility(0)

    if self.__roiSelector.currentNode() != None:
        pNode.SetNodeReferenceID('roiNode', self.__roiSelector.currentNode().GetID())

    if self.__vrDisplayNode != None:
        #self.__vrDisplayNode.VisibilityOff()
        pNode.SetNodeReferenceID('vrDisplayNode', self.__vrDisplayNode.GetID())

    if goingTo.id() == 'Landmarks': # Change to next step

        #create progress bar dialog
        self.progress = qt.QProgressDialog(slicer.util.mainWindow())
        self.progress.minimumDuration = 0
        self.progress.show()
        self.progress.setValue(0)
        self.progress.setMaximum(0)
        self.progress.setCancelButton(0)
        self.progress.setMinimumWidth(500)
        self.progress.setWindowModality(2)

        self.progress.setLabelText('Cropping and resampling volume...')
        slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
        self.progress.repaint()

        self.doStepProcessing()

        #close progress bar
        self.progress.setValue(2)
        self.progress.repaint()
        slicer.app.processEvents(qt.QEventLoop.ExcludeUserInputEvents)
        self.progress.close()
        self.progress = None

    super(DefineROIStep, self).onExit(goingTo, transitionType)

  def updateWidgetFromParameterNode(self, parameterNode):
    roiNode = parameterNode.GetNodeReference('roiNode')
    if not roiNode:
      roiNode = slicer.vtkMRMLAnnotationROINode()
      roiNode.Initialize(slicer.mrmlScene)
      parameterNode.SetNodeReferenceID('roiNode', roiNode.GetID())
      roiNode.SetRadiusXYZ(50, 50, 100)
      # initialize slightly off-center, as spine is usually towards posterior side of the image
      roiNode.SetXYZ(0, -50, 0)
    self.__roiSelector.setCurrentNode(roiNode)

    self.onROIChanged()


  def doStepProcessing(self):
    '''
    prepare roi image for the next step
    '''
    #crop scalar volume
    pNode = self.parameterNode()

    pNode.SetParameter('vertebra', self.vSelector.currentText)
    pNode.SetParameter('inst_length', self.iSelector.currentText)
    pNode.SetParameter('approach', self.aSelector.currentText)

    cropVolumeNode = slicer.vtkMRMLCropVolumeParametersNode()
    cropVolumeNode.SetScene(slicer.mrmlScene)
    cropVolumeNode.SetName('CropVolume_node')
    cropVolumeNode.SetIsotropicResampling(True)
    cropVolumeNode.SetSpacingScalingConst(0.5)
    slicer.mrmlScene.AddNode(cropVolumeNode)
    # TODO hide from MRML tree

    cropVolumeNode.SetInputVolumeNodeID(pNode.GetNodeReference('baselineVolume').GetID())
    cropVolumeNode.SetROINodeID(pNode.GetNodeReference('roiNode').GetID())
    # cropVolumeNode.SetAndObserveOutputVolumeNodeID(outputVolume.GetID())

    cropVolumeLogic = slicer.modules.cropvolume.logic()
    cropVolumeLogic.Apply(cropVolumeNode)

    # TODO: cropvolume error checking
    outputVolume = slicer.mrmlScene.GetNodeByID(cropVolumeNode.GetOutputVolumeNodeID())
    outputVolume.SetName("baselineROI")
    pNode.SetNodeReferenceID('croppedBaselineVolume',cropVolumeNode.GetOutputVolumeNodeID())

    self.__vrDisplayNode = None
