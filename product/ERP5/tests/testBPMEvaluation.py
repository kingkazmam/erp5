# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
"""
This is BPM Evaluation Test class using erp5_bpm development Business Template

Generally it tries to use two Business Processes - one with sequence very
similar to normal ERP5 - TestBPMEvaluationDefaultProcessMixin, second one
inverted - TestBPMEvaluationDifferentProcessMixin.

It uses only Sale path to demonstrate BPM.

It is advised to *NOT* remove erp5_administration.

TODOs:
  * avoid duplication of code when possible
  * implement tests wisely, to support at least both BPM cases
"""
import unittest

from Products.ERP5.tests.testBPMCore import TestBPMMixin
from DateTime import DateTime

class TestBPMEvaluationMixin(TestBPMMixin):
  node_portal_type = 'Organisation'
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  packing_list_portal_type = 'Sale Packing List'
  packing_list_line_portal_type = 'Sale Packing List Line'
  trade_condition_portal_type = 'Sale Trade Condition'
  product_portal_type = 'Product'
  order_start_date = DateTime()
  order_stop_date = order_start_date + 10

  def getBusinessTemplateList(self):
    return TestBPMMixin.getBusinessTemplateList(self) + ('erp5_bpm',
        'erp5_administration')

  def afterSetUp(self):
    TestBPMMixin.afterSetUp(self)
    self._createNodes()
    self._createBusinessProcess()
    self._createTradeCondition()
    self._createOrder()
    self.stepTic()

  def _createDocument(self, portal_type, **kw):
    module = self.portal.getDefaultModule(portal_type=portal_type)
    return module.newContent(portal_type=portal_type, **kw)

  def _createProduct(self, **kw):
    return self._createDocument(self.product_portal_type, **kw)

  def _createNode(self, **kw):
    return self._createDocument(self.node_portal_type, **kw)

  def _createTradeCondition(self, **kw):
    self.trade_condition = self._createDocument(
        self.trade_condition_portal_type,
        specialise_value=self.business_process, **kw)

  def _createOrderLine(self, **kw):
    return self.order.newContent(portal_type=self.order_line_portal_type, **kw)

  def _createNodes(self):
    self.source, self.source_section = self._createNode(), self._createNode()
    self.destination, self.destination_section = self._createNode() \
        , self._createNode()

  def _createOrder(self):
    self.order = self._createDocument(self.order_portal_type,
        source_value = self.source,
        source_section_value = self.source_section,
        destination_value = self.destination,
        destination_section_value = self.destination_section,
        start_date = self.order_start_date,
        stop_date = self.order_stop_date,
        specialise_value = self.trade_condition)

  def _checkBPMSimulation(self, delivery, root_applied_rule_portal_type):
    # TODO:
    #  - gather errors into one list
    bpm_root_rule = delivery.getCausalityRelatedValue(
        portal_type='Applied Rule')
    self.assertEqual(bpm_root_rule.getSpecialiseValue().getPortalType(),
        root_applied_rule_portal_type)
    root_simulation_movement_list = bpm_root_rule.contentValues()
    self.assertEqual(len(delivery.getMovementList()),
      len(root_simulation_movement_list))
    for root_simulation_movement in root_simulation_movement_list:
      self.assertEqual(root_simulation_movement.getPortalType(),
          'Simulation Movement')
      movement = root_simulation_movement.getOrderValue()
      property_problem_list = []
      for property in 'resource', 'price', 'quantity', 'start_date', \
        'stop_date', 'source', 'destination', 'source_section', \
        'destination_section':
        if movement.getProperty(property) != root_simulation_movement \
            .getProperty(property):
          property_problem_list.append('property %s movement %s '
              'simulation %s' % (property, movement.getProperty(property),
                root_simulation_movement.getProperty(property)))
      if len(property_problem_list) > 0:
        self.fail('\n'.join(property_problem_list))
      self.assertEquals(len(root_simulation_movement.contentValues()), 1)
      for bpm_invoicing_rule in root_simulation_movement.contentValues():
        self.assertEqual(bpm_invoicing_rule.getPortalType(), 'Applied Rule')
        self.assertEqual(bpm_invoicing_rule.getSpecialiseValue() \
            .getPortalType(), 'BPM Invoicing Rule')
        self.assertEquals(len(bpm_invoicing_rule.contentValues()), 1)
        for invoicing_simulation_movement in bpm_invoicing_rule \
            .contentValues():
          self.assertEqual(invoicing_simulation_movement.getPortalType(),
              'Simulation Movement')
          self.assertEqual(invoicing_simulation_movement.getCausalityValue(),
              self.invoice_path)
          self.assertEquals(len(invoicing_simulation_movement.contentValues()), 1)
          for trade_model_rule in invoicing_simulation_movement \
              .contentValues():
            self.assertEqual(trade_model_rule.getPortalType(), 'Applied Rule')
            self.assertEqual(trade_model_rule.getSpecialiseValue() \
                .getPortalType(), 'Trade Model Rule')
            self.assertSameSet(trade_model_rule.contentValues(
              portal_type='Simulation Movement'), [])

  def _checkOrderBPMSimulation(self):
    """Checks BPM related simumation.
    
    Note: Simulation tree is the same, it is totally independent from
    BPM sequence"""
    self._checkBPMSimulation(self.order, 'BPM Order Rule')

