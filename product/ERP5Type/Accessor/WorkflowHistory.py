##############################################################################
#
# Copyright (c) 2018 Nexedi SARL and Contributors. All Rights Reserved.
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

from Products.ERP5Type.PsycoWrapper import psyco
from Base import Getter as BaseGetter
from Acquisition import aq_base

class Getter(BaseGetter):
    """
    Get a property from Workflow History. A default value can be
    provided if needed.
    """
    def __init__(self, id, workflow_id, transition_id, key):
      self._id = id
      self.__name__ = id
      self._workflow_id = workflow_id
      self._transition_id = transition_id
      self._key = key

    def __call__(self, instance, default=None):
      instance = aq_base(instance)
      try:
        workflow_history_dict_list = instance.workflow_history[self._workflow_id]
      except (AttributeError, KeyError):
        return default
      else:
        for workflow_history_dict in workflow_history_dict_list:
          if workflow_history_dict['action'] == self._transition_id:
            return workflow_history_dict.get(self._key, default)

    psyco.bind(__call__)
