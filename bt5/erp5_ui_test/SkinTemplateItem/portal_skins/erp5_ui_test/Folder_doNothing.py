from Products.ERP5Type.Log import log

log("Folder method received dialog_id, form_id, uids and {!s}".format(kwargs.keys()))

if kwargs.get('has_changed', None) is None:
  message = "First submission."
else:
  if kwargs['has_changed']:
    message = "Data has changed."
  else:
    message = "Data the same."

if kwargs.get("update_method", ""):
  return context.Base_renderForm(dialog_id, message="Updated. " + message)

if _my_confirmation == 0:
  # Here is an example of unfriendly confirmation Script which takes
  # whole keep_item for itself!
  # It should take keep_items from parameters, update it and pass it
  # along. But no programmer will ever comply with that so we are ready!
  return context.Base_renderForm(dialog_id,
                                 message="Submit again to confirm. " + message,
                                 level='warning',
                                 keep_items={'_my_confirmation': 1})

return context.Base_redirect(form_id, keep_items={"portal_status_message": message})
