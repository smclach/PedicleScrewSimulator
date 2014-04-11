from __main__ import qt, ctk

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
    print "-> onEntry - current [%s] - comingFrom [%s]" % ( self.id(), comingFromId )
    super( PedicleScrewSimulatorStep, self ).onEntry( comingFrom, transitionType )

  def onExit( self, goingTo, transitionType ):
    goingToId = "None"

    if goingTo: goingToId = goingTo.id()
    
    print "-> onExit - current [%s] - goingTo [%s]" % ( self.id(), goingToId )
    super( PedicleScrewSimulatorStep, self ).onExit( goingTo, transitionType )

  def validate( self, desiredBranchId ):
    return
    print "-> validate %s" % self.id()

  def validationSucceeded( self, desiredBranchId ):
    '''
    '''
    super( PedicleScrewSimulatorStep, self ).validate( True, desiredBranchId )

  def validationFailed( self, desiredBranchId, messageTitle='Error', messageText='There was an unknown error. See the console output for more details!' ):
    '''
    '''
    messageBox = qt.QMessageBox.warning( self, messageTitle, messageText )
    super( PedicleScrewSimulatorStep, self ).validate( False, desiredBranchId )