class TestBPMEvaluationDefaultProcessMixin:
  def _createBusinessProcess(self):
    self.business_process = self.createBusinessProcess()
    ordered = self.createBusinessState(self.business_process)
    delivered = self.createBusinessState(self.business_process)
    invoiced = self.createBusinessState(self.business_process)
    accounted = self.createBusinessState(self.business_process)
    paid = self.createBusinessState(self.business_process)

    self.delivery_path = self.createBusinessPath(self.business_process,
        predecessor_value = ordered, successor_value = delivered,
        trade_phase = 'default/delivery',
        deliverable = 1,
        completed_state_list = ['delivered'],
        frozen_state_list = ['stopped', 'delivered'])

    self.invoice_path = self.createBusinessPath(self.business_process,
        predecessor_value = delivered, successor_value = invoiced,
        completed_state_list = ['delivered'],
        frozen_state_list = ['stopped', 'delivered'],
        trade_phase='default/invoicing')

    self.account_path = self.createBusinessPath(self.business_process,
        predecessor_value = invoiced, successor_value = accounted,
        completed_state_list = ['delivered'],
        frozen_state_list = ['stopped', 'delivered'],
        trade_phase='default/accounting')

    self.pay_path = self.createBusinessPath(self.business_process,
        predecessor_value = invoiced, successor_value = accounted,
        completed_state_list = ['delivered'],
        frozen_state_list = ['stopped', 'delivered'],
        trade_phase='default/payment')

    self.stepTic()

class TestBPMEvaluationDifferentProcessMixin:
  def _createBusinessProcess(self):
    self.business_process = self.createBusinessProcess()
    ordered = self.createBusinessState(self.business_process)
    delivered = self.createBusinessState(self.business_process)
    invoiced = self.createBusinessState(self.business_process)
    accounted = self.createBusinessState(self.business_process)
    paid = self.createBusinessState(self.business_process)

    self.invoice_path = self.createBusinessPath(self.business_process,
        predecessor_value = ordered, successor_value = invoiced,
        completed_state_list = ['delivered'],
        frozen_state_list = ['stopped', 'delivered'],
        trade_phase='default/invoicing')

    self.account_path = self.createBusinessPath(self.business_process,
        predecessor_value = invoiced, successor_value = accounted,
        completed_state_list = ['delivered'],
        frozen_state_list = ['stopped', 'delivered'],
        trade_phase='default/accounting')

    self.pay_path = self.createBusinessPath(self.business_process,
        predecessor_value = invoiced, successor_value = accounted,
        completed_state_list = ['delivered'],
        frozen_state_list = ['stopped', 'delivered'],
        trade_phase='default/payment')

    self.delivery_path = self.createBusinessPath(self.business_process,
        predecessor_value = accounted, successor_value = delivered,
        trade_phase = 'default/delivery',
        deliverable = 1,
        completed_state_list = ['delivered'],
        frozen_state_list = ['stopped', 'delivered'])

    self.stepTic()

