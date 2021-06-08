from __main__ import qt, ctk, vtk, slicer

from .PedicleScrewSimulatorStep import *
from .Helper import *
import math
import logging
import numpy as np


class GradeStep(PedicleScrewSimulatorStep):

  def __init__( self, stepid ):
    self.initialize( stepid )
    self.setName( 'Grade' )
    self.setDescription( 'Grading Step' )
    self.screwName = []
    self.__corticalMin = 250
    self.__corticalMax = 1200
    self.__cancellousMin = 130
    self.__cancellousMax = 250
    self.screwLoc=[]
    self.itemsqtcoP = []
    self.itemsqtcaP = []
    self.itemsqtotP = []
    self.pointsArray = []
    self.screwContact = []
    self.screwCount = 0
    self.cvn = None

    self.__parent = super( GradeStep, self )

  def killButton(self):
    # hide useless button
    bl = slicer.util.findChildren(text='Final')
    if len(bl):
      bl[0].hide()

  def createUserInterface( self ):

    self.__layout = self.__parent.createUserInterface()

    ln = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLLayoutNode')
    ln.SetViewArrangement(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalPlotView)

    modLabel = qt.QLabel('Choose the puncture site:')
    # Paint Screw Button
    self.__selectScrewButton = qt.QPushButton("Grade Screws")
    self.__layout.addWidget(self.__selectScrewButton)
    self.__selectScrewButton.connect('clicked(bool)', self.gradeScrews)

    self.fiducial = self.fiducialNode()
    self.fidNumber = self.fiducial.GetNumberOfFiducials()*2/3
    self.screwList = slicer.modules.PedicleScrewSimulatorWidget.measurementsStep.screwList
    self.screwNumber = len(self.screwList)
    logging.debug("self.screwList:{}".format(self.screwList))

    # self.screwTable.setRowCount(self.screwNumber)

    # Screw Table
    horizontalHeaders = ["puncture site","Screw\n Size","Angle\n TPA/SPA","% Screw in\nSoft Tissue\n (<130HU)","% Screw in\nLD Bone\n (130-250HU)","% Screw in\nHD Bone\n (>250HU)" ]
    self.screwTable = qt.QTableWidget(self.screwNumber, 6)
    self.screwTable.sortingEnabled = False
    self.screwTable.setEditTriggers(1)
    self.screwTable.setMinimumHeight(self.screwTable.verticalHeader().length())
    self.screwTable.horizontalHeader().setSectionResizeMode(qt.QHeaderView.Stretch)
    self.screwTable.setSizePolicy (qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Preferred)
    self.screwTable.itemSelectionChanged.connect(self.onTableCellClicked)
    self.__layout.addWidget(self.screwTable)

    self.screwTable.setHorizontalHeaderLabels(horizontalHeaders)



    self.updateWidgetFromParameters(self.parameterNode())
    qt.QTimer.singleShot(0, self.killButton)

    self.updateTable()

  def onTableCellClicked(self):
    if self.screwTable.currentColumn() == 0:
      logging.debug(self.screwTable.currentRow())
      self.currentFid = self.screwTable.currentRow()
      logging.debug("self.currentFid:{}".format(self.currentFid))
      logging.debug("self.screwLoc[self.currentFid]:{}".format(self.screwLoc[self.currentFid]))
      position = [0,0,0]
      self.Pz = slicer.util.getNode("Isthmus-{}".format(self.currentFid))
      self.Pz.GetNthFiducialPosition(0, position)
      self.cameraFocus(position)
      self.sliceChange()
      #self.updateChart(self.screwList[self.currentFid])


  def cameraFocus(self, position):
    camera = slicer.mrmlScene.GetNodeByID('vtkMRMLCameraNode1')
    camera.SetFocalPoint(*position)
    camera.SetPosition(position[0],-200,position[2])
    camera.SetViewUp([1,0,0])
    camera.ResetClippingRange()

  def updateTable(self):
    self.itemsLoc = []
    self.itemsLD = []
    self.itemsAng = []
    # self.itemsDia = []

    self.screwList = slicer.modules.PedicleScrewSimulatorWidget.measurementsStep.screwList
    self.screwNumber = len(self.screwList)
    self.screwTable.setRowCount(self.screwNumber)
    for i in range(self.screwNumber):
      currentScrew = self.screwList[i]
      self.screwLoc = str(currentScrew[0])
      screwLD = str(currentScrew[3]) + " x " + str(currentScrew[4])
      screwAng = str(currentScrew[1]) + " / " + str(currentScrew[2])

      qtscrewLoc = qt.QTableWidgetItem(self.screwLoc)
      qtscrewLD = qt.QTableWidgetItem(screwLD)
      qtscrewAng = qt.QTableWidgetItem(screwAng)
      #qtscrewDia = qt.QTableWidgetItem(screwDia)

      self.itemsLoc.append(qtscrewLoc)
      self.itemsLD.append(qtscrewLD)
      self.itemsAng.append(qtscrewAng)
      #self.itemsDia.append(qtscrewDia)
      self.screwName.append("Isthmus_Screw_{}".format(self.screwLoc))

    # logging.debug(self.screwName)
      logging.debug("self.screwName:{}".format(self.screwName))


      self.screwTable.setItem(i, 0, qtscrewLoc)
      self.screwTable.setItem(i, 1, qtscrewLD)
      self.screwTable.setItem(i, 2, qtscrewAng)

      #self.screwTable.setItem(i, 2, qtscrewDia)



  def validate( self, desiredBranchId ):
    '''
    '''
    self.__parent.validate( desiredBranchId )
    self.__parent.validationSucceeded(desiredBranchId)

  def onEntry(self, comingFrom, transitionType):

    super(GradeStep, self).onEntry(comingFrom, transitionType)

    ln = slicer.mrmlScene.GetFirstNodeByClass('vtkMRMLLayoutNode')
    ln.SetViewArrangement(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalPlotView)

    pNode = self.parameterNode()

    self.fidNode = self.fiducialNode()

    self.vrUpdate(0.03)

    qt.QTimer.singleShot(0, self.killButton)



  def onExit(self, goingTo, transitionType):

    if goingTo.id() == 'Screw':
      self.clearGrade()

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
    logging.debug('Done')

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
    # logging.debug("fidlist:".format(self.screwName[0]))
    #self.fid = self.__modelSelector.currentNode()
    #self.sliceChange()
    self.screwContacts = []
    pNode = self.parameterNode()

    self.__inputScalarVol = pNode.GetNodeReference('croppedBaselineVolume')
    # logging.debug("scalar:".format(self.__inputScalarVosl))
    for x,v in enumerate(self.screwName):
      fidName = v
      logging.debug("fidName{}".format(fidName))
      screwIndex = x
      # if fidName != None:
      contact=self.gradeScrew(fidName, screwIndex)
      logging.debug("contact:{}".format(contact))
      self.screwContacts.append(contact)
      logging.debug("self.screwContacts:{}".format(self.screwContacts))
      
      # self.screwCount += 1
      # if x==0:
      #   screwContacts=[contact]
      # else:
      #   screwContacts=np.append(screwContacts,contact)
    self.screwCount = self.screwNumber
    # self.screwContacts = np.array(screwContacts.reshape(self.screwCount,len(contact)))

    # logging.debug("self.screwCount:{}".format(self.screwCount))
    # logging.debug("self.screwContacts:{}".format(self.screwContacts))
    #
    # logging.debug("self.screwCount:{}".format(self.screwCount))
    self.chartContact(self.screwCount)

  def screwProbe(self, modelNode, volumeNode):
    """
	Function to loop through the "ProbeVolumeWithModel" function in Slicer.
	Input: Surface Name, Volume Name Prefix, Image Start, Number of Images
	"""
    probe = slicer.modules.probevolumewithmodel
    parameters = {}
    parameters['InputModel'] = slicer.util.getNode(modelNode)
    outModel = slicer.vtkMRMLModelNode()
    outModel.SetName("grabe{}".format(modelNode))
    slicer.mrmlScene.AddNode(outModel)
    parameters['InputVolume'] = slicer.util.getNode(volumeNode)
    parameters['OutputModel'] = outModel
    slicer.cli.runSync(probe, None, parameters)
    #     contact(outModel,modelNode,1)
    return


  def gradeScrew(self, screwModel, screwIndex, volumeNode="baselineROI"):

    volume_node = slicer.util.getNode(volumeNode)
    voxels = slicer.util.arrayFromVolume(volume_node)  # get voxels as a numpy array#获取像numpy阵列一样的voxels
    Seg = 12
    totalCount = 20
    VVList = []
    Pdata = Helper.Pcoord(screwModel)[2]
    corticalCount = 0
    cancellousCount = 0
    # totalCount = 0
    for i in range(Seg):
      P1 = Pdata[2 * i]
      P2 = Pdata[2 * i + 1]
      for j in range(totalCount):
        L = np.linalg.norm(P1 - P2)
        P = Helper.p2pexLine(P1, P2, -L * j / totalCount)
        volumeRasToIjk = vtk.vtkMatrix4x4()
        volume_node.GetRASToIJKMatrix(volumeRasToIjk)
        point_Ijk = [0, 0, 0, 1]
        volumeRasToIjk.MultiplyPoint(np.append(P, 1.0), point_Ijk)
        point_Ijk = [int(round(c)) for c in point_Ijk[0:3]]
        voxelValue = voxels[point_Ijk[2], point_Ijk[1], point_Ijk[0]]
        if j == 0:
          VVlist = np.array([voxelValue])
        else:
          VVlist = np.append(VVlist, voxelValue)
      VVList.append(VVlist)
    self.screwContact = np.array(VVList).mean(axis=0)
    logging.debug("screwContact:{}".format(self.screwContact))
    logging.debug("VVList:{}".format(VVList))
    for count,value in enumerate(self.screwContact):
      if value >= self.__corticalMin:
        corticalCount += 1
      elif self.__cancellousMax > value >= self.__cancellousMin:
        cancellousCount += 1
