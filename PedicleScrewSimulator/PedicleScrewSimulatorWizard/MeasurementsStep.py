from __main__ import qt, ctk, vtk, slicer

from PedicleScrewSimulatorStep import *
from Helper import *
import PythonQt
import string

class MeasurementsStep( PedicleScrewSimulatorStep ):
    
    def __init__( self, stepid ):
      self.initialize( stepid )
      self.setName( '3. Measurements' )
      self.setDescription( 'Make Anatomical Measurements' )

      self.__parent = super( MeasurementsStep, self )
      qt.QTimer.singleShot(0, self.killButton)
      #self.__vrDisplayNode = None
      #self.__threshold = [ -1, -1 ]
      
      # initialize VR stuff
      #self.__vrLogic = slicer.modules.volumerendering.logic()
      #self.__vrOpacityMap = None

      #self.__roiVolume = None

      #self.__xnode = None
      self.adjustCount = 0
      self.adjustCount2 = 0
      self.rulerList = []
      self.rulerLengths = []
      self.measureCount = 0
      self.entryCount = 0
      self.rulerStatus = 0
      
    def killButton(self):
      # hide useless button
      bl = slicer.util.findChildren(text='Final')
      if len(bl):
        bl[0].hide()
    '''
    def rulerMeasures(self):
      self.rulerList = []
      rulers = slicer.util.getNodesByClass('vtkMRMLAnnotationRulerNode')
      for ruler in rulers:
        self.rulerList.append("%.2f" % ruler.GetDistanceMeasurement())
    '''    
    def updateTable(self):
      #print pNode.GetParameter('vertebrae')
      self.fiducial = self.fiducialNode()
      self.fidNumber = self.fiducial.GetNumberOfFiducials()
      self.fidLabels = []
      self.fidLevels = []
      self.fidSides = []
      self.itemsLabels = []
      self.itemsLevels = []
      self.itemsSides = []
      self.rulerList = []
      self.lengthCombo = []
      self.widthCombo = []

      self.angleTable.setRowCount(self.fidNumber)

      for i in range(0,self.fidNumber):
          self.fidLabels.append(slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.item(i,0).text())
          self.fidLevels.append(slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.cellWidget(i,1).currentText)
          self.fidSides.append(slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.cellWidget(i,2).currentText)
      
      for i in range(0,self.fidNumber):
          Label = str(self.fidLabels[i])
          Level = str(self.fidLevels[i])
          Side = str(self.fidSides[i])
          #print Label
          #print Level
          #print Side
          #print self.levelselection[i] + "loop"
          qtLabel = qt.QTableWidgetItem(Label)
          qtLevel = qt.QTableWidgetItem(Level)
          qtSide = qt.QTableWidgetItem(Side)
          self.itemsLabels.append(qtLabel)
          self.itemsLevels.append(qtLevel)
          self.itemsSides.append(qtSide)
          #print self.items
          self.angleTable.setItem(i, 0, qtLabel)
          self.angleTable.setItem(i, 1, qtLevel)
          self.angleTable.setItem(i, 2, qtSide)

          self.lengthCombo.insert(i,qt.QComboBox())
          self.widthCombo.insert(i,qt.QComboBox())
          self.lengthCombo[i].addItem(" ")
          self.widthCombo[i].addItem(" ")
          #self.rulerMeasures()
          #self.measuresLength = qt.QComboBox()
          #self.measuresLength.addItems(self.rulerList)
          #self.measuresWidth = qt.QComboBox()
          #self.measuresWidth.addItems(self.rulerList) 
          if self.entryCount == 0:
            self.angleTable.setCellWidget(i,3, self.lengthCombo[i])
            self.angleTable.setCellWidget(i,4, self.widthCombo[i])
      #self.entryCount = 1
      # change entry count to update the contents to the list of rulers if = 1   

    def onTableCellClicked(self):
      if self.angleTable.currentColumn() == 0:
          print self.angleTable.currentRow()
          self.currentFid = self.angleTable.currentRow()
          self.zoomIn()
          self.sliceChange()
          self.fiducial.AddObserver('ModifiedEvent', self.fidMove)
      
    def fidMove(self, observer, event):    
        
      #coords = [0,0,0]  
      #observer.GetFiducialCoordinates(coords)
      self.sliceChange()
      
    def rulerAdded(self, observer, event):
      print "ruler added"
      print self.entryCount
      rulers = slicer.util.getNodesByClass('vtkMRMLAnnotationRulerNode')
      
      rulerX = rulers[-1] # last ruler
      self.rulerList.append("%.2f" % rulerX.GetDistanceMeasurement())
      
      for i in range(self.fidNumber):
        print i
        #self.measuresLength = qt.QComboBox()
        #self.measuresWidth = qt.QComboBox()
        self.lengthCombo[i].addItem("%.2f" % rulerX.GetDistanceMeasurement())
        self.widthCombo[i].addItem("%.2f" % rulerX.GetDistanceMeasurement())
        #self.rulerLengths.append("%.2f" % rulerX.GetDistanceMeasurement())
        #self.angleTable.setCellWidget(i,3, self.measuresLength)
        #self.angleTable.setCellWidget(i,4, self.measuresWidth)
    
    def rulerLengthCheck(self, observer, event):
      rulers = slicer.util.getNodesByClass('vtkMRMLAnnotationRulerNode')
      for [i, rulerX] in enumerate(rulers):
        if rulerX[i].GetDistanceMeasurement() == self.rulerList[i].GetDistanceMeasurement():
          print "okay"
        else:
          self.lengthCombo[i].removeItem(i)
          self.widthCombo[i].removeItem(i)
          self.lengthCombo[i].insertItem(i,"%.2f" % rulerX[i].GetDistanceMeasurement())
          self.widthCombo[i].insertItem(i, "%.2f" % rulerX[i].GetDistanceMeasurement())
        

      #self.rulerList.append("%.2f" % rulerX.GetDistanceMeasurement())
    
    def sliceChange(self):
        print "changing"
        coords = [0,0,0]
        if self.fiducial != None:
          self.fiducial.GetNthFiducialPosition(self.currentFid,coords)
        
          lm = slicer.app.layoutManager()
          redWidget = lm.sliceWidget('Red')
          redController = redWidget.sliceController()
        
          yellowWidget = lm.sliceWidget('Yellow')
          yellowController = yellowWidget.sliceController()
        
          greenWidget = lm.sliceWidget('Green')
          greenController = greenWidget.sliceController()
        
          yellowController.setSliceOffsetValue(coords[0])
          greenController.setSliceOffsetValue(coords[1])
          redController.setSliceOffsetValue(coords[2])
        else:
            return
    
    def zoomIn(self):
      print "zoom"
      slicer.app.applicationLogic().PropagateVolumeSelection(1)
      
    def makeFidAdjustments(self):
      if self.adjustCount == 0:
        fidNode = self.fiducialNode()                   
        slicer.modules.markups.logic().SetAllMarkupsLocked(fidNode,False)
        self.adjustCount = 1
        self.adjustFiducials.setText("Fix Landmarks")
        if self.measureCount == 1:
          self.startMeasure()
      elif self.adjustCount == 1:
        fidNode = self.fiducialNode()                   
        slicer.modules.markups.logic().SetAllMarkupsLocked(fidNode,True)
        self.adjustCount = 0
        self.adjustFiducials.setText("Adjust Landmarks")
    
    def crosshairVisible(self):
      if self.adjustCount2 == 0:
        # Disable Slice Intersections
        viewNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
        for viewNode in viewNodes:
          viewNode.SetSliceIntersectionVisibility(0)

        self.adjustCount2 = 1
        self.crosshair.setText("Show Crosshair") 

      elif self.adjustCount2 == 1:  
        # Enable Slice Intersections
        viewNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
        for viewNode in viewNodes:
          viewNode.SetSliceIntersectionVisibility(1)

        self.adjustCount2 = 0
        self.crosshair.setText("Hide Crosshair")   

    def begin(self):
      #slicer.app.applicationLogic().PropagateVolumeSelection(1)
      selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
      # place rulers
      selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLAnnotationRulerNode")
      # to place ROIs use the class name vtkMRMLAnnotationROINode
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      placeModePersistence = 1
      interactionNode.SetPlaceModePersistence(placeModePersistence)
      # mode 1 is Place, can also be accessed via slicer.vtkMRMLInteractionNode().Place
      interactionNode.SetCurrentInteractionMode(1)

    def stop(self):
      selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
      # place rulers
      selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLAnnotationRulerNode")
      # to place ROIs use the class name vtkMRMLAnnotationROINode
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      placeModePersistence = 1
      interactionNode.SetPlaceModePersistence(placeModePersistence)
      # mode 1 is Place, can also be accessed via slicer.vtkMRMLInteractionNode().Place
      interactionNode.SetCurrentInteractionMode(2)
    
    def startMeasure(self):
      if self.measureCount == 0:
        self.begin()
        self.measureCount = 1
        self.startMeasurements.setText("Stop Measuring")
      elif self.measureCount == 1:
        self.stop()
        self.measureCount = 0
        self.startMeasurements.setText("Start Measuring")  
       
    def createUserInterface( self ):
      '''
      '''
      print "1"
      anno = slicer.modules.annotations.logic()
      anno.AddHierarchy()
      
      rulerNode = slicer.mrmlScene.GetNodeByID('vtkMRMLAnnotationHierarchyNode4')
      rulerNode.AddObserver('ModifiedEvent', self.rulerAdded)
      
      rulers = slicer.util.getNodesByClass('vtkMRMLAnnotationRulerNode')
      for ruler in rulers:
        ruler.AddObserver('ModifiedEvent', self.rulerLengthCheck)
      
      '''
      rs = slicer.mrmlScene.GetNodeByID('vtkMRMLAnnotationRulerNode1')
      rs.AddObserver('ModifiedEvent', a)
      '''
      self.__layout = self.__parent.createUserInterface()
      #slicer.app.applicationLogic().PropagateVolumeSelection()
    
      #self.fiducialSelectionButton = slicer.qSlicerMouseModeToolBar()
      #self.fiducialSelectionButton.connect('mrmlSceneChanged(slicer.vtkMRMLScene*)', 'setMRMLScene(slicer.vtkMRMLScene*)')
      #buttonDescription = qt.QLabel('Click to Add Insertion Points to Scene:')
      #self.__layout.addRow(buttonDescription)
      #self.__layout.addRow(self.fiducialSelectionButton)
      #self.fiducialSelectionButton.setApplicationLogic(slicer.app.applicationLogic())
      #self.fiducialSelectionButton.setMRMLScene(slicer.app.mrmlScene())
      
      self.startMeasurements = qt.QPushButton("Start Measuring")
      self.startMeasurements.connect('clicked(bool)', self.startMeasure)
      #self.__layout.addWidget(self.startMeasurements)
      
      #self.stopMeasurements = qt.QPushButton("Stop Measuring")
      #self.stopMeasurements.connect('clicked(bool)', self.stop)
      #self.__layout.addWidget(self.stopMeasurements)

      #self.updateTable2 = qt.QPushButton("Update Table")
      #self.updateTable2.connect('clicked(bool)', self.updateTable)
      #self.__layout.addWidget(self.updateTable2)
      
      self.adjustFiducials = qt.QPushButton("Adjust Landmarks")
      self.adjustFiducials.connect('clicked(bool)', self.makeFidAdjustments)
      
      self.crosshair = qt.QPushButton("Hide Crosshair")
      self.crosshair.connect('clicked(bool)', self.crosshairVisible)
      
      buttonLayout = qt.QHBoxLayout()
      buttonLayout.addWidget(self.startMeasurements) 
      #buttonLayout.addWidget(self.stopMeasurements)
      #buttonLayout.addWidget(self.updateTable2)
      self.__layout.addRow(buttonLayout)
      buttonLayout2 = qt.QHBoxLayout()
      buttonLayout2.addWidget(self.adjustFiducials)
      buttonLayout2.addWidget(self.crosshair)
      self.__layout.addRow(buttonLayout2)
      
      self.fiducial = self.fiducialNode()
      self.fidNumber = self.fiducial.GetNumberOfFiducials()
      self.fidLabels = []
      self.fidLevels = []
      self.fidSides = []
      self.oldPosition = 0
      
      '''
      for i in range(0,self.fidNumber):
          self.fidLabels.append(slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.item(i,0).text())
          self.fidLevels.append(slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.cellWidget(i,1).currentText)
          self.fidSides.append(slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.cellWidget(i,2).currentText)   
          #self.fidLabels.append(self.fiducial.GetNthFiducialLabel(i))
          #position = [0,0,0]
          #self.fiducial.GetNthFiducialPosition(i,position)
          #self.fidPositions.append(position)
      '''    
      print self.fidLabels
      print self.fidLevels 
      print self.fidSides 
      #self.levels = ("C1","C2","C3","C4","C5","C6","C7","T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12","L1", "L2", "L3", "L4", "L5","S1")

      #pNode = self.parameterNode()
      # Angle Table
      horizontalHeaders = ["Fiducial","Level","Side","Pedicle\n Length", "Pedicle\n Width"]
      #self.vertebra = str(pNode.GetParameter('vertebra'))
      #self.inst_length = str(pNode.GetParameter('inst_length'))
      #print self.vertebra
      #print self.inst_length

      #self.levelselection = []

      #for i in range(self.levels.index(self.vertebra),self.levels.index(self.vertebra)+int(self.inst_length)):
      #  print self.levels[i]
      #  self.levelselection.append(self.levels[i])
      #print self.levelselection

      self.angleTable = qt.QTableWidget(self.fidNumber, 5)
      self.angleTable.sortingEnabled = False
      self.angleTable.setEditTriggers(1)
      self.angleTable.setMinimumHeight(self.angleTable.verticalHeader().length())
      self.angleTable.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
      self.angleTable.setSizePolicy (qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Preferred)
      self.angleTable.itemSelectionChanged.connect(self.onTableCellClicked)
      self.__layout.addWidget(self.angleTable)

      self.angleTable.setHorizontalHeaderLabels(horizontalHeaders)
      self.items = []
      '''  
      for i in range(0,self.fidNumber):
          #print self.levelselection[i] + "loop"
          Label = qt.QTableWidgetItem(str(self.fidLabels[i]))
          print Label
          Level = qt.QTableWidgetItem(str(self.fidLevels[i]))
          print Level
          Side = qt.QTableWidgetItem(str(self.fidSides[i]))
          print Side
          #self.items.append(Label)
          self.angleTable.setItem(i, 0, Label)
          self.angleTable.setItem(i, 1, Level)
          self.angleTable.setItem(i, 2, Side)
      '''
      reconCollapsibleButton = ctk.ctkCollapsibleButton()
      reconCollapsibleButton.text = "Change Slice Reconstruction"
      self.__layout.addWidget(reconCollapsibleButton)
      reconCollapsibleButton.collapsed = True
      # Layout
      reconLayout = qt.QFormLayout(reconCollapsibleButton)

      #label for ROI selector
      reconLabel = qt.QLabel( 'Recon Slice:' )
      rotationLabel = qt.QLabel( 'Rotation Angle:' )
    
      #creates combobox and populates it with all vtkMRMLAnnotationROINodes in the scene
      self.selector = slicer.qMRMLNodeComboBox()
      self.selector.nodeTypes = ['vtkMRMLSliceNode']
      self.selector.toolTip = "Change Slice Reconstruction"
      self.selector.setMRMLScene(slicer.mrmlScene)
      self.selector.addEnabled = 1

      #add label + combobox
      reconLayout.addRow( reconLabel, self.selector )
      
      #self.reconSlice = slicer.qMRMLNodeComboBox()   
      #self.recon = slicer.modules.reformat.createNewWidgetRepresentation()
      # pull slice selector
      #self.selector = self.recon.findChild('qMRMLNodeComboBox')
      #self.selector.setCurrentNodeID('vtkMRMLSliceNodeRed')
      #self.__layout.addWidget(self.selector)
      
      self.slider = ctk.ctkSliderWidget()
      #self.slider = PythonQt.qMRMLWidgets.qMRMLLinearTransformSlider()
      #tnode = slicer.mrmlScene.GetNodeByID('vtkMRMLLinearTransformNode1')
      #self.slider.setMRMLTransformNode(tnode)
      self.slider.connect('valueChanged(double)', self.sliderValueChanged)
      self.slider.minimum = -100
      self.slider.maximum = 100
      reconLayout.addRow( rotationLabel, self.slider)
     
      '''
      # pull offset & rotation sliders
    
      self.reconButton = self.recon.findChild('ctkCollapsibleButton')
      self.reconProperties = self.reconButton.findChildren('ctkCollapsibleGroupBox')
      self.reconSpecificProperty1 = self.reconProperties[2]
      self.reconSlider1 = self.reconSpecificProperty1.findChildren('qMRMLLinearTransformSlider')
      self.slider = self.reconSlider1[0]
      self.reconSpecificProperty2 = self.reconProperties[0]
      self.reconSlider2 = self.reconSpecificProperty2.findChildren('qMRMLLinearTransformSlider')
      self.slider2 = self.reconSlider2[0]
      rText = qt.QLabel("Rotate Slice:")
      self.__layout.addWidget(rText)
      self.__layout.addWidget(self.slider)
      #tText = qt.QLabel("Translate Slice:")
      #self.__layout.addWidget(tText)
      #self.__layout.addWidget(self.slider2)
      '''      
      # self.updateWidgetFromParameters(self.parameterNode())
      qt.QTimer.singleShot(0, self.killButton)
      self.updateTable()
    
    def sliderValueChanged(self, value):
      print value
      print self.oldPosition

      transform = vtk.vtkTransform()
            
      if self.selector.currentNodeID == 'vtkMRMLSliceNodeRed':
        print "red"
        redSlice = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeRed')
        transform.SetMatrix(redSlice.GetSliceToRAS())
        transform.RotateX(value - self.oldPosition)
        redSlice.GetSliceToRAS().DeepCopy(transform.GetMatrix())
        redSlice.UpdateMatrices()
        
      elif self.selector.currentNodeID == 'vtkMRMLSliceNodeYellow':
        print "yellow"
        redSlice = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeYellow')
        transform.SetMatrix(redSlice.GetSliceToRAS())
        transform.RotateY(value - self.oldPosition)
        redSlice.GetSliceToRAS().DeepCopy(transform.GetMatrix())
        redSlice.UpdateMatrices()
      
      elif self.selector.currentNodeID == 'vtkMRMLSliceNodeGreen':
        print "green"
        redSlice = slicer.mrmlScene.GetNodeByID('vtkMRMLSliceNodeGreen')
        transform.SetMatrix(redSlice.GetSliceToRAS())
        transform.RotateZ(value - self.oldPosition)
        redSlice.GetSliceToRAS().DeepCopy(transform.GetMatrix())
        redSlice.UpdateMatrices()
      #self.slider.TypeOfTransform = self.slider.ROTATION_LR
      #self.slider.applyTransformation(self.slider.value - self.oldPosition)
      self.oldPosition = value
                                      
    def validate( self, desiredBranchId ):
      self.__parent.validate( desiredBranchId )
      #volCheck = slicer.util.getNodesByClass('vtkMRMLScalarVolumeNode')[0]
      #if volCheck != None:
      #  self.__parent.validationSucceeded('pass')
      #else:
      #slicer.mrmlScene.Clear(0)
      #  self.__parent.validationSucceeded('fail')
      self.__parent.validationSucceeded(desiredBranchId)
      
    def onEntry(self, comingFrom, transitionType):

      super(MeasurementsStep, self).onEntry(comingFrom, transitionType)
                      
      print "2"
      qt.QTimer.singleShot(0, self.killButton)
      
      lm = slicer.app.layoutManager()
      if lm == None: 
        return 
      lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutSideBySideView)

      print "entering measurements"
      self.zoomIn()
                  
      # Enable Slice Intersections
      viewNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
      for viewNode in viewNodes:
        viewNode.SetSliceIntersectionVisibility(1)

      rulers = slicer.util.getNodesByClass('vtkMRMLAnnotationRulerNode')
      for rulerX in rulers:
        rulerX.SetDisplayVisibility(1)
      
      if self.entryCount == 1:
        self.updateTable()
      
      
                              
    def onExit(self, goingTo, transitionType):
      super(MeasurementsStep, self).onExit(goingTo, transitionType)
      print "exiting"  
      # Disable Slice Intersections
      viewNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
      for viewNode in viewNodes:
        viewNode.SetSliceIntersectionVisibility(0)
       
      rulers = slicer.util.getNodesByClass('vtkMRMLAnnotationRulerNode')
      for rulerX in rulers:
        rulerX.SetDisplayVisibility(0)

      if goingTo.id() == 'Screw':
        print "screw"
        self.doStepProcessing()  
    
      self.stop()
      self.measureCount = 0
      self.startMeasurements.setText("Start Measuring")   
        
      # extra error checking, in case the user manages to click ReportROI button
      if goingTo.id() != 'Landmarks' and goingTo.id() != 'Screw':
        print "here 1"
        return
                   
      
      
    def doStepProcessing(self):
      print('Done')                       
      
