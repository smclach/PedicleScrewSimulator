# slicer imports
from __main__ import vtk, slicer

# python includes
import logging
import sys
import time
import numpy as np
import os
import math


class Helper( object ):
  '''
  classdocs
  '''

  @staticmethod
  def Info( message ):
    '''

    '''

    #logging.debug("[PedicleScrewSimulatorPy " + time.strftime( "%Y-%m-%d %H:%M:%S" ) + "]: " + str( message ))
    #sys.stdout.flush()

  @staticmethod
  def Warning( message ):
    '''

    '''

    #logging.debug("[PedicleScrewSimulatorPy " + time.strftime( "%Y-%m-%d %H:%M:%S" ) + "]: WARNING: " + str( message ))
    #sys.stdout.flush()

  @staticmethod
  def Error( message ):
    '''

    '''

    logging.debug("[PedicleScrewSimulatorPy " + time.strftime( "%Y-%m-%d %H:%M:%S" ) + "]: ERROR: " + str( message ))
    sys.stdout.flush()

  @staticmethod
  def ErrorPopup( message ):
    '''

    '''
    messageBox = qt.QMessageBox()
    messageBox.critical(None,'',message)

  @staticmethod
  def Debug( message ):
    '''

    '''

    showDebugOutput = 0
    from time import strftime
    if showDebugOutput:
        logging.debug("[PedicleScrewSimulatorPy " + time.strftime( "%Y-%m-%d %H:%M:%S" ) + "] DEBUG: " + str( message ))
        sys.stdout.flush()

  @staticmethod
  def CreateSpace( n ):
    '''
    '''
    spacer = ""
    for s in range( n ):
      spacer += " "

    return spacer

  @staticmethod
  def GetNthStepId( n ):
    '''
    '''
    steps = [None, # 0
             'LoadData', # 1
             'DefineROI', #2
             'Measurements', #3
             'Landmarks', #4
             'Final', #5
             ]

    if n < 0 or n > len( steps ):
      n = 0

    return steps[n]

  @staticmethod
  def SetBgFgVolumes(bg):
    appLogic = slicer.app.applicationLogic()
    selectionNode = appLogic.GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(bg)
    appLogic.PropagateVolumeSelection()

  @staticmethod
  def SetLabelVolume(lb):
    appLogic = slicer.app.applicationLogic()
    selectionNode = appLogic.GetSelectionNode()
    selectionNode.SetReferenceActiveLabelVolumeID(lb)
    appLogic.PropagateVolumeSelection()

  @staticmethod
  def findChildren(widget=None,name="",text=""):
    """ return a list of child widgets that match the passed name """
    # TODO: figure out why the native QWidget.findChildren method
    # does not seem to work from PythonQt
    if not widget:
      widget = mainWindow()
    children = []
    parents = [widget]
    while parents != []:
      p = parents.pop()
      parents += p.children()
      if name and p.name.find(name)>=0:
        children.append(p)
      elif text:
        try:
          p.text
          if p.text.find(text)>=0:
            children.append(p)
        except AttributeError:
          pass
    return children

  @staticmethod
  def getNodeByID(id):
    return slicer.mrmlScene.GetNodeByID(id)

  @staticmethod
  def readFileAsString(fname):
    s = ''
    with open(fname, 'r') as f:
      s = f.read()
    return s

  @staticmethod
  def probeVolume(P1, P2, Ps=20, thV=150, Vol="baselineROI"):
    volumeNode = slicer.util.getNode(Vol)
    voxels = slicer.util.arrayFromVolume(volumeNode)
    L = int(np.linalg.norm(P1-P2))
    for j in range(Ps+L, 0, -1):
      P = Helper.p2pexLine(P1, P2, j-L)
      #   addFid(P,lableName="{}".format(j))
      volumeRasToIjk = vtk.vtkMatrix4x4()
      volumeNode.GetRASToIJKMatrix(volumeRasToIjk)
      point_Ijk = [0, 0, 0, 1]
      volumeRasToIjk.MultiplyPoint(np.append(P, 1.0), point_Ijk)
      point_Ijk = [int(round(c)) for c in point_Ijk[0:3]]
      voxelValue = voxels[point_Ijk[2], point_Ijk[1], point_Ijk[0]]
      if voxelValue > thV:
        # Helper.addFid(P, 1, lableName="PB")
        return P

  @staticmethod
  def myColor(colorName):
    if colorName == "red":
      colorArr = [1, 0, 0]
    elif colorName == "green":
      colorArr = [0, 1, 0]
    elif colorName == "blue":
      colorArr = [0, 0, 1]
    elif colorName == "black":
      colorArr = [0, 0, 0]
    elif colorName == "white":
      colorArr = [1, 1, 1]
    elif colorName == "yellow":
      colorArr = [1, 1, 0]
    elif colorName == "pink":
      colorArr = [1, 0, 1]
    elif colorName == "cyan":
      colorArr = [0, 1, 1]
    return (colorArr)

  @staticmethod
  def p2pexLine(pos1, pos2, plus=200, Dim=5.0, modName="", color="red", Visibility2D=True):
    """The coordinates of the point-to-point line and extension line"""
    direction = (pos2 - pos1) / np.linalg.norm(pos2 - pos1)
    pos3 = pos1 + direction / np.linalg.norm(direction) * (plus + np.linalg.norm(pos2 - pos1))
    if modName != "":
      markupsNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsLineNode', modName)
      markupsNode.AddControlPoint(vtk.vtkVector3d(pos1))
      markupsNode.AddControlPoint(vtk.vtkVector3d(pos3))
      markupsNode.CreateDefaultDisplayNodes()
      dn = markupsNode.GetDisplayNode()
      dn.SetGlyphTypeFromString("CrossDot2D")
      dn.SetGlyphScale(Dim * 10)

      # dn.SetSliceIntersectionThickness(3)
      dn.SetSelectedColor(Helper.myColor(color))
      # dn.SetSliceDisplayModeToProjection()
      dn.SetVisibility2D(Visibility2D)
      # Hide measurement result while markup up
      markupsNode.GetMeasurement('length').SetEnabled(True)
    return np.array(pos3)

  @staticmethod
  def Psline(nodName):
    """Take the line coordinates"""
    lineNode = slicer.util.getNode(nodName)
    lineStartP = np.zeros(3)
    lineEndP = np.zeros(3)
    lineNode.GetNthControlPointPositionWorld(0, lineStartP)
    lineNode.GetNthControlPointPositionWorld(1, lineEndP)
    length = lineNode.GetMeasurement('length').GetValue()
    dn = lineNode.GetDisplayNode()
    Dim = dn.GetGlyphScale()/10
    return lineStartP, lineEndP,length,Dim

  # @staticmethod
  def addFid(data, Dim=.5, nodName="N", lableName="1", color="red", GlyphType=1):
    """add a larger point"""
    xyz = tuple(data)
    tipFiducial = slicer.mrmlScene.AddNode(slicer.vtkMRMLMarkupsFiducialNode())
    tipFiducial.SetName(nodName)
    tipFiducial.AddFiducial(xyz[0], xyz[1], xyz[2])
    tipFiducial.SetNthFiducialLabel(0, lableName)
    slicer.mrmlScene.AddNode(tipFiducial)
    tipFiducial.SetDisplayVisibility(True)
    tipFiducial.GetDisplayNode().SetGlyphType(GlyphType)  # Vertex2D
    tipFiducial.GetDisplayNode().SetGlyphScale(Dim*10)
    tipFiducial.GetDisplayNode().SetTextScale(3)
    tipFiducial.GetDisplayNode().SetSelectedColor(Helper.myColor(color))
    '''	GlyphShapes {
      GlyphTypeInvalid = 0, 1-StarBurst2D, 2-Cross2D, 3-CrossDot2D,
      4-ThickCross2D, 5-Dash2D, 6-Sphere3D, 7-Vertex2D,
      8-Circle2D,9-Triangle2D, 10-Square2D, Diamond2D,
      Arrow2D, ThickArrow2D, HookedArrow2D, GlyphType_Last
    }'''

  @staticmethod
  def p3Angle(P0, P1, P2):
    """3 o'clock angle"""
    markupsNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsAngleNode')
    markupsNode.AddControlPoint(vtk.vtkVector3d(P0))
    markupsNode.AddControlPoint(vtk.vtkVector3d(P1))
    markupsNode.AddControlPoint(vtk.vtkVector3d(P2))
    measurement = markupsNode.GetMeasurement("angle").GetValue()
    
    slicer.mrmlScene.AddNode(markupsNode)
    markupsNode.SetDisplayVisibility(False)
    return np.around(measurement, 1)

  @staticmethod
  def UpdateSlicePlane(data, view,P1=1,P2=2):
    """Three o'clock RedSlicer"""
    #   a = data
    #   points = data
    points = np.array([list(zip(*data))])[0]
    #     b2 = np.array([list(zip(*a))])
    sliceNode = slicer.app.layoutManager().sliceWidget(view).mrmlSliceNode()
    planePosition = points.mean(axis=1)
    #   print (planePosition)
    planeNormal = np.cross(points[:, 1] - points[:, 0], points[:, 2] - points[:, 0])
    # pPlane1 = 2 if view == "Red" else 1
    # pPlane2 = 1 if view == "Yellow" else 2
    # (pPlane1, pPlane2) = (2, 1) if view == "red" else (1, 2)
    planeX = points[:, P1] - points[:, P2]
    sliceNode.SetSliceToRASByNTP(planeNormal[0], planeNormal[1], planeNormal[2],
                                 planeX[0], planeX[1], planeX[2],
                                 planePosition[0], planePosition[1], planePosition[2], 0)
  @staticmethod
  def p2pCyl(startPoint, endPoint, radius=10, modName="Cyl", plus=0, Seg=3,
             color="red", Opacity=1, RotY=0, Tx = 0):
    """12 prisms of point-to-point"""
    cylinderSource = vtk.vtkCylinderSource()
    cylinderSource.SetRadius(radius)
    cylinderSource.SetResolution(Seg)

    rng = vtk.vtkMinimalStandardRandomSequence()
    rng.SetSeed(8775070)  # For testing 8775070

    # Compute a basis
    normalizedX = [0] * 3
    normalizedY = [0] * 3
    normalizedZ = [0] * 3

    # The X axis is a vector from start to end
    vtk.vtkMath.Subtract(endPoint, startPoint, normalizedX)
    length = vtk.vtkMath.Norm(normalizedX) + plus
    #     length = 20
    vtk.vtkMath.Normalize(normalizedX)

    # The Xn axis is an arbitrary vector cross X
    arbitrary = [0] * 3
    for i in range(0, 3):
      rng.Next()
      arbitrary[i] = rng.GetRangeValue(-10, 10)
    vtk.vtkMath.Cross(normalizedX, arbitrary, normalizedZ)
    vtk.vtkMath.Normalize(normalizedZ)

    # The Zn axis is Xn cross X
    vtk.vtkMath.Cross(normalizedZ, normalizedX, normalizedY)
    matrix = vtk.vtkMatrix4x4()
    # Create the direction cosine matrix
    matrix.Identity()
    for i in range(0, 3):
      matrix.SetElement(i, 0, normalizedX[i])
      matrix.SetElement(i, 1, normalizedY[i])
      matrix.SetElement(i, 2, normalizedZ[i])
    # Apply the transforms
    transform = vtk.vtkTransform()
    transform.Translate(startPoint)  # translate to starting point
    transform.Concatenate(matrix)  # apply direction cosines
    transform.RotateZ(-90.0)  # align cylinder to x axis
    transform.Scale(1.0, length, 1.0)  # scale along the height vector
    transform.Translate(0, .5, 0)  # translate to start of cylinder
    transform.RotateY(RotY)
    transform.Translate(Tx, 0, 0)

    # Transform the polydata
    transformPD = vtk.vtkTransformPolyDataFilter()
    transformPD.SetTransform(transform)
    transformPD.SetInputConnection(cylinderSource.GetOutputPort())

    stlMapper = vtk.vtkPolyDataMapper()
    stlMapper.SetInputConnection(transformPD.GetOutputPort())
    vtkNode = slicer.modules.models.logic().AddModel(transformPD.GetOutputPort())
    vtkNode.SetName(modName)
    modelDisplay = vtkNode.GetDisplayNode()
    modelDisplay.SetColor(Helper.myColor(color))
    modelDisplay.SetOpacity(Opacity)
    modelDisplay.SetBackfaceCulling(0)
    # modelDisplay.SetVisibility(1)
    modelDisplay.SetVisibility2D (True)
    # modelDisplay.SetSliceDisplayModeToProjection()
    # dn.SetVisibility2D(True)
    return

  @staticmethod
  def Pcoord(modName="CylR"):
    """Find the diameter cylinder axis and edge coordinate points"""
    modelNode = slicer.util.getNode(modName)  # Read the node (module)
    sr = modelNode.GetPolyData()  # module turn polygons
    pxyz = [0, 0, 0]
    NumP = sr.GetNumberOfPoints()  # The number of points in the polygon
    for i in range(NumP // 2):  # circulate: i=NumP//2
      sr.GetPoint(i, pxyz)  # Get the point coordinates in turn
      # becomes a matrix
      if i == 0:
        Pxyz = np.array([pxyz])
      else:
        Pxyz = np.append(Pxyz, np.array([pxyz]), axis=0)
    axisMed0 = (Pxyz[0] + Pxyz[NumP // 4]) / 2
    axisMed1 = (Pxyz[1] + Pxyz[1 + NumP // 4]) / 2
    dimeter = np.linalg.norm(Pxyz[0] - Pxyz[NumP // 4])
    return np.array([axisMed0, axisMed1]), np.around(dimeter),Pxyz

  @staticmethod
  def delNode(nodeName):
    """What to do to delete multiple Node deletions of nodes (TODO)."""
    slicer.util.getNode(nodeName)
    slicer.mrmlScene.RemoveNode(slicer.util.getNode(nodeName))
    return

  @staticmethod
  def Pdata(fidNode="T", groups=2):
    """Read the value of the fidlist"""
    fidList = slicer.util.getNode(fidNode)
    numFids = fidList.GetNumberOfFiducials()
    Mdata = [0,0,0]
    for i in range(numFids):
      ras = [0, 0, 0]
      #         Mdata = [0,0,0]
      fidList.GetNthFiducialPosition(i, ras)
      if i == 0:
        Mdata = np.array([ras])
      else:
        Mdata = np.append(Mdata, np.array([ras]), axis=0)
    data = np.array(Mdata).ravel()
    zcount = int(data.size / (3*groups))
    data = np.array(data.reshape(zcount, groups, 3))
    # ras = [-1, -1, 1] * data  # ras coordinate
    return (data)

  @staticmethod
  def Pdata3(fidName="T",N=0):
    """Three o'clock turns two o'clock"""
    Data = Helper.Pdata(fidName, 3)
    Numzhuiti = Data.shape[0]
    #   Data3 = []
    for i in range(0, Numzhuiti):
      Pa = Data[i, 0]
      Pl = Data[i, 1]
      Pr = Data[i, 2]
      Plo = Pa[1]-Pl[1]
      Pro = Pa[1]-Pr[1]
      Pal = Pa+[0,Plo*N,0]
      Par = Pa+[0,Pro*N,0]

      if i == 0:
        Data3 = np.array([Pal])
        Data3 = np.append(Data3, Pl)
        Data3 = np.append(Data3, Par)
        Data3 = np.append(Data3, Pr)
      else:
        Data3 = np.append(Data3, Pal)
        Data3 = np.append(Data3, Pl)
        Data3 = np.append(Data3, Par)
        Data3 = np.append(Data3, Pr)
    Data3 = np.array(Data3.reshape(Data.shape[0] * 2, 2, 3))
    return Data3


  @staticmethod
  def Screws(fidName="T"):
    """Show the screw"""
    Data = Helper.Pdata3(fidName)  # Gets the data coordinates
    Pa = Data[:, 0, :]
    Pz = Data[:, 1, :]
    # P0 = FidP[0]
    fids = Data.shape[0]  # The number of groups
    for i in range(fids):
      PA = Pa[i]  # The front point of the vertebrae
      PZ = Pz[i]  # The narrowest point
      boneP = Helper.probeVolume(PA, PZ)
      PA_PB = np.linalg.norm(PA - boneP) # length
      Length=(PA_PB//5-2)*5 # The screws are rounded
      Dim = Helper.estimateDim(PA, PZ)
      Helper.p2pexLine(boneP, PA, Length-PA_PB, Dim,"w_{0}_D:{1}_L".format(i,Dim), "blue")
    return Data

  @staticmethod
  def estimateDim(Pz, Pa, volumeName="baselineROI", minThread=150):
    volume_node = slicer.util.getNode(volumeName)
    voxels = slicer.util.arrayFromVolume(volume_node)
    VVList = []
    seg = 12
    for ii in range(20):
      i = 2 + ii * .5
      cylName = "Cyl{}".format(str(i))
      cyl = Helper.p2pCyl(Pa, Pz, i, cylName, 1 - np.linalg.norm(Pz - Pa), Seg=seg)
      pzP = Helper.Pcoord(cylName)[2]
      Helper.delNode(cylName)
      for j in range(seg):
        P = pzP[j * 2]
        volumeRasToIjk = vtk.vtkMatrix4x4()
        volume_node.GetRASToIJKMatrix(volumeRasToIjk)
        point_Ijk = [0, 0, 0, 1]
        volumeRasToIjk.MultiplyPoint(np.append(P, 1.0), point_Ijk)
        point_Ijk = [int(round(c)) for c in point_Ijk[0:3]]
        voxelValue = voxels[point_Ijk[2], point_Ijk[1], point_Ijk[0]]
        #       print(voxelValue)
        # if voxelValue<150:
        #   AddPoint(P)
        if j == 0:
          VVlist = np.array([voxelValue])
        else:
          VVlist = np.append(VVlist, voxelValue)
      VVList.append(VVlist)
    arrayV = np.array(VVList).mean(0)

    return np.argmax(arrayV) * .5

  @staticmethod
  def Screw(No, Pz, sDim=0, manulYN = False):
    """Adjust the angle diameter and length of the screw"""
    lineNode = "w_{}*".format(No)
    lineN = Helper.Psline(lineNode)
    PB0=lineN[0]
    # Helper.addFid(PB0,lableName="PB00")
    Pa = lineN[1]
    # Dim = Helper.estimateDim(Pz, Pa)
    # Lscrew = lineN[2]
    if manulYN is False:
      PB = PB0
      PT = Pa
      Helper.delNode(lineNode)
      B_T = np.linalg.norm(PB - PT)
      Length = 5 * (B_T// 5) - B_T
      if sDim != 0:
        screwDim = sDim
      else:
        screwDim = np.around(lineN[3], 1)
      Helper.p2pexLine(PB,PT,Length, screwDim,"w_{}_D:{}_L".format(No,screwDim),"red")
    else:
      PT = Pa
      # Helper.addFid(PB0, lableName="PB0")
      PB = Helper.probeVolume(PT,PB0)
      # Helper.addFid(PB)
      # logging.debug("PB:{}".format(PB))
      # logging.debug("PT:{}".format(PT))
      B_T = np.linalg.norm(PB - PT)
      Length =  5*(B_T//5)-B_T
      PB_Pz = np.linalg.norm(PT - PB) * (Pz[1] - PB[1]) / (PT[1] - PB[1])
      PZ = Helper.p2pexLine(PB, PT, 5 + PB_Pz - np.linalg.norm(PT - PB))
      screwDim = Helper.estimateDim(PT, PZ)
      Helper.delNode(lineNode)
      Helper.p2pexLine(PB,PT,Length, screwDim,"w_{}_D:{}_L".format(No,screwDim),"red")
    return int(Length+B_T), screwDim,PB, PT

  @staticmethod
  def screwAngle(No,Pz):
    """Screw angle"""
    lineNode = "w_{}*".format(No)
    lineN = Helper.Psline(lineNode)
    PB0 = lineN[0]
    Pa = lineN[1]
    Lscrew = lineN[2]
    x = [Pa[0], Pz[1], Pz[2]]
    xy = [Pa[0], Pa[1], Pz[2]]
    y = [Pz[0], Pa[1], Pz[2]]
    yz = [Pz[0], Pa[1], Pa[2]]
    ''' 
      1. SPA: x_o_xy_Angle((PA[0],PZ[1],PZ[2]),PZ,(PA[0],PA[1],PZ[2]))
      2. TPA: y_o_yz_Angle((PZ[0],PA[1],PZ[2]),PZ,(PZ[0],PA)[1],PA[2]))    
      3. xyy: x*tan(SPA+3*sn)
      4. yzz: y*tan(TPA+3*tn)
    '''

    SPA = Helper.p3Angle(x, Pz, xy)  # Coronary Angle (PSA)
    # logging.debug("SPA:{}".format(SPA))
    TPA = Helper.p3Angle(y, Pz, yz)  # Syryatic angle (PTA)
    # logging.debug("TPA:{}".format(TPA))
    return np.around(SPA), np.around(TPA)
