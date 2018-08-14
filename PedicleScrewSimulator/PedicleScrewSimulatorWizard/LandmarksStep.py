from __main__ import qt, ctk, vtk, slicer

from PedicleScrewSimulatorStep import *
from Helper import *
import PythonQt
import os

class LandmarksStep( PedicleScrewSimulatorStep ):
    
    def __init__( self, stepid ):
      self.initialize( stepid )
      self.setName( '3. Identify Insertion Landmarks' )
      self.setDescription( 'Place at least one fiducial on the spine to mark a screw insertion point.' )
      
      self.__parent = super( LandmarksStep, self )
      qt.QTimer.singleShot(0, self.killButton)
      self.levels = ("C1","C2","C3","C4","C5","C6","C7","T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12","L1", "L2", "L3", "L4", "L5","S1")
      self.startCount = 0
      self.addCount = 0
      self.fidObserve = None
          
    def killButton(self):
      # hide useless button
      bl = slicer.util.findChildren(text='Final')
      if len(bl):
        bl[0].hide()

    def begin(self):
      # TODO: we could prepare placement mode here
      pass

    def stop(self):
      self.startMeasurements.placeModeEnabled = False
      
    def cameraFocus(self, position):  
      camera = slicer.mrmlScene.GetNodeByID('vtkMRMLCameraNode1')
      
      if self.approach == 'Posterior':
          
          camera.SetFocalPoint(*position)
          camera.SetPosition(position[0],-200,position[2])
          camera.SetViewUp([0,0,1])
               
      elif self.approach == 'Anterior':
          
          camera.SetFocalPoint(*position)
          camera.SetPosition(position[0],200,position[2])
          camera.SetViewUp([0,0,1])
               
      elif self.approach == 'Left':
          
          camera.SetFocalPoint(*position)
          camera.SetPosition(-200,position[1],position[2])
          camera.SetViewUp([0,0,1])
                
      elif self.approach == 'Right':
          
          camera.SetFocalPoint(*position)
          camera.SetPosition(200,position[1],position[2])
          camera.SetViewUp([0,0,1])
      
      camera.ResetClippingRange()
      
    def onTableCellClicked(self):
      if self.table2.currentColumn() == 0:
          print self.table2.currentRow()
          currentFid = self.table2.currentRow()
          position = [0,0,0]
          self.fiducial = self.fiducialNode()
          self.fiducial.GetNthFiducialPosition(currentFid,position)
          print position
          self.cameraFocus(position)
            
        
    def updateTable(self):
      #print pNode.GetParameter('vertebrae')
      self.fiducial = self.fiducialNode()
      self.fidNumber = self.fiducial.GetNumberOfFiducials()
      print self.fidNumber
      self.fidLabels = []
      self.items = []
      self.Label = qt.QTableWidgetItem()

      self.table2.setRowCount(self.fidNumber)
      
      
      for i in range(0,self.fidNumber):
          self.Label = qt.QTableWidgetItem(self.fiducial.GetNthFiducialLabel(i))
          self.items.append(self.Label)
          self.table2.setItem(i, 0, self.Label)
          self.comboLevel = qt.QComboBox()
          self.comboLevel.addItems(self.levelselection)
          self.comboSide = qt.QComboBox()
          self.comboSide.addItems(["Left","Right"])
          self.table2.setCellWidget(i,1, self.comboLevel)
          self.table2.setCellWidget(i,2, self.comboSide)
      print self.Label.text()

    def deleteFiducial(self):   
      if self.table2.currentColumn() == 0:
          item = self.table2.currentItem()
          self.fidNumber = self.fiducial.GetNumberOfFiducials()
          self.fiducial = self.fiducialNode()
          for i in range(0,self.fidNumber):
              if item.text() == self.fiducial.GetNthFiducialLabel(i):
                  deleteIndex = i
          self.fiducial.RemoveMarkup(deleteIndex)
          deleteIndex = -1

          print self.table2.currentRow()
          row = self.table2.currentRow()
          self.table2.removeRow(row)
          
    def lockFiducials(self):
      fidNode = self.fiducialNode()                   
      slicer.modules.markups.logic().SetAllMarkupsLocked(fidNode,True)
      
    def addFiducials(self):
      pass

    def addFiducialToTable(self, observer, event):
      print event
      print "MODIFIED"
      self.fiducial = self.fiducialNode()
      self.fidNumber = self.fiducial.GetNumberOfFiducials()
      slicer.modules.markups.logic().SetAllMarkupsVisibility(self.fiducial,1)
      print self.fidNumber
      self.fidLabels = []
      self.items = []
      self.Label = qt.QTableWidgetItem()

      self.table2.setRowCount(self.fidNumber)
      
      
      for i in range(0,self.fidNumber):
          self.Label = qt.QTableWidgetItem(self.fiducial.GetNthFiducialLabel(i))
          self.items.append(self.Label)
          self.table2.setItem(i, 0, self.Label)
          self.comboLevel = qt.QComboBox()
          self.comboLevel.addItems(self.levelselection)
          self.comboSide = qt.QComboBox()
          self.comboSide.addItems(["Left","Right"])
          self.table2.setCellWidget(i,1, self.comboLevel)
          self.table2.setCellWidget(i,2, self.comboSide)
          if i == 0 or i == 1:
            self.table2.cellWidget(i,1).setCurrentIndex(0)
            if i == 1:
              self.table2.cellWidget(i,2).setCurrentIndex(1)
          elif i == 2 or i == 3:
            self.table2.cellWidget(i,1).setCurrentIndex(1)
            if i == 3:
              self.table2.cellWidget(i,2).setCurrentIndex(1)
          elif i == 4 or i == 5:
            self.table2.cellWidget(i,1).setCurrentIndex(2)
            if i == 5:
              self.table2.cellWidget(i,2).setCurrentIndex(1)    
      
      #self.addCount = self.addCount + 1

    def createUserInterface( self ):
      markup = slicer.modules.markups.logic()
      markup.AddNewFiducialNode()

      
      
      self.__layout = self.__parent.createUserInterface()
      self.startMeasurements = slicer.qSlicerMarkupsPlaceWidget()
      self.startMeasurements.setButtonsVisible(False)
      self.startMeasurements.placeButton().show()
      self.startMeasurements.setMRMLScene(slicer.mrmlScene)
      self.startMeasurements.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
      self.startMeasurements.connect('activeMarkupsFiducialPlaceModeChanged(bool)', self.addFiducials)          
      #self.__layout.addWidget(self.startMeasurements)  
      
      #self.stopMeasurements = qt.QPushButton("Stop Placing")
      #self.stopMeasurements.connect('clicked(bool)', self.stop)
      #self.__layout.addWidget(self.stopMeasurements)

      #self.updateTable2 = qt.QPushButton("Update Table")
      #self.updateTable2.connect('clicked(bool)', self.updateTable)
      #self.__layout.addWidget(self.updateTable2)
      
      buttonLayout = qt.QHBoxLayout()
      buttonLayout.addWidget(self.startMeasurements) 
      #buttonLayout.addWidget(self.stopMeasurements)
      #buttonLayout.addWidget(self.updateTable2)
      self.__layout.addRow(buttonLayout)

      '''       
      # Table Output of Fiducial List (Slicer 4.3 Markups)  
      tableDescription = qt.QLabel('List of Points Added to Scene:')
      self.__layout.addRow(tableDescription)
      self.__markupWidget = slicer.modules.markups.createNewWidgetRepresentation()
      slicer.modules.markups.logic().AddNewFiducialNode()
      self.__markupWidget.onActiveMarkupMRMLNodeChanged(0)
      self.table = self.__markupWidget.findChild('QTableWidget')
      self.table.hideColumn(0)
      self.table.hideColumn(1)
      self.table.hideColumn(2)
      self.table.setMinimumHeight(100)
      self.table.setMaximumHeight(170)
      self.table.setMinimumWidth(400)
      self.table.setMaximumWidth(447)
      self.table.resize(400,170)
      self.__layout.addWidget(self.table)
      '''
      self.table2 = qt.QTableWidget()
      self.table2.setRowCount(1)
      self.table2.setColumnCount(3)
      self.table2.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
      self.table2.setSizePolicy (qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Preferred)
      self.table2.setMinimumWidth(400)
      self.table2.setMinimumHeight(215)
      self.table2.setMaximumHeight(215)
      horizontalHeaders = ["Fiducial","Level","Side"]
      self.table2.setHorizontalHeaderLabels(horizontalHeaders)
      self.table2.itemSelectionChanged.connect(self.onTableCellClicked)
      self.__layout.addWidget(self.table2)
      

      self.deleteFid = qt.QPushButton("Remove Selected Fiducial")
      self.deleteFid.connect('clicked(bool)', self.deleteFiducial)
      self.__layout.addWidget(self.deleteFid)


      # Camera Transform Sliders
      
      transCam = ctk.ctkCollapsibleButton()
      transCam.text = "Shift Camera Position"
      transCam.collapsed = True
      self.__layout.addWidget(transCam)
      #transCam.collapsed = True
      camLayout = qt.QFormLayout(transCam)

      a = PythonQt.qMRMLWidgets.qMRMLTransformSliders()
      a.setMRMLTransformNode(slicer.mrmlScene.GetNodeByID('vtkMRMLLinearTransformNode4'))
      #transWidget = slicer.modules.transforms.createNewWidgetRepresentation()
      #transSelector = transWidget.findChild('qMRMLNodeComboBox')
      #transWidgetPart = transWidget.findChild('ctkCollapsibleButton')
      #transformSliders = transWidgetPart.findChildren('qMRMLTransformSliders')
      camLayout.addRow(a)
            
                   
      qt.QTimer.singleShot(0, self.killButton)
       
    
    def onEntry(self, comingFrom, transitionType):

      super(LandmarksStep, self).onEntry(comingFrom, transitionType)
      
      qt.QTimer.singleShot(0, self.killButton)
      
      lm = slicer.app.layoutManager()
      if lm == None: 
        return 
      lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
          
      pNode = self.parameterNode()
      print pNode
      self.levelselection = []
      self.vertebra = str(pNode.GetParameter('vertebra'))
      self.inst_length = str(pNode.GetParameter('inst_length'))
      self.approach = str(pNode.GetParameter('approach'))
      for i in range(self.levels.index(self.vertebra),self.levels.index(self.vertebra)+int(self.inst_length)):
          #print self.levels[i]
          self.levelselection.append(self.levels[i])
      print self.levelselection
      
      camera = slicer.mrmlScene.GetNodeByID('vtkMRMLCameraNode1')
      if self.approach == 'Posterior':
          print "posterior"
          camera.SetPosition(0,-600,0)
          camera.SetViewUp([0,0,1])
      elif self.approach == 'Anterior':
          print "Anterior"
          camera.SetPosition(0,600,0)
          camera.SetViewUp([0,0,1])
      elif self.approach == 'Left':
          print "Left"
          camera.SetPosition(-600,0,0)
          camera.SetViewUp([0,0,1])
      elif self.approach == 'Right':
          print "Right"
          camera.SetPosition(600,0,0)
          camera.SetViewUp([0,0,1])
      camera.ResetClippingRange()
      #pNode = self.parameterNode()
      #pNode.SetParameter('currentStep', self.stepid)
      '''
      #roiVolume = Helper.getNodeByID(pNode.GetParameter('croppedBaselineVolumeID'))
      selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
      # place rulers
      selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
      # to place ROIs use the class name vtkMRMLAnnotationROINode
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      placeModePersistence = 1
      interactionNode.SetPlaceModePersistence(placeModePersistence)
      # mode 1 is Place, can also be accessed via slicer.vtkMRMLInteractionNode().Place
      interactionNode.SetCurrentInteractionMode(1)
      '''

      fiducialNode = self.fiducialNode()
      self.startMeasurements.setCurrentNode(fiducialNode)
      self.fidObserve = fiducialNode.AddObserver('ModifiedEvent', self.addFiducialToTable)
      
      if comingFrom.id() == 'DefineROI':
          self.updateTable() 
     
    def getLandmarksNode(self):
      return self.startMeasurements.currentNode()
     
    def onExit(self, goingTo, transitionType):
      
      if goingTo.id() == 'Measurements' or goingTo.id() == 'DefineROI':
          self.stop()
          fiducialNode = self.fiducialNode()
          fiducialNode.RemoveObserver(self.fidObserve)
          self.doStepProcessing()
          #print self.table2.cellWidget(0,1).currentText
      
      #if goingTo.id() == 'Threshold':
          #slicer.mrmlScene.RemoveNode(self.__outModel)     
      
      if goingTo.id() != 'DefineROI' and goingTo.id() != 'Measurements':
          print "here 2"  
          return
      
      super(LandmarksStep, self).onExit(goingTo, transitionType)
      '''
      selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
      # place rulers
      selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLMarkupsFiducialNode")
      # to place ROIs use the class name vtkMRMLAnnotationROINode
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      placeModePersistence = 1
      interactionNode.SetPlaceModePersistence(placeModePersistence)
      # mode 1 is Place, can also be accessed via slicer.vtkMRMLInteractionNode().Place
      interactionNode.SetCurrentInteractionMode(2)
      '''
    def validate( self, desiredBranchId ):

      self.__parent.validate( desiredBranchId )
      self.__parent.validationSucceeded(desiredBranchId)
      
      #self.inputFiducialsNodeSelector.update()
      #fid = self.inputFiducialsNodeSelector.currentNode() 
      fidNumber = self.fiducial.GetNumberOfFiducials() 
       
      #pNode = self.parameterNode()
      if fidNumber != 0:
      #  fidID = fid.GetID()
      #  if fidID != '':
      #    pNode = self.parameterNode()
      #    pNode.SetParameter('fiducialID', fidID)
          self.__parent.validationSucceeded(desiredBranchId)
      else:
          self.__parent.validationFailed(desiredBranchId, 'Error','Please place at least one fiducial on the model before proceeding')

    def doStepProcessing(self):
      #list = ['a','b','c']
      #listNode = self.parameterNode()
      #listNode.SetParameter = ('list', list)  
      print('Done')
      self.lockFiducials()  
