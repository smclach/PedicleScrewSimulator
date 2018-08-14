from __main__ import qt, ctk, vtk, slicer

from PedicleScrewSimulatorStep import *
from Helper import *
import PythonQt
import math
import os
import time
import logging

class ScrewStep(PedicleScrewSimulatorStep):
    
    
    def __init__( self, stepid ):
      self.initialize( stepid )
      self.setName( '5. Place Screws' )
      self.setDescription( 'Load screw models and change orientation using sliders' )
      self.screwPath = None
      self.screwName = None
      self.coords = [0,0,0]
      self.matrix1 = vtk.vtkMatrix3x3()
      self.matrix2 = vtk.vtkMatrix3x3()
      self.matrix3 = vtk.vtkMatrix3x3()
      self.matrixScrew = vtk.vtkMatrix4x4()
      self.fiduciallist = []
      self.screwSummary = []
      
      self.approach = None
      
      self.screwList = []
      self.currentFidIndex = 0
      self.currentFidLabel = None
                
      self.fidNode = slicer.vtkMRMLMarkupsFiducialNode()
      
      self.valueTemp1 = 0
      self.valueTemp2 = 0
      self.driveTemp = 0
      
      self.__loadScrewButton = None
      self.__parent = super( ScrewStep, self )
      
      self.timer = qt.QTimer()
      self.timer.setInterval(2)
      self.timer.connect('timeout()', self.driveScrew)
      self.timer2 = qt.QTimer()
      self.timer2.setInterval(2)
      self.timer2.connect('timeout()', self.reverseScrew)
      self.screwInsert = 0.0
      
    
    def killButton(self):
      # hide useless button
      bl = slicer.util.findChildren(text='Final')
      if len(bl):
        bl[0].hide()

    def createUserInterface( self ):

      self.__layout = self.__parent.createUserInterface() 
      ''' 
      # Input fiducials node selector
      #self.inputFiducialsNodeSelector = slicer.qMRMLNodeComboBox()
      self.inputFiducialsNodeSelector.toolTip = "Select a fiducial to define an insertion point for a screw."
      self.inputFiducialsNodeSelector.nodeTypes = (("vtkMRMLMarkupsFiducialNode"), "")
      self.inputFiducialsNodeSelector.addEnabled = False
      self.inputFiducialsNodeSelector.removeEnabled = False
      self.inputFiducialsNodeSelector.setMRMLScene( slicer.mrmlScene ) 
      self.inputFiducialsNodeSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.fidChanged)
      self.__layout.addRow("Select Insertion Point:", self.inputFiducialsNodeSelector)
      self.fid = self.inputFiducialsNodeSelector.currentNode()
      self.sliceChange()
      '''
      
      '''
      # Input model selector
      self.inputScrewSelector = ctk.ctkComboBox()
      self.inputScrewSelector.toolTip = "Select a screw to insert."
      screwList = ['Select a screw','475x30', '475x35', '475x45', '550x30', '550x40', '550x45', '625x35', '625x40', '625x45', '625x50', '700x35', '700x40', '700x45', '700x50']
      self.inputScrewSelector.addItems(screwList)
      self.connect(self.inputScrewSelector, PythonQt.QtCore.SIGNAL('activated(QString)'), self.combo_chosen)
      self.__layout.addRow("Choose Screw:", self.inputScrewSelector)
      
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
      '''
      
      self.fiducial = ctk.ctkComboBox()
      self.fiducial.toolTip = "Select an insertion site."
      #fiducialList = ['Select an insertion landmark', self.fiduciallist]
      #print self.fiduciallist
      #print fiducialList
      #self.fiducial.addItem("Select an insertion site, no really")
      #self.fiducial.addItem("Select an insertion site.")
      self.fiducial.addItems(self.fiduciallist)
      self.connect(self.fiducial, PythonQt.QtCore.SIGNAL('activated(QString)'), self.fiducial_chosen)
      #self.connect(self.fiducial, PythonQt.QtCore.SIGNAL('activated(QString)'), self.fidChanged)
      
      #self.screwGridLayout.addWidget(self.fiducial,0,0)
      
      self.__layout.addRow("Insertion Site:", self.fiducial)
      self.__fiducial = ''
      measuredText1 = qt.QLabel("     Measured:")
      measuredText2 = qt.QLabel("     Measured:")
      lengthText = qt.QLabel("Screw Length:   ") 
      widthText = qt.QLabel("Screw Width:    ")            
      self.length = ctk.ctkComboBox()
      self.length.toolTip = "Select a screw to insert."
      screwList = ['Select a length (mm)','475', '550','625','700']
      self.length.addItems(screwList)
      self.connect(self.length, PythonQt.QtCore.SIGNAL('activated(QString)'), self.length_chosen)
      self.lengthMeasure = qt.QLineEdit()
      #self.__layout.addRow("Screw Length:", self.length)
      #self.__layout.addRow("Measured Pedicle Length:", self.lengthMeasure)
      self.__length = ''
      
      self.QHBox1 = qt.QHBoxLayout()
      self.QHBox1.addWidget(lengthText)
      self.QHBox1.addWidget(self.length)
      self.QHBox1.addWidget(measuredText1)
      self.QHBox1.addWidget(self.lengthMeasure)
      self.__layout.addRow(self.QHBox1)
      
      self.diameter = ctk.ctkComboBox()
      self.diameter.toolTip = "Select a screw to insert."
      screwList = ['Select a diameter (mm)','30', '35', '45', '50']
      self.diameter.addItems(screwList)
      self.widthMeasure = qt.QLineEdit()
      self.connect(self.diameter, PythonQt.QtCore.SIGNAL('activated(QString)'), self.diameter_chosen)
      #self.__layout.addRow("Screw Diameter:", self.diameter)
      #self.__layout.addRow("Measured Pedicle Width:", self.widthMeasure)
      self.__diameter = ''
      
      self.QHBox2 = qt.QHBoxLayout()
      self.QHBox2.addWidget(widthText)
      self.QHBox2.addWidget(self.diameter)
      self.QHBox2.addWidget(measuredText2)
      self.QHBox2.addWidget(self.widthMeasure)
      self.__layout.addRow(self.QHBox2)
      
      # Load Screw Button
      self.__loadScrewButton = qt.QPushButton("Load Screw")
      self.__loadScrewButton.enabled = False
      #self.__layout.addWidget(self.__loadScrewButton)
      self.__loadScrewButton.connect('clicked(bool)', self.loadScrew)
      
      # Delete Screw Button
      self.__delScrewButton = qt.QPushButton("Delete Screw")
      self.__delScrewButton.enabled = True
      #self.__layout.addWidget(self.__delScrewButton)
      self.__delScrewButton.connect('clicked(bool)', self.delScrew)
      
      self.QHBox3 = qt.QHBoxLayout()
      self.QHBox3.addWidget(self.__loadScrewButton)
      self.QHBox3.addWidget(self.__delScrewButton)
      self.__layout.addRow(self.QHBox3)
      
      # Input model node selector
      self.modelNodeSelector = slicer.qMRMLNodeComboBox()
      self.modelNodeSelector.toolTip = "."
      self.modelNodeSelector.nodeTypes = (("vtkMRMLModelNode"), "")
      self.modelNodeSelector.addEnabled = False
      self.modelNodeSelector.removeEnabled = False
      self.modelNodeSelector.setMRMLScene( slicer.mrmlScene ) 
      #self.__layout.addRow("Current Screws:", self.modelNodeSelector)
      
      self.transformGrid = qt.QGridLayout()
      vText = qt.QLabel("Vertical Adjustment:")
      iText = qt.QLabel("Horizontal Adjustment:")
      self.transformGrid.addWidget(vText, 0,0)
      self.transformGrid.addWidget(iText, 0,2)
      
      self.b = ctk.ctkDoubleSpinBox()
      self.b.minimum = -45
      self.b.maximum = 45
      
      self.transformGrid.addWidget(self.b, 1,0)
      
      # Transform Sliders
      self.transformSlider1 = ctk.ctkDoubleSlider()
      self.transformSlider1.minimum = -45
      self.transformSlider1.maximum = 45
      self.transformSlider1.connect('valueChanged(double)', self.transformSlider1ValueChanged)
      self.transformSlider1.connect('valueChanged(double)', self.b.setValue)
      self.transformSlider1.setMinimumHeight(120)
      #self.__layout.addRow("Rotate IS", self.transformSlider1)
      self.transformGrid.addWidget(self.transformSlider1, 1,1)
      
      self.b.connect('valueChanged(double)', self.transformSlider1.setValue)
      
      # Transform Sliders
      self.transformSlider2 = ctk.ctkSliderWidget()
      self.transformSlider2.minimum = -45
      self.transformSlider2.maximum = 45
      self.transformSlider2.connect('valueChanged(double)', self.transformSlider2ValueChanged)
      self.transformSlider2.setMaximumWidth(200)
      #self.__layout.addRow("Rotate LR", self.transformSlider2)
      self.transformGrid.addWidget(self.transformSlider2, 1,2)
      self.__layout.addRow(self.transformGrid)
      '''
      # Transfors Sliders
      self.transformSlider3 = ctk.ctkSliderWidget()
      self.transformSlider3.minimum = 0
      self.transformSlider3.maximum = 100
      self.transformSlider3.connect('valueChanged(double)', self.transformSlider3ValueChanged)
      self.__layout.addRow("Drive Screw", self.transformSlider3)
      '''
      # Insert Screw Button
      self.insertScrewButton = qt.QPushButton("Insert Screw")
      self.insertScrewButton.enabled = True
      #self.__layout.addWidget(self.__loadScrewButton)
      self.insertScrewButton.connect('clicked(bool)', self.insertScrew)
      
      # Backout Screw Button
      self.backoutScrewButton = qt.QPushButton("Backout Screw")
      self.backoutScrewButton.enabled = False
      #self.__layout.addWidget(self.__delScrewButton)
      self.backoutScrewButton.connect('clicked(bool)', self.backoutScrew)
      
      # Reset Screw Button
      self.resetScrewButton = qt.QPushButton("Reset Screw")
      self.resetScrewButton.enabled = True
      #self.__layout.addWidget(self.__delScrewButton)
      self.resetScrewButton.connect('clicked(bool)', self.resetScrew)
      
      self.QHBox4 = qt.QHBoxLayout()
      self.QHBox4.addWidget(self.insertScrewButton)
      self.QHBox4.addWidget(self.backoutScrewButton)
      self.QHBox4.addWidget(self.resetScrewButton)
      self.__layout.addRow(self.QHBox4)

      # Hide ROI Details
      #measurementsTable = ctk.ctkCollapsibleButton()
      #measurementsTable.text = "Measurements Table"
      #self.__layout.addWidget(measurementsTable)
      #measurementsTable.collapsed = True
      
      '''
      self.view = qt.QTableView()
      self.model = qt.QStandardItemModel()
      self.view.setModel(self.model)
      item = qt.QStandardItem()
      item.setText("item")
      self.model.setItem(0,0,item)
      self.__layout.addWidget(self.view)
      '''
      #self.__layout.addRow(self.screwGridLayout)
      # self.updateWidgetFromParameters(self.parameterNode())
      qt.QTimer.singleShot(0, self.killButton)
      self.currentFidIndex = self.fiducial.currentIndex
      self.currentFidLabel = self.fiducial.currentText
      self.fidNode.GetNthFiducialPosition(self.currentFidIndex,self.coords)
      print self.coords
      self.updateMeasurements()
      self.cameraFocus(self.coords)
      #self.screwLandmarks()
    
    def insertScrew(self):
      print "insert"
      self.timer.start()
      self.backoutScrewButton.enabled = True
      self.insertScrewButton.enabled = False
      self.b.enabled = False
      self.transformSlider1.enabled = False
      self.transformSlider2.enabled = False
      #self.transformSlider3ValueChanged(int(self.__diameter))
      
      temp = self.screwList[self.currentFidIndex]
      temp[3] = "1"
      self.screwList[self.currentFidIndex] = temp
      print self.screwList
      
    def backoutScrew(self):
      print "backout"
      self.timer2.start()
      self.backoutScrewButton.enabled = False
      self.insertScrewButton.enabled = True
      self.b.enabled = True
      self.transformSlider1.enabled = True
      self.transformSlider2.enabled = True
      
      temp = self.screwList[self.currentFidIndex]
      temp[3] = "0"
      self.screwList[self.currentFidIndex] = temp
      print self.screwList
            
    def resetScrew(self):
      print "reset"  
      self.resetOrientation()
      
      temp = self.screwList[self.currentFidIndex]
      temp[3] = "0"
      self.screwList[self.currentFidIndex] = temp
      print self.screwList
    
    def updateMeasurements(self):
      pedicleLength = slicer.modules.PedicleScrewSimulatorWidget.measurementsStep.angleTable.cellWidget(self.currentFidIndex,3).currentText
      pedicleWidth = slicer.modules.PedicleScrewSimulatorWidget.measurementsStep.angleTable.cellWidget(self.currentFidIndex,4).currentText
      self.lengthMeasure.setText(pedicleLength + " mm")
      self.widthMeasure.setText(pedicleWidth + " mm")
      print pedicleLength
      
    def screwLandmarks(self):
      self.fiducial = self.fiducialNode()
      self.fidNumber = self.fiducial.GetNumberOfFiducials()
      self.fidLabels = []
      self.fidLevels = []
      self.fidSides = []
      self.fidLevelSide = []
      
      for i in range(0,self.fidNumber):
          self.fidLabels.append(slicer.modules.PedicleScrewSimulatorWidget.measurementsStep.angleTable.item(i,0).text())
          self.fidLevels.append(slicer.modules.PedicleScrewSimulatorWidget.measurementsStep.angleTable.cellWidget(i,1).currentText)
          self.fidSides.append(slicer.modules.PedicleScrewSimulatorWidget.measurementsStep.angleTable.cellWidget(i,2).currentText)
          #self.fidLevelSide.append(self.fidLevels[i] + " " + self.fidSides[i])
      
      print self.fidLevelSide
    
    def sliceChange(self):
        pos = [0,0,0]
        if self.fidNode != None:
          self.fidNode.GetNthFiducialPosition(self.currentFidIndex,pos)
                  
          lm = slicer.app.layoutManager()
          redWidget = lm.sliceWidget('Red')
          redController = redWidget.sliceController()
        
          yellowWidget = lm.sliceWidget('Yellow')
          yellowController = yellowWidget.sliceController()
        
          greenWidget = lm.sliceWidget('Green')
          greenController = greenWidget.sliceController()
        
          yellowController.setSliceOffsetValue(pos[0])
          greenController.setSliceOffsetValue(pos[1])
          redController.setSliceOffsetValue(pos[2])
          print pos[0]
          print pos[1]
          print pos[2]
          self.fidNode.UpdateScene(slicer.mrmlScene)
          
        else:
            return
        
    def fidChanged(self, fid):
        
        self.fid = fid
        self.valueTemp1 = 0
        self.valueTemp2 = 0
        self.driveTemp = 0
        
        #self.transformSlider3.reset()

        screwCheck = slicer.mrmlScene.GetFirstNodeByName('Screw at point %s' % self.currentFidLabel)
        
        if screwCheck == None:
            self.transformSlider1.setValue(0)
            self.transformSlider2.reset()
        else:
            temp = self.screwList[self.currentFidIndex]
            vertOrt = float(temp[4])
            horzOrt = float(temp[5])
            self.resetScrew()
            self.transformSlider1.setValue(vertOrt)
            self.transformSlider2.setValue(horzOrt)
        
        print self.__length
        self.sliceChange()
        self.updateMeasurements()
        self.cameraFocus(self.coords)
        
        self.backoutScrewButton.enabled = False
        self.insertScrewButton.enabled = True
        self.b.enabled = True
        self.transformSlider1.enabled = True
        self.transformSlider2.enabled = True
        
    def fiducial_chosen(self, text):
        if text != "Select an insertion landmark":
            self.__fiducial = text
            self.currentFidIndex = self.fiducial.currentIndex
            self.currentFidLabel = self.fiducial.currentText
            self.fidNode.GetNthFiducialPosition(self.currentFidIndex,self.coords)
            print self.currentFidIndex
            print self.currentFidLabel
            print self.coords
            self.combo_chosen()
            

    def length_chosen(self, text):
        if text != "Select a length (mm)":
            self.__length = text
            self.combo_chosen()
        
    def diameter_chosen(self, text):
        if text != "Select a diameter (mm)":
            self.__diameter = text
            self.combo_chosen()

    def updateComboBox(self):
        print "update combo box"
        print self.fiduciallist
        self.fiducial.addItem("blah")
        
    def combo_chosen(self):
        if self.__length != "Select a length (mm)" and self.__diameter != "Select a diameter (mm)":
          self.screwPath = os.path.join(os.path.dirname(slicer.modules.pediclescrewsimulator.path), 'Resources/ScrewModels/scaled_' + self.__length + 'x' + self.__diameter + '.vtk')
          self.screwPath = self.screwPath.replace("\\","/")
          print(self.screwPath)
          self.__loadScrewButton.enabled = True
          #self.screwName = 'scaled_' + text
          #self.transformSlider3.maximum = int(self.__diameter)
          
    def loadScrew(self):    
        print "load screw button"
        #self.fidChanged

        screwCheck = slicer.mrmlScene.GetFirstNodeByName('Screw at point %s' % self.currentFidLabel)
        if screwCheck != None:
            # screw already loaded
            return

        screwDescrip = ["0","0","0","0","0","0"]
        screwModel = slicer.modules.models.logic().AddModel(self.screwPath)
        if screwModel is None:
            logging.error("Failed to load screw model: "+self.screwPath)
            return

        matrix = vtk.vtkMatrix4x4()
        matrix.DeepCopy((1, 0, 0, self.coords[0],
                       0, -1, 0, self.coords[1],
                       0, 0, -1, self.coords[2],
                       0, 0, 0, 1))

        transformScrewTemp = slicer.vtkMRMLLinearTransformNode()
        transformScrewTemp.SetName("Transform-%s" % self.currentFidLabel)
        slicer.mrmlScene.AddNode(transformScrewTemp)
        transformScrewTemp.ApplyTransformMatrix(matrix)

        screwModel.SetName('Screw at point %s' % self.currentFidLabel)
        screwModel.SetAndObserveTransformNodeID(transformScrewTemp.GetID())

        modelDisplay = screwModel.GetDisplayNode()
        modelDisplay.SetColor(0.12,0.73,0.91)
        modelDisplay.SetDiffuse(0.90)
        modelDisplay.SetAmbient(0.10)
        modelDisplay.SetSpecular(0.20)
        modelDisplay.SetPower(10.0)
        modelDisplay.SetSliceIntersectionVisibility(True)
        screwModel.SetAndObserveDisplayNodeID(modelDisplay.GetID())

        screwDescrip[0] = self.currentFidLabel
        screwDescrip[1] = self.__length
        screwDescrip[2] = self.__diameter

        self.screwList.append(screwDescrip)

        self.insertScrewButton.enabled = True
        self.backoutScrewButton.enabled = False
        self.b.enabled = True
        self.transformSlider1.enabled = True
        self.transformSlider2.enabled = True

    def delScrew(self):
        #fidName = self.inputFiducialsNodeSelector.currentNode().GetName()

        transformFid = slicer.mrmlScene.GetFirstNodeByName('Transform-%s' % self.currentFidLabel)
        screwModel = slicer.mrmlScene.GetFirstNodeByName('Screw at point %s' % self.currentFidLabel)
            
        if screwModel != None:
            slicer.mrmlScene.RemoveNode(transformFid)
            slicer.mrmlScene.RemoveNode(screwModel)
        else:
            return
        
    def fidMove(self, observer, event):

        screwCheck = slicer.mrmlScene.GetFirstNodeByName('Screw at point %s' % observer.GetName())

        if screwCheck != None:
          coords = [0,0,0]  
          observer.GetFiducialCoordinates(coords)

          transformFid = slicer.mrmlScene.GetFirstNodeByName('Transform-%s' % observer.GetName())

          matrixScrew = transformFid.GetMatrixTransformToParent()
          matrixScrew.SetElement(0,3,coords[0])
          matrixScrew.SetElement(1,3,coords[1])
          matrixScrew.SetElement(2,3,coords[2])
          transformFid.SetMatrixTransformToParent(matrixScrew)
        
          transformFid.UpdateScene(slicer.mrmlScene)
          self.sliceChange()
        else:
          return
        
    def cameraFocus(self, position):  
      camera = slicer.mrmlScene.GetNodeByID('vtkMRMLCameraNode1')
            
      if self.approach == 'Posterior':
          
          camera.SetFocalPoint(*position)
          camera.SetPosition(position[0],-400,position[2])
          camera.SetViewUp([0,0,1])
               
      elif self.approach == 'Anterior':
          
          camera.SetFocalPoint(*position)
          camera.SetPosition(position[0],400,position[2])
          camera.SetViewUp([0,0,1])
               
      elif self.approach == 'Left':
          
          camera.SetFocalPoint(*position)
          camera.SetPosition(-400,position[1],position[2])
          camera.SetViewUp([0,0,1])
                
      elif self.approach == 'Right':
          
          camera.SetFocalPoint(*position)
          camera.SetPosition(400,position[1],position[2])
          camera.SetViewUp([0,0,1])
      
      camera.ResetClippingRange()
          
    def transformSlider1ValueChanged(self, value):
        print(value)
        
        newValue = value - self.valueTemp1
        
        angle1 = math.pi / 180.0 * newValue * -1 # Match screw direction
        
        matrix1 = vtk.vtkMatrix3x3()
        matrix1.DeepCopy([ 1, 0, 0,
                          0, math.cos(angle1), -math.sin(angle1),
                          0, math.sin(angle1), math.cos(angle1)])

        self.transformScrewComposite(matrix1)
        
        self.valueTemp1 = value 
        
        temp = self.screwList[self.currentFidIndex]
        temp[4] = str(value)
        self.screwList[self.currentFidIndex] = temp
        print self.screwList
        
    def transformSlider2ValueChanged(self, value):
        print(value)
        
        newValue = value - self.valueTemp2
        
        angle2 = math.pi / 180.0 * newValue * -1 # Match screw direction
        
        matrix2 = vtk.vtkMatrix3x3()
        matrix2.DeepCopy([ math.cos(angle2), -math.sin(angle2), 0,
                          math.sin(angle2), math.cos(angle2), 0,
                          0, 0, 1])
        
        self.transformScrewComposite(matrix2)
        
        self.valueTemp2 = value
        
        temp = self.screwList[self.currentFidIndex]
        temp[5] = str(value)
        self.screwList[self.currentFidIndex] = temp
        print self.screwList
    
    def nothing():
        print "nothing"
    
    def delayDisplay(self,action, msec=1000):
	"""This utility method displays a small dialog and waits.
	This does two things: 1) it lets the event loop catch up
	to the state of the test so that rendering and widget updates
	have all taken place before the test continues and 2) it
	shows the user/developer/tester the state of the test
	so that we'll know when it breaks.
	"""
	#print(message)
	#self.info = qt.QDialog()
	#self.infoLayout = qt.QVBoxLayout()
	#self.info.setLayout(self.infoLayout)
	#self.label = qt.QLabel(message,self.info)
	#self.infoLayout.addWidget(self.label)
	#qt.QTimer.singleShot(msec, action)
	#self.info.exec_()    
    
                            
    def driveScrew(self):
        if self.screwInsert < int(self.__diameter):
            
            value = self.screwInsert
            #print(value)
            # attempt to rotate with driving        
            
            angle3 = math.pi / 180.0 * 72 #((360/2.5)*self.screwInsert) 
        
            matrix3 = vtk.vtkMatrix3x3()
            matrix3.DeepCopy([ math.cos(angle3), 0, -math.sin(angle3),
                          0, 1, 0,
                          math.sin(angle3), 0, math.cos(angle3)])
        
            self.transformScrewComposite(matrix3)


            value = value*-1
            transformFid = slicer.mrmlScene.GetFirstNodeByName('Transform-%s' % self.currentFidLabel)
        
            matrixScrew = transformFid.GetMatrixTransformToParent()
        
            newVal = value - self.driveTemp
            print(newVal)
        
            drive1 = matrixScrew.GetElement(0,1)
            drive2 = matrixScrew.GetElement(1,1)
            drive3 = matrixScrew.GetElement(2,1)
        
            coord1 = drive1 * newVal + matrixScrew.GetElement(0,3)
            coord2 = drive2 * newVal + matrixScrew.GetElement(1,3)
            coord3 = drive3 * newVal + matrixScrew.GetElement(2,3)
        
            matrixScrew.SetElement(0,3,coord1)
            matrixScrew.SetElement(1,3,coord2)
            matrixScrew.SetElement(2,3,coord3)

            transformFid.SetMatrixTransformToParent(matrixScrew)
                
            #transformFid.UpdateScene(slicer.mrmlScene)
            #self.delayDisplay(transformFid.UpdateScene(slicer.mrmlScene), 2000)
            self.driveTemp = value
            self.screwInsert += 1
        else:
            self.timer.stop()  
            self.screwInsert = 0.0 
            self.driveTemp = 0  
        '''    
        angle3 = math.pi / 180.0 * (value*50) 
        
        matrix3 = vtk.vtkMatrix3x3()
        matrix3.DeepCopy([ math.cos(angle3), 0, -math.sin(angle3),
                          0, 1, 0,
                          math.sin(angle3), 0, math.cos(angle3)])
        
        self.transformScrewComposite(matrix3)


        value = value*-1
        transformFid = slicer.mrmlScene.GetFirstNodeByName('Transform-%s' % self.currentFidLabel)
        
        matrixScrew = transformFid.GetMatrixTransformToParent()
        
        newVal = value - self.driveTemp
        
        drive1 = matrixScrew.GetElement(0,1)
        drive2 = matrixScrew.GetElement(1,1)
        drive3 = matrixScrew.GetElement(2,1)
        
        coord1 = drive1 * newVal + matrixScrew.GetElement(0,3)
        coord2 = drive2 * newVal + matrixScrew.GetElement(1,3)
        coord3 = drive3 * newVal + matrixScrew.GetElement(2,3)
        
        matrixScrew.SetElement(0,3,coord1)
        matrixScrew.SetElement(1,3,coord2)
        matrixScrew.SetElement(2,3,coord3)

        transformFid.SetMatrixTransformToParent(matrixScrew)
        
        transformFid.UpdateScene(slicer.mrmlScene)
        
        self.driveTemp = value
        '''   
    def reverseScrew(self):
        if self.screwInsert < int(self.__diameter):
            
            value = self.screwInsert
            #print(value)
            # attempt to rotate with driving        
            
            angle3 = math.pi / 180.0 * -72 #((360/2.5)*self.screwInsert) 
        
            matrix3 = vtk.vtkMatrix3x3()
            matrix3.DeepCopy([ math.cos(angle3), 0, -math.sin(angle3),
                          0, 1, 0,
                          math.sin(angle3), 0, math.cos(angle3)])
        
            self.transformScrewComposite(matrix3)

            transformFid = slicer.mrmlScene.GetFirstNodeByName('Transform-%s' % self.currentFidLabel)
        
            matrixScrew = transformFid.GetMatrixTransformToParent()
        
            newVal = value - self.driveTemp
            print(newVal)
        
            drive1 = matrixScrew.GetElement(0,1)
            drive2 = matrixScrew.GetElement(1,1)
            drive3 = matrixScrew.GetElement(2,1)
        
            coord1 = drive1 * newVal + matrixScrew.GetElement(0,3)
            coord2 = drive2 * newVal + matrixScrew.GetElement(1,3)
            coord3 = drive3 * newVal + matrixScrew.GetElement(2,3)
        
            matrixScrew.SetElement(0,3,coord1)
            matrixScrew.SetElement(1,3,coord2)
            matrixScrew.SetElement(2,3,coord3)

            transformFid.SetMatrixTransformToParent(matrixScrew)

            #transformFid.UpdateScene(slicer.mrmlScene)
            #self.delayDisplay(transformFid.UpdateScene(slicer.mrmlScene), 2000)
            self.driveTemp = value
            self.screwInsert += 1
        else:
            self.timer2.stop()  
            self.screwInsert = 0.0 
            self.driveTemp = 0 

    def resetOrientation(self):
                
        self.transformSlider1.setValue(0)
        self.transformSlider2.reset()

        transformFid = slicer.mrmlScene.GetFirstNodeByName('Transform-%s' % self.currentFidLabel)
        
        matrixScrew = transformFid.GetMatrixTransformToParent()
        
        matrixScrew.SetElement(0,0,1)
        matrixScrew.SetElement(0,1,0)
        matrixScrew.SetElement(0,2,0)
        
        matrixScrew.SetElement(1,0,0)
        matrixScrew.SetElement(1,1,-1)
        matrixScrew.SetElement(1,2,0)
        
        matrixScrew.SetElement(2,0,0)
        matrixScrew.SetElement(2,1,0)
        matrixScrew.SetElement(2,2,-1)
        
        matrixScrew.SetElement(0,3,self.coords[0])
        matrixScrew.SetElement(1,3,self.coords[1])
        matrixScrew.SetElement(2,3,self.coords[2])

        transformFid.SetMatrixTransformToParent(matrixScrew)

        transformFid.UpdateScene(slicer.mrmlScene)

        self.backoutScrewButton.enabled = False
        self.insertScrewButton.enabled = True
               
        self.transformSlider1.enabled = True
        self.transformSlider2.enabled = True
        self.b.enabled = True
        #self.transformSlider3.reset()

    def transformScrewComposite(self, inputMatrix):

        transformFid = slicer.mrmlScene.GetFirstNodeByName('Transform-%s' % self.currentFidLabel)
        
        matrixScrew = transformFid.GetMatrixTransformToParent()
        
        newMatrix = vtk.vtkMatrix3x3()
        outputMatrix = vtk.vtkMatrix3x3()
        
        newMatrix.SetElement(0,0,matrixScrew.GetElement(0,0))
        newMatrix.SetElement(0,1,matrixScrew.GetElement(0,1))
        newMatrix.SetElement(0,2,matrixScrew.GetElement(0,2))
        
        newMatrix.SetElement(1,0,matrixScrew.GetElement(1,0))
        newMatrix.SetElement(1,1,matrixScrew.GetElement(1,1))
        newMatrix.SetElement(1,2,matrixScrew.GetElement(1,2))
        
        newMatrix.SetElement(2,0,matrixScrew.GetElement(2,0))
        newMatrix.SetElement(2,1,matrixScrew.GetElement(2,1))
        newMatrix.SetElement(2,2,matrixScrew.GetElement(2,2))
        
        vtk.vtkMatrix3x3.Multiply3x3(newMatrix, inputMatrix, outputMatrix)
        
        #coords = [0,0,0]  
        #self.fid.GetFiducialCoordinates(coords)
        
        matrixScrew.SetElement(0,0,outputMatrix.GetElement(0,0))
        matrixScrew.SetElement(0,1,outputMatrix.GetElement(0,1))
        matrixScrew.SetElement(0,2,outputMatrix.GetElement(0,2))
        #matrixScrew.SetElement(0,3,self.coords[0])
        
        matrixScrew.SetElement(1,0,outputMatrix.GetElement(1,0))
        matrixScrew.SetElement(1,1,outputMatrix.GetElement(1,1))
        matrixScrew.SetElement(1,2,outputMatrix.GetElement(1,2))
        #matrixScrew.SetElement(1,3,self.coords[1])
        
        matrixScrew.SetElement(2,0,outputMatrix.GetElement(2,0))
        matrixScrew.SetElement(2,1,outputMatrix.GetElement(2,1))
        matrixScrew.SetElement(2,2,outputMatrix.GetElement(2,2))
        #matrixScrew.SetElement(2,3,self.coords[2])
        
        matrixScrew.SetElement(3,0,0)
        matrixScrew.SetElement(3,1,0)
        matrixScrew.SetElement(3,2,0)
        matrixScrew.SetElement(3,3,1)

        transformFid.SetMatrixTransformToParent(matrixScrew)

        transformFid.UpdateScene(slicer.mrmlScene)


    def validate( self, desiredBranchId ):
        
      self.__parent.validate( desiredBranchId )
      self.__parent.validationSucceeded(desiredBranchId)

      
    def onEntry(self, comingFrom, transitionType):

      self.fidNode = self.fiducialNode()
      self.fidNodeObserver = self.fidNode.AddObserver(vtk.vtkCommand.ModifiedEvent,self.fidMove)

      print self.fidNode
      
      self.fidNode.SetLocked(1)
      slicer.modules.models.logic().SetAllModelsVisibility(1)

      #self.updateComboBox()
      
      for x in range (0,self.fidNode.GetNumberOfFiducials()):
        print x
        label = self.fidNode.GetNthFiducialLabel(x)
        level = slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.cellWidget(x,1).currentText
        side = slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.cellWidget(x,2).currentText
        self.fiduciallist.append(label + " / " + level + " / " + side)
        print self.fiduciallist
        #modelX = slicer.mrmlScene.GetNodeByID('vtkMRMLModelDisplayNode' + str(x + 4))
        #modelX.SetSliceIntersectionVisibility(1)
     
      
      #self.fiducial.clear()
      #self.fiducial.addItem("Select an insertion site")
      #self.fiducial.addItems(self.fiduciallist)    
      
      super(ScrewStep, self).onEntry(comingFrom, transitionType)
      
      lm = slicer.app.layoutManager()
      if lm == None: 
        return 
      lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
      
      pNode = self.parameterNode()
      pNode.SetParameter('currentStep', self.stepid)
      print(pNode.GetParameter('currentStep'))
      self.approach = str(pNode.GetParameter('approach'))

      qt.QTimer.singleShot(0, self.killButton)

   
    def onExit(self, goingTo, transitionType):

      self.fidNode.RemoveObserver(self.fidNodeObserver)

      if goingTo.id() != 'Grade' and goingTo.id() != 'Measurements':
          return
      
      if goingTo.id() == 'Measurements':
          '''
          fiducialNode = self.fiducialNode()
          fidCount = fiducialNode.GetNumberOfFiducials()
          for i in range(fidCount):
            fidName = fiducialNode.GetNthFiducialLabel(i)
            screwModel = slicer.mrmlScene.GetFirstNodeByName('Screw at point %s' % fidName)
            slicer.mrmlScene.RemoveNode(screwModel)
            
          fiducialNode.RemoveAllMarkups()
          '''
          slicer.modules.models.logic().SetAllModelsVisibility(0)
          
          for x in range(0,self.fidNode.GetNumberOfFiducials()):
             modelX = slicer.mrmlScene.GetNodeByID('vtkMRMLModelDisplayNode' + str(x + 4))
             modelX.SetSliceIntersectionVisibility(0)
          
          self.fidNode.SetLocked(0)
      
      if goingTo.id() == 'Grade':
        
        self.doStepProcessing()

      super(ScrewStep, self).onExit(goingTo, transitionType)


    def doStepProcessing(self):

        print('Done')
