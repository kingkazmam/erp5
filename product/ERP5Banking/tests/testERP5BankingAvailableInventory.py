##############################################################################
#
# Copyright (c) 2005-2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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


# import requested python module
import os
from zLOG import LOG
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.DCWorkflow.DCWorkflow import Unauthorized, ValidationFailed
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from Products.ERP5Banking.tests.TestERP5BankingMixin import TestERP5BankingMixin
from Products.ERP5Banking.tests.testERP5BankingCheckPayment \
      import TestERP5BankingCheckPaymentMixin
from Products.ERP5Banking.tests.testERP5BankingMoneyDeposit \
      import TestERP5BankingMoneyDepositMixin
from Products.ERP5Form.Document.Preference import Priority

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE']     = os.path.join(os.getcwd(), 'zLOG.log')
# Define the level of log we want, here is all
os.environ['EVENT_LOG_SEVERITY'] = '-300'

# Define how to launch the script if we don't use runUnitTest script
if __name__ == '__main__':
  execfile(os.path.join(sys.path[0], 'framework.py'))


class TestERP5BankingAvailableInventory(TestERP5BankingCheckPaymentMixin,
                                        TestERP5BankingMoneyDepositMixin,
                                        TestERP5BankingMixin,
                                        ERP5TypeTestCase):
  """
  Unit test class in order to make sure that it is not possible
  to debit two times the same account if the amount on the account is
  too short.

  We must make sure that future incoming movements will not be
  taken into account

  We will by the way check the way counter dates are working.

  Also, we must make sure it is not possible to deliver two check
  payments by the same time (due to tag on counter)
  """

  login = PortalTestCase.login

  # pseudo constants
  RUN_ALL_TEST = 1 # we want to run all test
  QUIET = 0 # we don't want the test to be quiet


  def getTitle(self):
    """
      Return the title of the test
    """
    return "ERP5BankingAvailabeInventory"

  def afterSetUp(self):
    """
      Method called before the launch of the test to initialize some data
    """
    TestERP5BankingCheckPaymentMixin.afterSetUp(self)
    self.money_deposit_counter = self.paris.surface.banque_interne
    self.money_deposit_counter_vault = self.paris.surface.banque_interne.guichet_1.encaisse_des_billets_et_monnaies.entrante
    
    self.createCashInventory(source=None, 
                             destination=self.money_deposit_counter_vault, 
                             currency=self.currency_1,
                             line_list=self.line_list)

    self.openCounter(site=self.money_deposit_counter_vault,id='counter_2')

    # Set some variables : 
    self.money_deposit_module = self.getMoneyDepositModule()

    # Add a preference
    preference = self.getPortal().portal_preferences.newContent()
    preference.setPreferredUsualCashMaxRenderingPrice(1000000)
    preference.setPriority(Priority.USER)
    preference.enable()

  def stepCheckOpenCounterDateTwiceFail(self, sequence=None, sequence_list=None, **kwd):
    """
    Make sure we can not open the counter date twice
    """
    self.openCounterDate(site=self.paris,id='counter_date_2',open=0)
    # open counter date and counter
    self.assertRaises(ValidationFailed,
                     self.workflow_tool.doActionFor,
                     self.counter_date_2,'open_action',
                     wf_id='counter_date_workflow')
    # get workflow history
    workflow_history = self.workflow_tool.getInfoFor(
           ob=self.counter_date_2, name='history', wf_id='counter_date_workflow')
    # check its len is 2
    # check we get an "Insufficient balance" message in the workflow history because of the invalid line
    msg = workflow_history[-1]['error_message']
    self.assertTrue('there is already a counter date opened' in "%s" %(msg,))

  def stepCheckRemainingOperations(self, 
               sequence=None, sequence_list=None, **kwd):
    """
    Make sure we can not close the counter date 
    when there is still some operations remaining
    """
    site = self.counter_date_2.getSiteValue()
    self.assertRaises(ValidationFailed,
                     self.getPortal().Baobab_checkRemainingOperation,
                     site=site)

  def stepCheckNoRemainingOperations(self, 
               sequence=None, sequence_list=None, **kwd):
    """
    Make sure we can not close the counter date 
    when there is still some operations remaining
    """
    site = self.counter_date_1.getSiteValue()
    self.getPortal().Baobab_checkRemainingOperation(site=site)

  def stepCheckBadStockBeforeClosingDate(self, 
               sequence=None, sequence_list=None, **kwd):
    """
    Make sure we can not close the counter date 
    when there is still some operations remaining
    """
    site = self.counter_date_1.getSiteValue()
    self.assertRaises(ValidationFailed,
                     self.getPortal().Baobab_checkStockBeforeClosingDate,
                     site=site)

  def stepResetInventory(self, 
               sequence=None, sequence_list=None, **kwd):
    """
    Make sure we can not close the counter date 
    when there is still some operations remaining
    """
    bi_counter = self.paris.surface.banque_interne
    bi_counter_vault = bi_counter.guichet_1.encaisse_des_billets_et_monnaies.entrante
    line_list = self.line_list
    self.resetInventory(source=None, destination=bi_counter_vault, currency=self.currency_1,
                             line_list=line_list,extra_id='_reset_in')
    bi_counter_vault = bi_counter.guichet_1.encaisse_des_billets_et_monnaies.sortante
    self.resetInventory(source=None, destination=bi_counter_vault, currency=self.currency_1,
                             line_list=line_list,extra_id='_reset_out')

  def stepCheckRightStockBeforeClosingDate(self, 
               sequence=None, sequence_list=None, **kwd):
    """
    Make sure we can not close the counter date 
    when there is still some operations remaining
    """
    site = self.counter_date_2.getSiteValue()
    self.getPortal().Baobab_checkStockBeforeClosingDate(site=site)

  def stepCheckAccountInitialInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check the inventory of the bank account
    self.assertEqual(self.currency_1.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.currency_1.getAvailableInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.currency_1.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)

  def stepCheckAccountConfirmedInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check the final inventory of the bank account
    self.assertEqual(self.currency_1.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.currency_1.getAvailableInventory(payment=self.bank_account_1.getRelativeUrl()), 10000)
    self.assertEqual(self.currency_1.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)

  def stepCheckAccountFinalInventory(self, sequence=None, sequence_list=None, **kwd):
    """
    Check the initial inventory before any operations
    """
    self.simulation_tool = self.getSimulationTool()
    # check the final inventory of the bank account
    self.assertEqual(self.currency_1.getCurrentInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.currency_1.getAvailableInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)
    self.assertEqual(self.currency_1.getFutureInventory(payment=self.bank_account_1.getRelativeUrl()), 30000)


  def test_01_ERP5BankingAvailabeInventory(self, quiet=QUIET, run=RUN_ALL_TEST):
    """
    Define the sequence of step that will be play
    """
    if not run: return
    sequence_list = SequenceList()
    # define the sequence
    sequence_string = 'Tic CheckObjects Tic CheckAccountInitialInventory ' \
                      'CheckOpenCounterDateTwiceFail Tic ' \
                      'CheckNoRemainingOperations Tic ' \
                      'CreateCheckPayment Tic ' \
                      'CheckConsistency Tic ' \
                      'CreateMoneyDeposit ' \
                      'ValidateAnotherCheckPaymentWorks Tic ' \
                      'SendToCounter ' \
                      'MoneyDepositSendToCounter ' \
                      'stepValidateAnotherCheckPaymentFails Tic ' \
                      'CheckAccountConfirmedInventory ' \
                      'stepValidateAnotherCheckPaymentFailsAgain Tic ' \
                      'CheckRemainingOperations Tic ' \
                      'InputCashDetails Tic ' \
                      'MoneyDepositInputCashDetails Tic ' \
                      'DeliverMoneyDeposit Tic ' \
                      'ValidateAnotherCheckPaymentWorksAgain Tic ' \
                      'Pay PayAnotherCheckPaymentFails ' \
                      'Tic ' \
                      'CheckAccountFinalInventory ' \
                      'CheckBadStockBeforeClosingDate ' \
                      'ResetInventory Tic ' \
                      'CheckRightStockBeforeClosingDate '
    sequence_list.addSequenceString(sequence_string)
    # play the sequence
    sequence_list.play(self)

# define how we launch the unit test
if __name__ == '__main__':
  framework()
else:
  import unittest
  def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestERP5BankingAvailableInventory))
    return suite
