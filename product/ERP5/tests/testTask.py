##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
#         Mikolaj Antoszkiewicz <mikolaj@erp5.pl> 
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
############################################################################## 

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.CMFCore.utils import getToolByName
from Testing import ZopeTestCase

class TestTaskMixin:

  default_quantity = 99.99999999
  default_price = 555.88888888
  organisation_portal_type = 'Organisation'
  resource_portal_type = 'Service'
  project_portal_type = 'Project'
  task_portal_type = 'Task'
  task_description = 'Task Description %s'
  task_line_portal_type = 'Task Line'
  task_report_portal_type = 'Task Report'
  task_report_line_portal_type = 'Task Report Line'
  datetime = DateTime()
  task_workflow_id='task_workflow'

  default_task_sequence = 'stepCreateOrganisation \
                       stepCreateOrganisation \
                       stepCreateResource \
                       stepCreateProject \
                       stepCreateSimpleTask \
                       stepFillTaskWithData \
                       stepConfirmTask \
                       stepTic \
                       stepSetTaskReport '

  default_task_sequence_two_lines = 'stepCreateOrganisation \
                       stepCreateOrganisation \
                       stepCreateResource \
                       stepCreateResource \
                       stepCreateProject \
                       stepCreateSimpleTask \
                       stepFillTaskWithData \
                       stepCreateTaskLine \
                       stepConfirmTask \
                       stepTic \
                       stepSetTaskReport '
                       
  default_task_report_sequence = 'stepCreateOrganisation \
                       stepCreateOrganisation \
                       stepCreateResource \
                       stepCreateSimpleTaskReport \
                       stepFillTaskReportWithData \
                       stepCreateTaskReportLine '

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_project',)

  def login(self, quiet=0, run=1):
    uf = self.getPortal().acl_users
    uf._doAddUser('dummy', '', 
                  ['Member', 'Auditor', 'Author', 'Assignee', 'Assignor'], [])
    user = uf.getUserById('dummy').__of__(uf)
    newSecurityManager(None, user)

  def stepTic(self,**kw):
    self.tic()

  def stepCreateResource(self,sequence=None, sequence_list=None, \
                                    **kw):
    """
      Create a resource_list with no variation
    """
    resource_list = sequence.get('resource_list', [])
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(
        portal_type=self.resource_portal_type,
        title = 'Resource%s' % len(resource_list),
    )
    resource_list.append(resource)
    sequence.edit(resource_list=resource_list)

  def stepCreateProject(self,sequence=None, sequence_list=None, \
                        **kw):
    """
    Create a project
    """
    portal = self.getPortal()
    module = portal.getDefaultModule(self.project_portal_type)
    obj = module.newContent(
        portal_type=self.project_portal_type,
        title = 'Project',
    )
    sequence.edit(project=obj)

  def stepCreateOrganisation(self, sequence=None, sequence_list=None, **kw):
    """
      Create a empty organisation
    """
    organisation_list = sequence.get('organisation_list', [])
    portal = self.getPortal()
    organisation_module = portal.getDefaultModule(
                                   portal_type=self.organisation_portal_type)
    organisation = organisation_module.newContent(
                        portal_type=self.organisation_portal_type,
                        title='Organization%s' % len(organisation_list),
    )
    organisation_list.append(organisation)
    sequence.edit(organisation_list=organisation_list)

  def stepCreateSimpleTask(self,sequence=None, sequence_list=None, **kw):
    """
      Create a task and fill it with dummy data.
    """
    portal = self.getPortal()
    task_module = portal.getDefaultModule(portal_type=self.task_portal_type)
    task = task_module.newContent(portal_type=self.task_portal_type)
    # Check if no task lines are created at the start
    self.assertEquals(len(task.contentValues()), 0)
    task.edit(
      title = "Task",
    )
    sequence.edit(task = task)

  def stepFillTaskWithData(self, sequence=None, sequence_list=None, **kw):
    """
      Fill created task with some necessary data.
    """
    task = sequence.get('task')
    project = sequence.get('project')
    resource = sequence.get('resource_list')[0]
    organisation_list = sequence.get('organisation_list')
    organisation1 = organisation_list[0]
    organisation2 = organisation_list[1]
    task.edit(source_value=organisation1,
              source_section_value=organisation1,
              destination_value=organisation1,
              destination_section_value=organisation2,
              source_project_value=project,
              description=self.task_description % task.getId(),
              task_line_resource_value = resource,
              task_line_quantity = self.default_quantity,
              task_line_price = self.default_price,
              start_date = self.datetime + 10,
              stop_date = self.datetime + 20,)
    sequence.edit( task = task)

  def stepCreateSimpleTaskReport(self,sequence=None, sequence_list=None, **kw):
    """
      Create a task report.
    """
    portal = self.getPortal()
    task_report_module = portal.getDefaultModule(
                                    portal_type=self.task_report_portal_type)
    task_report = task_report_module.newContent(
                                    portal_type=self.task_report_portal_type)
    # Check if no task lines are created at the start
    self.assertEquals(len(task_report.contentValues()), 0)
    task_report.edit(
      title = "Task Report",
    )
    sequence.edit(task_report = task_report)

  def stepFillTaskReportWithData(self, sequence=None, sequence_list=None, **kw):
    """
      Fill created task report with some necessary data.
    """
    task_report = sequence.get('task_report')
    organisation_list = sequence.get('organisation_list')
    organisation1 = organisation_list[0]
    organisation2 = organisation_list[1]
    task_report.edit(source_value=organisation1,
                 source_section_value=organisation1,
                 destination_value=organisation1,
                 destination_section_value=organisation2,
                 start_date = self.datetime + 10,
                 stop_date = self.datetime + 20,)
    sequence.edit( task_report = task_report)

  def stepCreateTaskReportLine(self, sequence=None, sequence_list=None, **kw):
    """
      Create task report line and fill with dummy data.
    """
    resource = sequence.get('resource_list')[0]
    portal = self.getPortal()
    task_report = sequence.get('task_report')
    task_report_line = task_report.newContent(
                             portal_type=self.task_report_line_portal_type)
    task_report_line.edit( title = 'New Task Report Line',
                    resource_value = resource,
                    quantity = self.default_quantity,
                    price = self.default_price)
    sequence.edit(task_report_line = task_report_line)

  def stepVerifyGeneratedByBuilderTaskReport(self, sequence=None,
                                                    sequence_list=None, **kw):
    """
    Verify that simulation generated report is correct.
    """
    task = sequence.get('task')
    task_report = sequence.get('task_report')
    self.assertEquals('confirmed', task_report.getSimulationState())
    self.assertEquals(task.getSource(), task_report.getSource())
    self.assertEquals(task.getSourceSection(), task_report.getSourceSection())
    self.assertEquals(task.getSourceProject(), task_report.getSourceProject())
    self.assertEquals(task.getDestination(), task_report.getDestination())
    self.assertEquals(task.getDestinationSection(),
                      task_report.getDestinationSection())
    self.assertEquals(task.getDestinationDecision(),
                      task_report.getDestinationDecision())
    self.assertEquals(task.getTitle(),
                      task_report.getTitle())
    self.assertEquals(task.getDescription(),
                      task_report.getDescription())
    self.assertEquals(task.getPredecessor(), task_report.getPredecessor())
    self.assertEquals(task.getDescription(), task_report.getDescription())
    self.assertEquals(len(task_report.contentValues()), 1)
    task_report_line = task_report.contentValues()[0]
    self.assertEquals(task.getTaskLineResource(), task_report_line.getResource())
    self.assertEquals(task.getTaskLineQuantity(), task_report_line.getQuantity())
    self.assertEquals(task.getTaskLinePrice(), task_report_line.getPrice())

  def stepCreateTaskLine(self, sequence=None, sequence_list=None, **kw):
    """
      Create task line and fill with dummy data.
    """
    organisation = sequence.get('organisation_list')[0]
    resource1 = sequence.get('resource_list')[1]
    portal = self.getPortal()
    task = sequence.get('task')
    task_line = task.newContent(
        portal_type=self.task_line_portal_type,
        title='New Task Line',
        source_value=organisation,
        destination_value=organisation,
        resource_value=resource1,
        quantity=self.default_quantity,
        price=self.default_price)
    sequence.edit(task_line=task_line)
  
  def stepVerifyGeneratedTaskReportLines(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Verify that simulation generated report is correct.
    """
    task = sequence.get('task')
    task_report = sequence.get('task_report') 
    task_content_list = task.contentValues()
    self.assertNotEquals(len(task_content_list), 0)
    self.assertEquals(len(task_report.contentValues()),
                      len(task_content_list))

    # Task report values not tested
    # XXX
    # Task line not precisely tested
    for task_line in task_content_list:
        task_report_resource_list = \
            [line.getResource() for line in task_report.contentValues()]
        task_report_quantity_list = \
            [line.getQuantity() for line in task_report.contentValues()]
        task_report_price_list = \
            [line.getPrice() for line in task_report.contentValues()]
        self.assertTrue(task_line.getResource() in task_report_resource_list)
        self.assertTrue(task_line.getQuantity() in task_report_quantity_list)
        self.assertTrue(task_line.getPrice() in task_report_price_list)

  def stepVerifyTaskReportCausalityState(self, sequence=None,
                                         sequence_list=None, **kw):
    """
      Verify that confirmed task report starts building and gets solved.
    """
    task_report = sequence.get('task_report')
    self.assertEqual(task_report.getCausalityState(), 'solved')

  def modifyState(self, object_name, transition_name, sequence=None,
                       sequence_list=None):
    object_value = sequence.get(object_name)
    workflow_method = getattr(object_value, transition_name)
    workflow_method()

  def stepConfirmTask(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task', 'confirm', sequence=sequence)
  
  def stepConfirmTaskReport(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task_report', 'confirm', sequence=sequence)
  
  def stepStartTaskReport(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task_report', 'start', sequence=sequence)

  def stepFinishTaskReport(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task_report', 'stop', sequence=sequence)

  def stepCloseTaskReport(self, sequence=None, sequence_list=None, **kw):
    self.modifyState('task_report', 'deliver', sequence=sequence)
  
  def stepSetTaskReport(self, sequence=None, sequence_list=None, **kw):
    """
      Set task report object in sequence.
    """
    task = sequence.get('task')
    task_report = task.getCausalityRelatedValueList(
                                                portal_type = 'Task Report')[0]
    sequence.edit( task_report = task_report)


class TestTask(TestTaskMixin, ERP5TypeTestCase):
  """
    Test task behaviour.
  """
  run_all_test = 1

  def getTitle(self):
    return "Task"

  def enableLightInstall(self):
    """
    You can override this.
    Return if we should do a light install (1) or not (0)
    """
    return 1

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def test_01_testTaskBasicUseCase(self, quiet=0, run=run_all_test):
    """
      Test creation of task and (automatic) task_report
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = self.default_task_sequence + '\
                       stepVerifyGeneratedByBuilderTaskReport \
                       stepStartTaskReport \
                       stepFinishTaskReport \
                       stepCloseTaskReport \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_testMultipleLineTaskBasicUseCase(self, quiet=0, run=run_all_test):
    """
      Test creation of task with multiple task lines \
      and (automatic) creation of task_report.
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = self.default_task_sequence_two_lines + '\
                       stepVerifyGeneratedTaskReportLines \
                       stepStartTaskReport \
                       stepFinishTaskReport \
                       stepCloseTaskReport \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_03_testTaskReportBasicUseCase(self, quiet=0, run=run_all_test):
    """
      Test creation of task report and task report lines. 
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = self.default_task_report_sequence + '\
                       stepConfirmTaskReport \
                       stepTic \
                       stepVerifyTaskReportCausalityState \
                       stepStartTaskReport \
                       stepFinishTaskReport \
                       stepCloseTaskReport \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTask))
  return suite
