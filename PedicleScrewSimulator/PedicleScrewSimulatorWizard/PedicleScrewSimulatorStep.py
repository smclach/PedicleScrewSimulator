import logging
from __main__ import qt, ctk, slicer

class PedicleScrewSimulatorStep( ctk.ctkWorkflowWidgetStep ) :

  def __init__( self, stepid ):
    self.initialize( stepid )

  def setParameterNode(self, parameterNode):
    '''
    Keep the pointer to the parameter node for each step
    '''
    self.__parameterNode = parameterNode

  def parameterNode(self):
    return self.__parameterNode
    
  def fiducialNode(self):
    fiducialNode = self.__parameterNode.GetNodeReference("LandmarksFiducial")
    if not fiducialNode:
      ml=slicer.modules.markups.logic()
      newLandmarksNodeID = ml.AddNewFiducialNode('T')
      self.__parameterNode.SetNodeReferenceID("LandmarksFiducial", newLandmarksNodeID)
      fiducialNode = slicer.mrmlScene.GetNodeByID(newLandmarksNodeID)
    return fiducialNode

  def getBoldFont( self ):
    '''
    '''
    boldFont = qt.QFont( "Sans Serif", 12, qt.QFont.Bold )
    return boldFont

  def createUserInterface( self ):
    self.__layout = qt.QFormLayout( self )
    self.__layout.setVerticalSpacing( 5 )

    # Add empty rows
    self.__layout.addRow( "", qt.QWidget() )
    self.__layout.addRow( "", qt.QWidget() )

    return self.__layout

  def onEntry( self, comingFrom, transitionType ):
    comingFromId = "None"
    if comingFrom: comingFromId = comingFrom.id()
    logging.debug("-> onEntry - current [%s] - comingFrom [%s]" % ( self.id(), comingFromId ))
    super( PedicleScrewSimulatorStep, self ).onEntry( comingFrom, transitionType )

  def onExit( self, goingTo, transitionType ):
    goingToId = "None"

    if goingTo: goingToId = goingTo.id()
    
    logging.debug("-> onExit - current [%s] - goingTo [%s]" % ( self.id(), goingToId ))
    super( PedicleScrewSimulatorStep, self ).onExit( goingTo, transitionType )

  def validate( self, desiredBranchId ):
    return
    logging.debug("-> validate %s" % self.id())

  def validationSucceeded( self, desiredBranchId ):
    '''
    '''
    super( PedicleScrewSimulatorStep, self ).validate( True, desiredBranchId )

  def validationFailed( self, desiredBranchId, messageTitle='Error', messageText='There was an unknown error. See the console output for more details!' ):
    '''
    '''
    messageBox = qt.QMessageBox.warning( self, messageTitle, messageText )
    super( PedicleScrewSimulatorStep, self ).validate( False, desiredBranchId )

