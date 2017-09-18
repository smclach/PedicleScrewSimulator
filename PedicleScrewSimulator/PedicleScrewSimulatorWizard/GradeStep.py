from __main__ import qt, ctk, vtk, slicer

from PedicleScrewSimulatorStep import *
from Helper import *
import math

class GradeStep(PedicleScrewSimulatorStep):
    
    def __init__( self, stepid ):
      self.initialize( stepid )
      self.setName( 'Grade' )
      self.setDescription( 'Grading Step' )
      self.fiduciallist = []
      self.__corticalMin = 375
      self.__corticalMax = 1200
      self.__cancellousMin = 135
      self.__cancellousMax = 375
      self.fiduciallist = []
      self.itemsqtcoP = []
      self.itemsqtcaP = []
      self.itemsqtotP = []
      self.pointsArray = []
      self.screwContact = []
      self.screwCount = 0

      self.__parent = super( GradeStep, self )
    
    def killButton(self):
      # hide useless button
      bl = slicer.util.findChildren(text='Final')
      if len(bl):
        bl[0].hide()

    def createUserInterface( self ):
      
      self.__layout = self.__parent.createUserInterface()  
      
      ln = slicer.util.getNode(pattern='vtkMRMLLayoutNode*')
      ln.SetViewArrangement(24)
      
      modLabel = qt.QLabel('Select Screw at Point:')
      '''
      self.__modelSelector = slicer.qMRMLNodeComboBox()
      self.__modelSelector.nodeTypes = ( ("vtkMRMLAnnotationFiducialNode"), "" )
      self.__modelSelector.addEnabled = False
      self.__modelSelector.removeEnabled = False
      self.__modelSelector.setMRMLScene( slicer.mrmlScene )
      self.__layout.addRow( modLabel, self.__modelSelector )
      '''
      # Paint Screw Button
      self.__selectScrewButton = qt.QPushButton("Grade Screws")
      self.__layout.addWidget(self.__selectScrewButton)
      self.__selectScrewButton.connect('clicked(bool)', self.gradeScrews)
      '''
      #Opacity Slider
      self.transformSlider3 = ctk.ctkSliderWidget()
      self.transformSlider3.minimum = 0
      self.transformSlider3.maximum = 1
      self.transformSlider3.connect('valueChanged(double)', self.transformSlider3ValueChanged)
      self.__layout.addRow("Volume Opacity", self.transformSlider3)
      '''
      self.fiducial = self.fiducialNode()
      self.fidNumber = self.fiducial.GetNumberOfFiducials()
      
      # Screw Table
      horizontalHeaders = ["Screw At","Screw\n Size","% Screw in\n Soft Tissue\n (<130HU)","% Screw in\n LD Bone\n (130-250HU)","% Screw in\n HD Bone\n (>250HU)" ]
      self.screwTable = qt.QTableWidget(self.fidNumber, 5)
      self.screwTable.sortingEnabled = False
      self.screwTable.setEditTriggers(1)
      self.screwTable.setMinimumHeight(self.screwTable.verticalHeader().length())
      self.screwTable.horizontalHeader().setResizeMode(qt.QHeaderView.Stretch)
      self.screwTable.setSizePolicy (qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Preferred)
      self.screwTable.itemSelectionChanged.connect(self.onTableCellClicked)
      self.__layout.addWidget(self.screwTable)

      self.screwTable.setHorizontalHeaderLabels(horizontalHeaders)
      
      
      
      self.updateWidgetFromParameters(self.parameterNode())
      qt.QTimer.singleShot(0, self.killButton)
      
      self.updateTable()
    
    #def transformSlider3ValueChanged(self, value):
    #    #print(value)
    #    self.vrUpdate(value)
                
    def onTableCellClicked(self):
      if self.screwTable.currentColumn() == 0:
          print self.screwTable.currentRow()
          self.currentFid = self.screwTable.currentRow()
          position = [0,0,0]
          self.fiducial = self.fiducialNode()
          self.fiducial.GetNthFiducialPosition(self.currentFid,position)
          self.cameraFocus(position)
          self.sliceChange()
          #self.updateChart(self.screwList[self.currentFid])
    
              
    def cameraFocus(self, position):  
      camera = slicer.mrmlScene.GetNodeByID('vtkMRMLCameraNode1')
      camera.SetFocalPoint(*position)
      camera.SetPosition(position[0],position[1],75)
      camera.SetViewUp([0,1,0])    
      camera.ResetClippingRange()      
    
    def updateTable(self):
      self.itemsLoc = []
      self.itemsLen = []
      self.itemsDia = []
      
      self.screwList = slicer.modules.PedicleScrewSimulatorWidget.screwStep.screwList
      self.screwNumber = len(self.screwList)
      self.screwTable.setRowCount(self.screwNumber)

      for i in range(0,self.fidNumber):
          currentScrew = self.screwList[i]
          screwLoc = str(currentScrew[0])
          screwLen = str(currentScrew[1]) + " x " + str(currentScrew[2])
          
          
          
                    
          qtscrewLoc = qt.QTableWidgetItem(screwLoc)
          qtscrewLen = qt.QTableWidgetItem(screwLen)
          #qtscrewDia = qt.QTableWidgetItem(screwDia)
          
          self.itemsLoc.append(qtscrewLoc)
          self.itemsLen.append(qtscrewLen)
          #self.itemsDia.append(qtscrewDia)
          
          self.screwTable.setItem(i, 0, qtscrewLoc)
          self.screwTable.setItem(i, 1, qtscrewLen)
          #self.screwTable.setItem(i, 2, qtscrewDia)

               
    
    def validate( self, desiredBranchId ):
      '''
      '''
      self.__parent.validate( desiredBranchId )
      self.__parent.validationSucceeded(desiredBranchId)
      
    def onEntry(self, comingFrom, transitionType):

      super(GradeStep, self).onEntry(comingFrom, transitionType)
      
      ln = slicer.util.getNode(pattern='vtkMRMLLayoutNode*')
      ln.SetViewArrangement(24)
      
      pNode = self.parameterNode()

      fidCollection = slicer.mrmlScene.GetNodesByClass('vtkMRMLAnnotationFiducialNode')
      fidCount = fidCollection.GetNumberOfItems()
      for i in range(0, fidCount):
          fidCollection.GetItemAsObject(i).GetAnnotationPointDisplayNode().SetOpacity(0.0)
          
      self.fidNode = self.fiducialNode()
      for x in range (0,self.fidNode.GetNumberOfFiducials()):
        print x
        label = self.fidNode.GetNthFiducialLabel(x)
        level = slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.cellWidget(x,1).currentText
        side = slicer.modules.PedicleScrewSimulatorWidget.landmarksStep.table2.cellWidget(x,2).currentText
        self.fiduciallist.append(label + " / " + level + " / " + side)
        print self.fiduciallist    
      
      
      self.vrUpdate(0.03)
      
      qt.QTimer.singleShot(0, self.killButton)
      

      
    def onExit(self, goingTo, transitionType):
    
      if goingTo.id() == 'Screw':
          self.clearGrade()
          fidCollection = slicer.mrmlScene.GetNodesByClass('vtkMRMLAnnotationFiducialNode')
          fidCount = fidCollection.GetNumberOfItems()
          for i in range(0, fidCount):
            fidCollection.GetItemAsObject(i).GetAnnotationPointDisplayNode().SetOpacity(1.0)
      
      self.vrUpdate(1.0)
      
      super(GradeStep, self).onExit(goingTo, transitionType)
      
    def updateWidgetFromParameters(self, pNode):
        '''
        self.__corticalMin = float(pNode.GetParameter('corticalMin'))
        self.__corticalMax = float(pNode.GetParameter('corticalMax'))
        self.__cancellousMin = float(pNode.GetParameter('cancellousMin'))
        self.__cancellousMax = float(pNode.GetParameter('cancellousMax'))
        '''
        
        
    def doStepProcessing(self):
        print('Done')

    def sliceChange(self):
        coords = [0,0,0]
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
    
    def gradeScrews(self):
        #print self.fiduciallist[0]
        #self.fid = self.__modelSelector.currentNode()
        #self.sliceChange()
        
        
        
        pNode = self.parameterNode()
        
        self.__inputScalarVol = Helper.getNodeByID(pNode.GetParameter('croppedBaselineVolumeID'))
        for x in range(0, len(self.fiduciallist)):
            fidName = self.fiduciallist[x]
            print(fidName)
            collectionT = slicer.mrmlScene.GetNodesByName('Transform-%s' % fidName)
            transformFid = collectionT.GetItemAsObject(0)
            
            collectionS = slicer.mrmlScene.GetNodesByName('Screw at point %s' % fidName)
            screwModel = collectionS.GetItemAsObject(0)
            screwIndex = x
            
            if screwModel != None:
                self.gradeScrew(screwModel, transformFid, fidName, screwIndex)
                self.screwCount += 1
                print "yes"
            else:
                #self.clearGrade()
                print "no"
                return
        self.chartContact(self.screwCount)
        
    #Crops out head of the screw    
    def cropScrew(self,input, area):
        #Get bounds of screw 
        bounds = input.GetPolyData().GetBounds()
        print bounds
        
        #Define bounds for cropping out the head or shaft of the screw respectively
        if area == 'head':
            i = bounds[2]
            j = bounds[3]-17
        elif area == 'shaft':
            i = bounds[3]-17
            j = bounds[3]

        #Create a box with bounds equal to that of the screw minus the head (-17)
        cropBox = vtk.vtkBox()
        cropBox.SetBounds(bounds[0],bounds[1],i,j,bounds[4],bounds[5])
        
        #Crop out head of screw
        extract = vtk.vtkExtractPolyDataGeometry()
        extract.SetImplicitFunction(cropBox)
        extract.SetInput(input.GetPolyData())
        extract.Update()
        
        #PolyData of cropped screw
        output = extract.GetOutput()
        return output
    
    #Select all points in the shaft of the screw for grading
    def cropPoints(self, input):
        #Get bounds of screw 
        bounds = input.GetPolyData().GetBounds()
        
        #Create a cube with bounds equal to that of the screw minus the head (-17)
        cropCube = vtk.vtkCubeSource()
        cropCube.SetBounds(bounds[0],bounds[1],bounds[2],bounds[3]-17,bounds[4],bounds[5])
        
        #Select points on screw within cube
        select = vtk.vtkSelectEnclosedPoints()
        select.SetInput(input.GetPolyData())
        select.SetSurface(cropCube.GetOutput())
        select.Update()
        
        return select
        
        
    def gradeScrew(self, screwModel, transformFid, fidName, screwIndex):
        #Reset screws
        #self.clearGrade()
        
        #Crop out head of screw
        croppedScrew = self.cropScrew(screwModel, 'head')
        
        #Clone screw model poly data
        inputModel = slicer.vtkMRMLModelNode()
        inputModel.SetAndObservePolyData(croppedScrew)
        inputModel.SetAndObserveTransformNodeID(transformFid.GetID())
        slicer.mrmlScene.AddNode(inputModel)
        slicer.vtkSlicerTransformLogic.hardenTransform(inputModel)
        
        #Create new model for output    
        output = slicer.vtkMRMLModelNode()
        output.SetName('Grade model-%s' % fidName)
        slicer.mrmlScene.AddNode(output)
                  
        #Parameters for ProbeVolumeWithModel
        parameters = {}
        parameters["InputVolume"] = self.__inputScalarVol.GetID()
        parameters["InputModel"] = inputModel.GetID()
        parameters["OutputModel"] = output.GetID()
        
        probe = slicer.modules.probevolumewithmodel
        slicer.cli.run(probe, None, parameters, wait_for_completion=True)
        
        #Hide original screw
        modelDisplay = screwModel.GetDisplayNode()
        modelDisplay.SetColor(0,1,0)
        modelDisplay.VisibilityOff()
        
        #Highlight screwh head
        headModel = slicer.vtkMRMLModelNode()
        headModel.SetName('Head %s' % fidName)
        headModel.SetAndObservePolyData(self.cropScrew(screwModel, 'shaft'))
        headModel.SetAndObserveTransformNodeID(transformFid.GetID())
        slicer.mrmlScene.AddNode(headModel)
        
        headDisplay = slicer.vtkMRMLModelDisplayNode()
        headDisplay.SetColor(0,1,0)
        slicer.mrmlScene.AddNode(headDisplay)
        headModel.SetAndObserveDisplayNodeID(headDisplay.GetID())

        #Remove clone    
        slicer.mrmlScene.RemoveNode(inputModel)
        
        #Grade and chart screw
        self.contact(output, screwModel, fidName, screwIndex)
        
        
    def contact(self, input, screwModel, fidName, screwIndex):
        #Get points in shaft of screw
        insidePoints = self.cropPoints(screwModel)
        
        #Get scalars to array
        scalarsArray = input.GetPolyData().GetPointData().GetScalars('NRRDImage')
        self.pointsArray = screwModel.GetPolyData()
        
        #Get total number of tuples/points
        value = scalarsArray.GetNumberOfTuples()
        
        #Reset variables
        point = [0]
        point2 = [0,0,0]
        corticalCount = 0
        cancellousCount = 0
        totalCount = 0
        bounds = [0]
        shaftBounds = 0
        count00 = 0
        points00 = 0
        avg00 = 0.0
        count10 = 0
        points10 = 0
        avg10 = 0.0
        count20 = 0
        points20 = 0
        avg20 = 0.0
        count30 = 0
        points30 = 0
        avg30 = 0.0
        count40 = 0
        points40 = 0
        avg40 = 0.0 
        count50 = 0
        points50 = 0
        avg50 = 0.0 
        count60 = 0
        points60 = 0
        avg60 = 0.0 
        count70 = 0
        points70 = 0
        avg70 = 0.0 
        count80 = 0
        points80 = 0
        avg80 = 0.0 
        count90 = 0
        points90 = 0
        avg90 = 0.0
        avgTotal = []
        avgQuad1 = []
        avgQuad2 = []
        avgQuad3 = []
        avgQuad4 = []
        countQ1_00 = 0
        pointsQ1_00 = 0
        countQ2_00 = 0
        pointsQ2_00 = 0
        countQ3_00 = 0
        pointsQ3_00 = 0
        countQ4_00 = 0
        pointsQ4_00 = 0
        countQ1_10 = 0
        pointsQ1_10 = 0
        countQ2_10 = 0
        pointsQ2_10 = 0
        countQ3_10 = 0
        pointsQ3_10 = 0
        countQ4_10 = 0
        pointsQ4_10 = 0
        countQ1_20 = 0
        pointsQ1_20 = 0
        countQ2_20 = 0
        pointsQ2_20 = 0
        countQ3_20 = 0
        pointsQ3_20 = 0
        countQ4_20 = 0
        pointsQ4_20 = 0
        countQ1_30 = 0
        pointsQ1_30 = 0
        countQ2_30 = 0
        pointsQ2_30 = 0
        countQ3_30 = 0
        pointsQ3_30 = 0
        countQ4_30 = 0
        pointsQ4_30 = 0
        countQ1_40 = 0
        pointsQ1_40 = 0
        countQ2_40 = 0
        pointsQ2_40 = 0
        countQ3_40 = 0
        pointsQ3_40 = 0
        countQ4_40 = 0
        pointsQ4_40 = 0
        countQ1_50 = 0
        pointsQ1_50 = 0
        countQ2_50 = 0
        pointsQ2_50 = 0
        countQ3_50 = 0
        pointsQ3_50 = 0
        countQ4_50 = 0
        pointsQ4_50 = 0
        countQ1_60 = 0
        pointsQ1_60 = 0
        countQ2_60 = 0
        pointsQ2_60 = 0
        countQ3_60 = 0
        pointsQ3_60 = 0
        countQ4_60 = 0
        pointsQ4_60 = 0
        countQ1_70 = 0
        pointsQ1_70 = 0
        countQ2_70 = 0
        pointsQ2_70 = 0
        countQ3_70 = 0
        pointsQ3_70 = 0
        countQ4_70 = 0
        pointsQ4_70 = 0
        countQ1_80 = 0
        pointsQ1_80 = 0
        countQ2_80 = 0
        pointsQ2_80 = 0
        countQ3_80 = 0
        pointsQ3_80 = 0
        countQ4_80 = 0
        pointsQ4_80 = 0
        countQ1_90 = 0
        pointsQ1_90 = 0
        countQ2_90 = 0
        pointsQ2_90 = 0
        countQ3_90 = 0
        pointsQ3_90 = 0
        countQ4_90 = 0
        pointsQ4_90 = 0
        
        
        xCenter = 0
        zCenter = 0         
        
        bounds = self.pointsArray.GetPoints().GetBounds()
        lowerBound = bounds[2] #+ 17
        shaftBounds = 30 # FOR NOW
        print bounds
        xCenter = (bounds[0] + bounds[1])/2
        zCenter = (bounds[4] + bounds[5])/2
        
        #For each point in the screw model...
        for i in range(0, value):
            #If the point is in the shaft of the screw...
            if insidePoints.IsInside(i) == 1:  
              totalCount += 1
              #Read scalar value at point to "point" array
              scalarsArray.GetTupleValue(i, point)
              print point
              self.pointsArray.GetPoints().GetPoint(i,point2)
              print point2
              if point2[1] >= lowerBound and point2[1] < (lowerBound + (shaftBounds*0.1)):
                  print "00%"
                  count00 = count00 + point[0]
                  points00 += 1
                  print xCenter
                  print point2[0]
                  print zCenter
                  print point2[2]  
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1"
                      countQ1_00 = countQ1_00 + point[0]
                      pointsQ1_00 += 1
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_00 = countQ2_00 + point[0]
                      pointsQ2_00 += 1
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_00 = countQ3_00 + point[0]
                      pointsQ3_00 += 1
                  else:
                      print "Quadrant 4"
                      countQ4_00 = countQ4_00 + point[0]
                      pointsQ4_00 += 1    
              elif point2[1] >= (lowerBound + (shaftBounds*0.1)) and point2[1] < (lowerBound + (shaftBounds*0.2)):
                  print "10%"
                  count10 = count10 + point[0]
                  points10 += 1
                  print xCenter
                  print point2[0]
                  print zCenter
                  print point2[2]    
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1"
                      countQ1_10 = countQ1_10 + point[0]
                      pointsQ1_10 += 1
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_10 = countQ2_10 + point[0]
                      pointsQ2_10 += 1
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_10 = countQ3_10 + point[0]
                      pointsQ3_10 += 1
                  else:
                      print "Quadrant 4"
                      countQ4_10 = countQ4_10 + point[0]
                      pointsQ4_10 += 1  
              elif point2[1] >= (lowerBound + (shaftBounds*0.2)) and point2[1] < (lowerBound + (shaftBounds*0.3)):
                  print "20%"
                  count20 = count20 + point[0]
                  points20 += 1
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1"
                      countQ1_20 = countQ1_20 + point[0]
                      pointsQ1_20 += 1
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_20 = countQ2_20 + point[0]
                      pointsQ2_20 += 1
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_20 = countQ3_20 + point[0]
                      pointsQ3_20 += 1
                  else:
                      print "Quadrant 4"
                      countQ4_20 = countQ4_20 + point[0]
                      pointsQ4_20 += 1      
              elif point2[1] >= (lowerBound + (shaftBounds*0.3)) and point2[1] < (lowerBound + (shaftBounds*0.4)):
                  print "30%"
                  count30 = count30 + point[0]
                  points30 += 1
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1"
                      countQ1_30 = countQ1_30 + point[0]
                      pointsQ1_30 += 1
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_30 = countQ2_30 + point[0]
                      pointsQ2_30 += 1
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_30 = countQ3_30 + point[0]
                      pointsQ3_30 += 1
                  else:
                      print "Quadrant 4"  
                      countQ4_30 = countQ4_30 + point[0]
                      pointsQ4_30 += 1    
              elif point2[1] >= (lowerBound + (shaftBounds*0.4)) and point2[1] < (lowerBound + (shaftBounds*0.5)):
                  print "40%"
                  count40 = count40 + point[0]
                  points40 += 1
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1"
                      countQ1_40 = countQ1_40 + point[0]
                      pointsQ1_40 += 1
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_40 = countQ2_40 + point[0]
                      pointsQ2_40 += 1
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_40 = countQ3_40 + point[0]
                      pointsQ3_40 += 1
                  else:
                      print "Quadrant 4"  
                      countQ4_40 = countQ4_40 + point[0]
                      pointsQ4_40 += 1    
              elif point2[1] >= (lowerBound + (shaftBounds*0.5)) and point2[1] < (lowerBound + (shaftBounds*0.6)):
                  print "50%"
                  count50 = count50 + point[0]
                  points50 += 1
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1"
                      countQ1_50 = countQ1_50 + point[0]
                      pointsQ1_50 += 1 
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_50 = countQ2_50 + point[0]
                      pointsQ2_50 += 1
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_50 = countQ3_50 + point[0]
                      pointsQ3_50 += 1
                  else:
                      print "Quadrant 4" 
                      countQ4_50 = countQ4_50 + point[0]
                      pointsQ4_50 += 1     
              elif point2[1] >= (lowerBound + (shaftBounds*0.6)) and point2[1] < (lowerBound + (shaftBounds*0.7)):
                  print "60%"
                  count60 = count60 + point[0]
                  points60 += 1
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1"
                      countQ1_60 = countQ1_60 + point[0]
                      pointsQ1_60 += 1
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_60 = countQ2_60 + point[0]
                      pointsQ2_60 += 1
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_60 = countQ3_60 + point[0]
                      pointsQ3_60 += 1
                  else:
                      print "Quadrant 4"  
                      countQ4_60 = countQ4_60 + point[0]
                      pointsQ4_60 += 1    
              elif point2[1] >= (lowerBound + (shaftBounds*0.7)) and point2[1] < (lowerBound + (shaftBounds*0.8)):
                  print "70%"
                  count70 = count70 + point[0]
                  points70 += 1
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1" 
                      countQ1_70 = countQ1_70 + point[0]
                      pointsQ1_70 += 1 
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_70 = countQ2_70 + point[0]
                      pointsQ2_70 += 1 
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_70 = countQ3_70 + point[0]
                      pointsQ3_70 += 1 
                  else:
                      print "Quadrant 4"  
                      countQ4_70 = countQ4_70 + point[0]
                      pointsQ4_70 += 1     
              elif point2[1] >= (lowerBound + (shaftBounds*0.8)) and point2[1] < (lowerBound + (shaftBounds*0.9)):
                  print "80%"
                  count80 = count80 + point[0]
                  points80 += 1
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1"
                      countQ1_80 = countQ1_80 + point[0]
                      pointsQ1_80 += 1
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_80 = countQ2_80 + point[0]
                      pointsQ2_80 += 1
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_80 = countQ3_80 + point[0]
                      pointsQ3_80 += 1
                  else:
                      print "Quadrant 4" 
                      countQ4_80 = countQ4_80 + point[0]
                      pointsQ4_80 += 1     
              elif point2[1] >= (lowerBound + (shaftBounds*0.9)) and point2[1] < (lowerBound + (shaftBounds*1)):
                  print "90%"
                  count90 = count90 + point[0]
                  points90 += 1
                  if point2[0] < xCenter and point2[2] >= zCenter:
                      print "Quadrant 1"
                      countQ1_90 = countQ1_90 + point[0]
                      pointsQ1_90 += 1
                  elif point2[0] >= xCenter and point2[2] >= zCenter:
                      print "Quadrant 2"
                      countQ2_90 = countQ2_90 + point[0]
                      pointsQ2_90 += 1
                  elif point2[0] < xCenter and point2[2] < zCenter:
                      print "Quadrant 3"
                      countQ3_90 = countQ3_90 + point[0]
                      pointsQ3_90 += 1
                  else:
                      print "Quadrant 4" 
                      countQ4_90 = countQ4_90 + point[0]
                      pointsQ4_90 += 1        
              else:
                  print "no" 
                 
              #print totalCount
              #Keep track of number of points that fall into cortical threshold and cancellous threshold respectively
              if point[0] >= self.__corticalMin:
                  corticalCount += 1
              elif point[0] < self.__corticalMin and point[0] >= self.__cancellousMin:
                  cancellousCount += 1
        #Calculate averages
        avgQuad1.extend([float(countQ1_00 / pointsQ1_00), float(countQ1_10 / pointsQ1_10), float(countQ1_20 / pointsQ1_20), float(countQ1_30 / pointsQ1_30), float(countQ1_40 / pointsQ1_40), float(countQ1_50 / pointsQ1_50), float(countQ1_60 / pointsQ1_60), float(countQ1_70 / pointsQ1_70), float(countQ1_80 / pointsQ1_80), float(countQ1_90 / pointsQ1_90)])
        avgQuad2.extend([float(countQ2_00 / pointsQ2_00), float(countQ2_10 / pointsQ2_10), float(countQ2_20 / pointsQ2_20), float(countQ2_30 / pointsQ2_30), float(countQ2_40 / pointsQ2_40), float(countQ2_50 / pointsQ2_50), float(countQ2_60 / pointsQ2_60), float(countQ2_70 / pointsQ2_70), float(countQ2_80 / pointsQ2_80), float(countQ2_90 / pointsQ2_90)])
        avgQuad3.extend([float(countQ3_00 / pointsQ3_00), float(countQ3_10 / pointsQ3_10), float(countQ3_20 / pointsQ3_20), float(countQ3_30 / pointsQ3_30), float(countQ3_40 / pointsQ3_40), float(countQ3_50 / pointsQ3_50), float(countQ3_60 / pointsQ3_60), float(countQ3_70 / pointsQ3_70), float(countQ3_80 / pointsQ3_80), float(countQ3_90 / pointsQ3_90)])
        avgQuad4.extend([float(countQ4_00 / pointsQ4_00), float(countQ4_10 / pointsQ4_10), float(countQ4_20 / pointsQ4_20), float(countQ4_30 / pointsQ4_30), float(countQ4_40 / pointsQ4_40), float(countQ4_50 / pointsQ4_50), float(countQ4_60 / pointsQ4_60), float(countQ4_70 / pointsQ4_70), float(countQ4_80 / pointsQ4_80), float(countQ4_90 / pointsQ4_90)])
        print avgQuad1
        print avgQuad2
        print avgQuad3
        print avgQuad4

        if points00 != 0:
            avg00 = count00 / points00
            avgTotal.append(avg00)
        if points10 != 0:
            avg10 = count10 / points10
            avgTotal.append(avg10)
        if points20 != 0:
            avg20 = count20 / points20
            avgTotal.append(avg20)
        if points30 != 0:
            avg30 = count30 / points30
            avgTotal.append(avg30)
        if points40 != 0:
            avg40 = count40 / points40
            avgTotal.append(avg40)
        if points50 != 0:
            avg50 = count50 / points50
            avgTotal.append(avg50)
        if points60 != 0:
            avg60 = count60 / points60
            avgTotal.append(avg60)
        if points70 != 0:
            avg70 = count70 / points70
            avgTotal.append(avg70)
        if points80 != 0:
            avg80 = count80 / points80
            avgTotal.append(avg80)
        if points90 != 0:
            avg90 = count90 / points90
            avgTotal.append(avg90)    
        print avg00
        print points00
        print avg10
        print points10
        print avg20
        print points20
        print avg30
        print points30
        print avg40
        print points40
        print avg50
        print points50
        print avg60
        print points60
        print avg70
        print points70
        print avg80
        print points80
        print avg90
        print points90
        
        self.screwContact.insert(screwIndex, avgTotal)
        '''
              
        '''
        #Calculate percentages 
        corticalPercent = float(corticalCount) / float(totalCount) *100
        cancellousPercent = float(cancellousCount) / float(totalCount) *100
        otherPercent = 100 - corticalPercent - cancellousPercent
        
        print corticalPercent
        print cancellousPercent
        
        coP = str("%.0f" % corticalPercent)
        caP = str("%.0f" % cancellousPercent)
        otP = str("%.0f" % otherPercent)
          
        qtcoP = qt.QTableWidgetItem(coP)
        qtcap = qt.QTableWidgetItem(caP)
        qtotP = qt.QTableWidgetItem(otP)
          
        self.itemsqtcoP.append(qtcoP)
        self.itemsqtcaP.append(qtcap)
        self.itemsqtotP.append(qtotP)
        
        print screwIndex    
        self.screwTable.setItem(screwIndex, 4, qtcoP)
        self.screwTable.setItem(screwIndex, 3, qtcap)
        self.screwTable.setItem(screwIndex, 2, qtotP)
        
        
        
    def chartContact(self, screwCount):
        # Get the Chart View Node
        cvns = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
        cvns.InitTraversal()
        cvn = cvns.GetNextItemAsObject()
        cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
        
        arrayNodes = []
        for i in range(0,screwCount):
            # Create an Array Node and add some data
            dn = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
            arrayNodes.insert(i,dn)
            a = dn.GetArray()
            a.SetNumberOfTuples(10)
            x = range(0, 10)
            screwValues = self.screwContact[i]
            for j in range(len(x)):
                a.SetComponent(j, 0, (j * 10) + 5)
                a.SetComponent(j, 1, screwValues[j])
                a.SetComponent(j, 2, 0)
                print j
                print screwValues[j]
            cn.AddArray('Screw %s' % i, dn.GetID())
        
        dnCort = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
        dnCanc = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
        
        a1 = dnCort.GetArray()
        a2 = dnCanc.GetArray()
        a1.SetNumberOfTuples(2)
        a2.SetNumberOfTuples(2)
        a1.SetComponent(0, 0, 0)
        a1.SetComponent(0, 1, 250)
        a1.SetComponent(0, 2, 0)
        a1.SetComponent(1, 0, 100)
        a1.SetComponent(1, 1, 250)
        a1.SetComponent(1, 2, 0)
        a2.SetComponent(0, 0, 0)
        a2.SetComponent(0, 1, 130)
        a2.SetComponent(0, 2, 0)
        a2.SetComponent(1, 0, 100)
        a2.SetComponent(1, 1, 130)
        a2.SetComponent(1, 2, 0)
        
        cn.AddArray('Cortical Bone', dnCort.GetID())
        cn.AddArray('Cancellous Bone', dnCanc.GetID())

        #cn.SetProperty('default', 'title', 'Information for Screw at point %s' % fidName)
        cn.SetProperty('default', 'title', 'Screw - Bone Contact')
        cn.SetProperty('default', 'xAxisLabel', 'Screw Percentile (Head - Tip)')
        #cn.SetProperty('default', 'xAxisType', 'categorical')
        cn.SetProperty('default', 'yAxisLabel', 'Average HU Contact')
        cn.SetProperty('default', 'showLegend', 'on')
        cn.SetProperty('default', 'type', 'Line')
        cn.SetProperty('default', 'xAxisPad', '0')
        #cn.SetProperty('default', 'xAxisPad', '0')
               
        cvn.SetChartNodeID(cn.GetID())
           
    def clearGrade(self):
        #Clear chart
        self.cvn.SetChartNodeID(None)

        
        #For each fiducial, restore original screw model and remove graded screw model
        fidCollection = slicer.mrmlScene.GetNodesByClass('vtkMRMLAnnotationFiducialNode')
        fidCount = fidCollection.GetNumberOfItems()
        for i in range(0, fidCount):
          fidCollection.GetItemAsObject(i).GetAnnotationPointDisplayNode().SetOpacity(0.0)
            
          fidName = fidCollection.GetItemAsObject(i).GetName()
          collectionS = slicer.mrmlScene.GetNodesByName('Screw at point %s' % fidName)
          screwModel = collectionS.GetItemAsObject(0)
          if screwModel != None:
              modelDisplay = screwModel.GetDisplayNode()
              modelDisplay.SetColor(0.12,0.73,0.91)
              modelDisplay.VisibilityOn()
            
          collectionG = slicer.mrmlScene.GetNodesByName('Grade model-%s' % fidName)
          gradeModel = collectionG.GetItemAsObject(0)
          if gradeModel != None:
              slicer.mrmlScene.RemoveNode(gradeModel)
          
          collectionH = slicer.mrmlScene.GetNodesByName('Head %s' % fidName)
          headModel = collectionH.GetItemAsObject(0)
          if headModel != None:
              slicer.mrmlScene.RemoveNode(headModel)

    def vrUpdate(self, opacity):
      pNode = self.parameterNode()
      vrDisplayNode = Helper.getNodeByID(pNode.GetParameter('vrDisplayNodeID'))
      vrOpacityMap = vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
      vrOpacityMap.RemoveAllPoints()
      vrOpacityMap.AddPoint(0,0)
      vrOpacityMap.AddPoint(self.__cancellousMin-1,0)
      vrOpacityMap.AddPoint(self.__cancellousMin,opacity)
      vrOpacityMap.AddPoint(self.__corticalMax,opacity)
      vrOpacityMap.AddPoint(self.__corticalMax+1,0)