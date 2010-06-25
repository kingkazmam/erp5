# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import zope.interface
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.mixin.solver import SolverMixin
from Products.ERP5.mixin.configurable import ConfigurableMixin

class AdoptSolver(SolverMixin, ConfigurableMixin, XMLObject):
  """
  """
  meta_type = 'ERP5 Adopt Solver'
  portal_type = 'Adopt Solver'
  add_permission = Permissions.AddPortalContent
  isIndexable = 0 # We do not want to fill the catalog with objects on which we need no reporting

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.TargetSolver
                    )

  # Declarative interfaces
  zope.interface.implements(interfaces.ISolver,
                            interfaces.IConfigurable,
                           )

  # ISolver Implementation
  def solve(self):
    """
    Adopt new property to movements or deliveries.
    """
    configuration_dict = self.getConfigurationPropertyDict()
    portal_type = self.getPortalObject().portal_types.getTypeInfo(self)
    solved_property_list = configuration_dict.get('tested_property_list',
                                                  portal_type.getTestedPropertyList())
    delivery_dict = {}
    for simulation_movement in self.getDeliveryValueList():
      delivery_dict.setdefault(simulation_movement.getDeliveryValue(),
                               []).append(simulation_movement)
    for movement, simulation_movement_list in delivery_dict.iteritems():
      for solved_property in solved_property_list:
        # XXX hardcoded
        if solved_property == 'quantity':
          total_quantity = sum(
            [x.getQuantity() for x in movement.getDeliveryRelatedValueList()])
          movement.setQuantity(total_quantity)
          for simulation_movement in simulation_movement_list:
            quantity = simulation_movement.getQuantity()
            delivery_ratio = quantity / total_quantity
            delivery_error = total_quantity * delivery_ratio - quantity
            simulation_movement.edit(delivery_ratio=delivery_ratio,
                                     delivery_error=delivery_error)
        else:
          # XXX TODO we need to support multiple values for categories or
          # list type property.
          simulation_movement = movement.getDeliveryRelatedValue()
          movement.setProperty(solved_property,
                               simulation_movement.getProperty(solved_property))
    # Finish solving
    self.succeed()