# Calculate percentages
    corticalPercent = float(corticalCount) / float(totalCount) * 100
    cancellousPercent = float(cancellousCount) / float(totalCount) * 100
    otherPercent = 100 - corticalPercent - cancellousPercent

    logging.debug("cancellousPercent:{}".format(cancellousPercent))
    logging.debug("corticalPercent:{}".format(corticalPercent))
    
    coP = str("%.0f" % corticalPercent)
    caP = str("%.0f" % cancellousPercent)
    otP = str("%.0f" % otherPercent)
    logging.debug("otP:{}".format(otP))

    qtcoP = qt.QTableWidgetItem(coP)
    qtcap = qt.QTableWidgetItem(caP)
    qtotP = qt.QTableWidgetItem(otP)

    self.itemsqtcoP.append(qtcoP)
    self.itemsqtcaP.append(qtcap)
    self.itemsqtotP.append(qtotP)

    # logging.debug("screwIndex{}".format(screwIndex))
    self.screwTable.setItem(screwIndex, 5, qtcoP)
    self.screwTable.setItem(screwIndex, 4, qtcap)
    self.screwTable.setItem(screwIndex, 3, qtotP)

    self.screwProbe(screwModel, volumeNode)

    return self.screwContact

    # encoding=utf-8
  def chartContact(self, screwCount):
    # Show this chart in the plot view 在绘图视图中显示此图表
    # screwCount = 2
    plotWidget = slicer.app.layoutManager().plotWidget(0)
    plotViewNode = plotWidget.mrmlPlotViewNode()

    # Retrieve/Create plot chart#检索/创建图
    plotChartNode = plotViewNode.GetPlotChartNode()
    if not plotChartNode:
      plotChartNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotChartNode", "Isthmus_Screw - Bone Contact chart")
      plotViewNode.SetPlotChartNodeID(plotChartNode.GetID())
    plotChartNode.SetTitle("Screw - Bone Contact")
    plotChartNode.SetXAxisTitle('Isthmus_Screw Percentile Length')
    plotChartNode.SetYAxisTitle('Average HU Contact')

    # Retrieve/Create plot table#检索/创建表
    firstPlotSeries = plotChartNode.GetNthPlotSeriesNode(0)
    plotTableNode = firstPlotSeries.GetTableNode() if firstPlotSeries else None
    if not plotTableNode:
      plotTableNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLTableNode", "Isthmus_Screw - Bone Contact table")

    # Set x, cortical bone, and cancellous bone columns#设置x、皮质骨和松质骨柱分界线
    plotTableNode.RemoveAllColumns()
    arrX = vtk.vtkFloatArray()
    arrX.SetName("Isthmus_Screw Length")
    plotTableNode.AddColumn(arrX)
    arrCortical = vtk.vtkFloatArray()
    arrCortical.SetName("Cortical Bone")
    plotTableNode.AddColumn(arrCortical)
    arrCancellous = vtk.vtkFloatArray()
    arrCancellous.SetName("Cancellous Bone")
    plotTableNode.AddColumn(arrCancellous)
    # arrIsthmus0 = vtk.vtkFloatArray()
    # arrIsthmus0.SetName("arrIsthmus0")
    # plotTableNode.AddColumn(arrIsthmus0)
    # arrIsthmus1 = vtk.vtkFloatArray()
    # arrIsthmus1.SetName("arrIsthmus1")
    # plotTableNode.AddColumn(arrIsthmus1)

    numPoints = 20
    plotTable = plotTableNode.GetTable()
    plotTable.SetNumberOfRows(numPoints)
    for i in range(numPoints):
      plotTable.SetValue(i, 0, i*.5)
      plotTable.SetValue(i, 1, 250)
      plotTable.SetValue(i, 2, 130)
      # plotTable.SetValue(i, 3, 5)
      # plotTable.SetValue(i, 4, 15)

    arrays = [arrCortical, arrCancellous]

    for i in range(screwCount):
      # Create an Array Node and add some data
      arrScrew = vtk.vtkFloatArray()
      arrScrew.SetName('Screw %s' % i)
      arrScrew.SetNumberOfValues(numPoints)
      screwValues = self.screwContacts[i]
      for j in range(numPoints):
        arrScrew.SetValue(j, screwValues[j])
      plotTableNode.AddColumn(arrScrew)
      arrays.append(arrScrew)

    # Update/Create plot series
    for arrIndex, arr in enumerate(arrays):
      plotSeriesNode = plotChartNode.GetNthPlotSeriesNode(arrIndex)
      if not plotSeriesNode:
        plotSeriesNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLPlotSeriesNode")
        plotChartNode.AddAndObservePlotSeriesNodeID(plotSeriesNode.GetID())
      plotSeriesNode.SetName("{0}".format(arr.GetName()))
      plotSeriesNode.SetAndObserveTableNodeID(plotTableNode.GetID())
      plotSeriesNode.SetXColumnName(arrX.GetName())
      plotSeriesNode.SetYColumnName(arr.GetName())
      plotSeriesNode.SetPlotType(slicer.vtkMRMLPlotSeriesNode.PlotTypeScatter)
      if arrIndex < 2:
        # two constant lines
        plotSeriesNode.SetLineStyle(slicer.vtkMRMLPlotSeriesNode.LineStyleDash)
      else:
        plotSeriesNode.SetLineStyle(slicer.vtkMRMLPlotSeriesNode.LineStyleSolid)
      plotSeriesNode.SetMarkerStyle(slicer.vtkMRMLPlotSeriesNode.MarkerStyleNone)
      plotSeriesNode.SetUniqueColor()
      # plotChartNode.XAxisRangeAutoOff()
      # plotChartNode.SetXAxisRange(0, 100)

    # Remove extra series nodes
    for i in range(plotChartNode.GetNumberOfPlotSeriesNodes() - len(arrays)):
      plotChartNode.RemoveNthPlotSeriesNodeID(plotChartNode.GetNumberOfPlotSeriesNodes() - 1)

  def clearGrade(self):
    #Clear chart
    if self.cvn:
      self.cvn.SetChartNodeID(None)


    #For each fid, restore original screw model and remove graded screw model
    fiducial = self.fiducialNode()
    fidCount = fiducial.GetNumberOfFiducials()
    for i in range(fidCount):
      fiducial.SetNthFiducialVisibility(i, False)
      fidName = fiducial.GetNthFiducialLabel(i)
      screwModel = slicer.mrmlScene.GetFirstNodeByName('Screw at point %s' % fidName)
      if screwModel != None:
        modelDisplay = screwModel.GetDisplayNode()
        modelDisplay.SetColor(0.12,0.73,0.91)
        modelDisplay.VisibilityOn()

      gradeModel = slicer.mrmlScene.GetFirstNodeByName('Grade model-%s' % fidName)
      if gradeModel != None:
        slicer.mrmlScene.RemoveNode(gradeModel)

      headModel = slicer.mrmlScene.GetFirstNodeByName('Head %s' % fidName)
      if headModel != None:
        slicer.mrmlScene.RemoveNode(headModel)

  def vrUpdate(self, opacity):
    pNode = self.parameterNode()
    vrDisplayNode = pNode.GetNodeReference('vrDisplayNode')
    vrOpacityMap = vrDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
    vrOpacityMap.RemoveAllPoints()
    vrOpacityMap.AddPoint(0,0)
    vrOpacityMap.AddPoint(self.__cancellousMin-1,0)
    vrOpacityMap.AddPoint(self.__cancellousMin,opacity)
    vrOpacityMap.AddPoint(self.__corticalMax,opacity)
    vrOpacityMap.AddPoint(self.__corticalMax+1,0)