class TestOrder(TestBPMEvaluationMixin):
  """Evaluation of BPM Sale Order system"""

  def test_planning(self):
    self.order_line = self._createOrderLine(resource_value = self._createProduct(),
        quantity = 10, price = 5)
    self.stepTic()

    self.order.plan()
    self.stepTic()
    self._checkOrderBPMSimulation()

  def test_planning_line_edit(self):
    self.test_planning()
    self.order_line.edit(quantity = 8, price = 6)
    self.stepTic()
    self._checkOrderBPMSimulation()

  def test_planning_line_edit_add(self):
    self.test_planning_line_edit()
    self.order_line_2 = self._createOrderLine(
        resource_value = self._createProduct(), quantity = 4, price = 2)
    self.stepTic()
    self._checkOrderBPMSimulation()

  def test_planning_line_edit_add_many_transactions(self):
    self.test_planning_line_edit()
    self.order_line_9 = self._createOrderLine()
    self.stepTic()
    self._checkOrderBPMSimulation()

    self.order_line_9.edit(resource_value = self._createProduct())
    self.stepTic()
    self._checkOrderBPMSimulation()

    self.order_line_9.edit(quantity = 1)
    self.stepTic()
    self._checkOrderBPMSimulation()

    self.order_line_9.edit(price = 33)
    self.stepTic()
    self._checkOrderBPMSimulation()

    self.order_line_9.edit(resource_value = self._createProduct())
    self.stepTic()
    self._checkOrderBPMSimulation()

  def test_planning_line_edit_add_same_resource(self):
    self.test_planning_line_edit()
    resource = self.order_line.getResourceValue()
    self.order_line_10 = self._createOrderLine(resource_value = resource,
        quantity = 9, price = 2)
    self.stepTic()
    self._checkOrderBPMSimulation()

  def test_planning_line_edit_add_same_resource_than_order(self):
    self.test_planning_line_edit_add_same_resource()
    self.order.order()
    self.stepTic()
    self._checkOrderBPMSimulation()

class TestPackingList(TestBPMEvaluationMixin):
  """Evaluation of BPM Order to Packing List"""
  packing_list_start_date = TestBPMEvaluationMixin.order_start_date
  packing_list_stop_date = TestBPMEvaluationMixin.order_stop_date

  def _createPackingListLine(self, **kw):
    return self.packing_list.newContent(portal_type=self.packing_list_line_portal_type, **kw)

  def _createPackingList(self):
    self.packing_list = self._createDocument(self.packing_list_portal_type,
        source_value = self.source,
        source_section_value = self.source_section,
        destination_value = self.destination,
        destination_section_value = self.destination_section,
        start_date = self.packing_list_start_date,
        stop_date = self.packing_list_stop_date,
        specialise_value = self.trade_condition)

  def _checkPackingListBPMSimulation(self):
    """Checks BPM related simumation.
    
    Note: Simulation tree is the same, it is totally independent from
    BPM sequence"""
    self._checkBPMSimulation(self.packing_list, 'BPM Delivery Rule')

  def test_confirming_packing_list_only(self):
    self._createPackingList()
    self.packing_list_line = self._createPackingListLine(resource_value = self._createProduct(),
        quantity = 10, price = 5)
    self.stepTic()

    self.packing_list.confirm()
    self.stepTic()
    self._checkPackingListBPMSimulation()

class TestInvoice(TestBPMEvaluationMixin):
  """Evaluation of BPM Order through Packing List to Invoice Transaction"""
  pass

class TestOrderDefaultProcess(TestOrder, TestBPMEvaluationDefaultProcessMixin):
  pass

class TestPackingListDefaultProcess(TestPackingList, TestBPMEvaluationDefaultProcessMixin):
  pass

class TestInvoiceDefaultProcess(TestInvoice, TestBPMEvaluationDefaultProcessMixin):
  pass

class TestOrderDifferentProcess(TestOrder, TestBPMEvaluationDifferentProcessMixin):
  pass

class TestPackingListDifferentProcess(TestPackingList, TestBPMEvaluationDifferentProcessMixin):
  pass

class TestInvoiceDifferentProcess(TestInvoice, TestBPMEvaluationDifferentProcessMixin):
  pass

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOrderDefaultProcess))
  suite.addTest(unittest.makeSuite(TestPackingListDefaultProcess))
  suite.addTest(unittest.makeSuite(TestInvoiceDefaultProcess))
  suite.addTest(unittest.makeSuite(TestOrderDifferentProcess))
  suite.addTest(unittest.makeSuite(TestPackingListDifferentProcess))
  suite.addTest(unittest.makeSuite(TestInvoiceDifferentProcess))
  return suite
