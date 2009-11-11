from zLOG import LOG, INFO
def dumpWorkflowChain(self):
  # This method outputs the workflow chain in the format that you can
  # easily get diff like the following:
  # ---
  # Account,account_workflow
  # Account,edit_workflow
  # ...
  # ---
  workflow_tool = self.getPortalObject().portal_workflow
  cbt = workflow_tool._chains_by_type
  ti = workflow_tool._listTypeInfo()
  types_info = []
  for t in ti:
    id = t.getId()
    title = t.Title()
    if title == id:
      title = None
    if cbt is not None and cbt.has_key(id):
      chain = sorted(cbt[id])
    else:
      chain = ['(Default)']
    types_info.append({'id': id,
                       'title': title,
                       'chain': chain})
  output = []
  for i in sorted(types_info, key=lambda x:x['id']):
    for chain in i['chain']:
      output.append('%s,%s' % (i['id'], chain))
  return '\n'.join(output)

def checkFolderHandler(self, fixit=0, **kw):
  error_list = []
  try:
    is_btree = self.isBTree()
    is_hbtree = self.isHBTree()
  except AttributeError:
    return error_list
  message = '%s' % self.absolute_url_path()
  problem = False
  if not is_btree and not is_hbtree:
    problem = True
    message = '%s is NOT BTree NOR HBTree' % message
    if fixit:
      try:
        result = self._fixFolderHandler()
      except AttributeError:
        result = False
      if result:
        message = '%s fixed' % message
      else:
        message = '%s CANNOT FIX' % message
  if is_btree and is_hbtree:
    problem = True
    message = '%s is BTree and HBTree' % message
    if fixit:
      message = '%s CANNOT FIX' % message
  if problem:
    error_list.append(message)
    LOG('checkFolderHandler', INFO, message)
  return error_list


def MessageCatalog_getMessageDict(self):
  """
    Get Localizer's MessageCatalog instance messages.
  """
  d = {}
  for k,v in self._messages.iteritems():
    d[k] = v
  return d

def MessageCatalog_getNotTranslatedMessageDict(self):
  """
    Get Localizer's MessageCatalog instance messages that are NOT translated.
  """
  not_translated_message_dict = {}
  messages = MessageCatalog_getMessageDict(self)
  for k,v in messages.iteritems():
    if not len(v):
      not_translated_message_dict[k] = v
  return not_translated_message_dict

def MessageCatalog_deleteNotTranslatedMessageDict(self):
  """
    Delete from  Localizer's MessageCatalog instance messages that are NOT translated.
  """
  not_translated_message_dict = MessageCatalog_getNotTranslatedMessageDict(self)
  for k,v in not_translated_message_dict.iteritems():
    # delete message from dict
    del(self._messages[k])
  return len(not_translated_message_dict.keys())
