#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __main__ import qt, ctk, vtk, slicer

from PedicleScrewSimulatorWizard import *
#from PedicleScrewSimulatorStep import *
#from .Helper import *

import PythonQt
import numpy as np
import string
import math
import os
import time
import logging

class PlanningMeasurementsStep( PedicleScrewSimulatorStep ):

  def __init__( self, stepid ):
    self.initialize( stepid )
    slicer.util.setDataProbeVisible(False)
    self.setName('4. Adjust Screws')
    self.setDescription("""Select a screw;\nIn the Red Slice or the Yellow Slice, Drag both ends of the analog screw to adjust the length and angle;\nUpdata;\nSelect the Diameter of the screw";\nAfter reaching the ideal size and angle,Click OK Generate the Screw""")
    self.fidlist = []
    self.dimeter = []
    self.length = []
    self.PSA = []
    self.PTA = []
    self.Cdata = None
    self.levels = (
      "C1", "C2", "C3", "C4", "C5", "C6", "C7", "T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9", "T10", "T11",
      "T12",
      "L1", "L2", "L3", "L4", "L5", "S1") #, "place")
    self.buttonToModName = ''

    self.__parent = super( PlanningMeasurementsStep, self )
    qt.QTimer.singleShot(0, self.killButton)



  def killButton(self):
    # hide useless button
    bl = slicer.util.findChildren(text='Final')
    if len(bl):
      bl[0].hide()

  #
  # def stop(self):
  #   selectionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSelectionNodeSingleton")
  #   # place rulers
  #   selectionNode.SetReferenceActivePlaceNodeClassName("vtkMRMLAnnotationRulerNode")
  #   # to place ROIs use the class name vtkMRMLAnnotationROINode
  #   interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
  #   placeModePersistence = 1
  #   interactionNode.SetPlaceModePersistence(placeModePersistence)
  #   # mode 1 is Place, can also be accessed via slicer.vtkMRMLInteractionNode().Place
  #   interactionNode.SetCurrentInteractionMode(2)

  def zoomIn(self):
    logging.debug("zoom")
    slicer.app.applicationLogic().PropagateVolumeSelection(1)


  def createUserInterface( self ):

    self.__layout = self.__parent.createUserInterface()

    self.fid = Helper.Screws()

    self.fids = len(self.fid)
    self.fidlist = ["Choose the insertion site"]
    self.dimeter = []
    self.length = []
    self.PSA = []
    self.PTA = []
    self.CZn = 0
    self.CXn = 0
    self.CLstep = 0
    self.CData = 3.5
    self.cScrew = ""
    self.csNo=0
    self.screwList=[]
    self.manulYn=0

    # logging.debug("fids: {0}".format(self.fids))
    # zheli
    pNode = self.parameterNode()
    print(pNode)
    self.vertebra = str(pNode.GetParameter('vertebra'))
    # logging.debug("椎体")
    logging.debug(self.vertebra)
    self.inst_length = str(pNode.GetParameter('inst_length'))
    self.sides = str(pNode.GetParameter('sides'))

    for i in range(self.levels.index(self.vertebra), self.levels.index(self.vertebra) + int(self.inst_length)):
      # if self.vertebra == "部位":
      #   self.fidlist.append(self.vertebra + "_" + str(i))
      # else:
      if self.sides == "L&R":
        self.fidlist.append(self.levels[i] + "_" + "L")
        self.fidlist.append(self.levels[i] + "_" + "R")
      else:
        self.fidlist.append(self.levels[i] + "_" + self.sides)
    for i, v in enumerate(self.fidlist[1:]):
      Helper.addFid(self.fid[i][1],1,"Isthmus-{}".format(i),v,"pink")

    logging.debug("Fidlist: {0}".format(self.fidlist))
    logging.debug(self.fidlist[0])
    sText = qt.QLabel('Choose the puncture site:')
    self.sSelector = ctk.ctkComboBox()
    self.sSelector.toolTip = "Choose the puncture site"
    # screwList = ['选择穿刺部位', "cS1","cS2","cS3","cS4","cS5"]
    self.sSelector.addItems(self.fidlist)
    self.connect(self.sSelector, PythonQt.QtCore.SIGNAL('activated(QString)'), self.sSelector_chosen)
    self.__sSelector=''

    dText = qt.QLabel('Select screw diameter:')
    self.dSelector = ctk.ctkComboBox()
    self.dSelector.toolTip = "Select screw diameter"
    dimList = ['Select screw diametermm', "2.5","3","3.5","4","4.5","5","5.5","6","6.5","7","7.5","8"]
    self.dSelector.addItems(dimList)
    self.connect(self.dSelector, PythonQt.QtCore.SIGNAL('activated(QString)'), self.dSelector_chosen)
    self.__dSelector=''

    self.QHBox0 = qt.QHBoxLayout()
    self.QHBox0.addWidget(sText)
    self.QHBox0.addWidget(self.sSelector)
    self.QHBox0.addWidget(self.dSelector)
    self.__layout.addRow(self.QHBox0)

    self.manButton = qt.QPushButton("Update")
    self.okButton = qt.QPushButton("OK")
    self.resetButton = qt.QPushButton("Reset")

    self.QHBox9 = qt.QHBoxLayout()
    self.QHBox9.addWidget(self.manButton)
    self.QHBox9.addWidget(self.okButton)
    self.QHBox9.addWidget(self.resetButton)
    # self.QHBox9.addWidget(self.okButton)
    self.__layout.addRow(self.QHBox9)

    self.manButton.connect('clicked(bool)', self.manualUp)
    self.okButton.connect('clicked(bool)', self.okShow)
    self.resetButton.connect('clicked(bool)', self.reset)

    # self.screwsTable.setHorizontalHeaderLabels(horizontalHeaders)
    self.items = []


    # Camera Transform Sliders

    transCam = ctk.ctkCollapsibleButton()
    transCam.text = "Shift Camera Position"
    transCam.collapsed = True
    self.__layout.addWidget(transCam)
    # transCam.collapsed = True
    camLayout = qt.QFormLayout(transCam)
    a = PythonQt.qMRMLWidgets.qMRMLTransformSliders()
    a.setMRMLTransformNode(slicer.mrmlScene.GetNodeByID('vtkMRMLLinearTransformNode4'))
    camLayout.addRow(a)

    qt.QTimer.singleShot(0, self.killButton)
    # self.updateTable()

  def cameraFocus(self, position):
    camera = slicer.mrmlScene.GetNodeByID('vtkMRMLCameraNode1')
    camera.SetFocalPoint(*position)
    camera.SetPosition(position[0], -200, position[2])
    camera.SetViewUp([1, 0, 0])
    camera.ResetClippingRange()

  def sSelector_chosen(self, text):

    if text != "Choose the puncture site":
      self.__sSelector = text
      self.__dSelector = ''
      self.currentFidIndex = self.sSelector.currentIndex-1
      self.currentmodName = "w_{}*".format(self.currentFidIndex)
      logging.debug("self.currentmodName:{}".format(self.currentmodName))
      self.CData=self.fid[self.currentFidIndex]
      self.CDscrew=self.CData[1]
      self.Pz=self.CData[1]
      self.Pa=self.CData[0]
      self.cScrewData=Helper.Screw(self.currentFidIndex,self.Pz)
      currentMod = slicer.util.getNode(self.currentmodName)
      modelDisplay = currentMod.GetDisplayNode()
      modelDisplay.SetSelectedColor(Helper.myColor("red"))
      modelDisplay.SetVisibility2D(True)  # yellow
      # logging.debug("这里{0}{1}".format([self.Pa[0],self.Pa[1],self.Pz[2]],self.Pa))
      self.redSlicerData=   [self.Pz,self.Pa,[self.Pz[0],self.Pa[1],self.Pa[2]]]
      self.yellowSlicerData=[self.Pz,self.Pa,[self.Pa[0],self.Pa[1],self.Pz[2]]]
      position = [0,0,0]
      self.Pzz = slicer.util.getNode("Isthmus-{}".format(self.currentFidIndex))
      self.Pzz.GetNthFiducialPosition(0, position)
      self.cameraFocus(position)
      Helper.UpdateSlicePlane(self.redSlicerData, "Red")
      Helper.UpdateSlicePlane(self.yellowSlicerData, "Yellow",2,1)
      # slicer.util.setSliceViewerLayers(self.vol, fit=True)

  def dSelector_chosen(self, text):

    if text != "Select the diameter of the screw":
      self.__dSelector = float(text)
      self.Cdata = Helper.Screw(self.currentFidIndex, self.Pz, self.__dSelector)
      logging.debug("self.currentFidIndex:{}".format(self.currentFidIndex))

  def manualUp(self):
    self.Cdata = Helper.Screw(self.currentFidIndex, self.Pz,manulYN =True)
    logging.debug("self.currentFidIndex:{}".format(self.currentFidIndex))

  def okShow(self):
    lineNode = "w_{}*".format(self.currentFidIndex)
    lineN = Helper.Psline(lineNode)
    PB = lineN[0]
    PT = lineN[1]
    Dim = lineN[3]
    # Length = lineN[3]
    markupsNode=slicer.util.getNode(lineNode)
    markupsNode.CreateDefaultDisplayNodes()
    dn = markupsNode.GetDisplayNode()
    dn.SetGlyphTypeFromString("CrossDot2D")
    dn.SetGlyphScale(1)
    # Helper.delNode(lineNode)
    screwName = "Screw_{}".format(self.__sSelector)
    # Pz0 = Helper.p2pexLine(PB,self.Pz,10)
    # Helper.p2pCyl(Pz0,self.Pz)
    PB_Pz=np.linalg.norm(PT-PB)*(self.Pz[1]-PB[1])/(PT[1]-PB[1])
    logging.debug("PB_Pz:{}".format(PB_Pz))
    PZ = Helper.p2pexLine(PB,PT,5+PB_Pz-np.linalg.norm(PT-PB))
    # PZ0 = Helper.p2pexLine(PB,PT,PB_Pz-np.linalg.norm(PT-PB))
    # Helper.addFid(PZ)
    # Helper.addFid(PZ0)
    Helper.p2pCyl(PZ, PB, Dim*.5, "Isthmus_{}".format(screwName), 5 - PB_Pz, 12, "white", .5)
    Helper.p2pCyl(PB, PT, Dim*.5, screwName, 0, 12, "white", .25)
    screwAngle = Helper.screwAngle(self.currentFidIndex, PZ)
    logging.debug("screwAngle:{}".format(screwAngle))
    if self.Cdata is None:
      self.screwList.append([self.__sSelector, 90-screwAngle[0],screwAngle[1],self.cScrewData[0], self.cScrewData[1], self.cScrewData[2],  self.cScrewData[3], self.Pz])
    else:
      self.screwList.append([self.__sSelector, 90-screwAngle[0],screwAngle[1],self.Cdata[0], self.Cdata[1], self.Cdata[2], self.Cdata[3],self.Pz])

  def reset(self):
    self.Pz = self.CData[1]
    self.Pa = self.CData[0]
    self.cScrewData = Helper.Screw(self.currentFidIndex, self.Pz)
    # pass

  def validate( self, desiredBranchId ):
    self.__parent.validate( desiredBranchId )

    self.__parent.validationSucceeded(desiredBranchId)

  def onEntry(self, comingFrom, transitionType):

    super(PlanningMeasurementsStep, self).onEntry(comingFrom, transitionType)

    qt.QTimer.singleShot(0, self.killButton)

    lm = slicer.app.layoutManager()
    if lm == None:
      return
    lm.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)

    viewNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
    for viewNode in viewNodes:
      viewNode.SetSliceIntersectionVisibility(1)

  # super(PlanningMeasurementsStep, self).onExit(goingTo, transitionType)
  def onExit(self, goingTo, transitionType):
    super(PlanningMeasurementsStep, self).onExit(goingTo, transitionType)
    logging.debug("exiting")
    # Disable Slice Intersections
    viewNodes = slicer.util.getNodesByClass('vtkMRMLSliceCompositeNode')
    for viewNode in viewNodes:
      viewNode.SetSliceIntersectionVisibility(0)

    if goingTo.id() == 'Grade':
      logging.debug("Grade")
      self.doStepProcessing()
    #
    # self.stop()

    if goingTo.id() != 'Landmarks' and goingTo.id() != 'Grade':
      return



  def doStepProcessing(self):
    logging.debug('resultList:{}'.format(self.screwList))
    logging.debug('Done')
