from __main__ import qt, ctk, vtk, slicer

from .PedicleScrewSimulatorStep import *
from .Helper import *

class EndStep(PedicleScrewSimulatorStep):
    
    def __init__( self, stepid ):
      self.initialize( stepid )
      self.setName( 'End' )
      self.setDescription( 'The End' )

      self.__parent = super( EndStep, self )
    
    def killButton(self):
      # hide useless button
      bl = slicer.util.findChildren(text='End')
      if len(bl):
        bl[0].hide()

    def createUserInterface( self ):
      '''
      '''
      self.__layout = self.__parent.createUserInterface()  
  
      # self.updateWidgetFromParameters(self.parameterNode())
      qt.QTimer.singleShot(0, self.killButton)
    
    def validate( self, desiredBranchId ):
      '''
      '''
      self.__parent.validate( desiredBranchId )
      self.__parent.validationSucceeded(desiredBranchId)
      
    def onEntry(self, comingFrom, transitionType):

      super(EndStep, self).onEntry(comingFrom, transitionType)

      
      qt.QTimer.singleShot(0, self.killButton)
      
    def onExit(self, goingTo, transitionType):
      #self.doStepProcessing()
    
      # extra error checking, in case the user manages to click ReportROI button
      #if goingTo.id() != 'DefineROI':
      #  return

      super(EndStep, self).onExit(goingTo, transitionType)
      
    def doStepProcessing(self):
        logging.debug('Done')