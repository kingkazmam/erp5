/*jslint indent: 2, nomen: true */
/*global window, rJS, jIO, document*/
(function (window, rJS, jIO, document, URL) {
  "use strict";

  rJS(window)
    .declareService(function () {
      var storage = jIO.createJIO({
        type: "indexeddb",
        database: "officejs-erp5"
      }),
        gadget = this;
      return storage.put('bad_document', {
        'filename': 'test.xlsx',
        'title': 'Bad Document',
        'portal_type': 'Spreadsheet',
        'mime_type': 'xlsx',
        'modification_date': 'Fri, 17 Aug 2018 11:21:22 +0000',
        'content_type': "application/x-asc-spreadsheet"
      })
      .push(function (id) {
        return jIO.util.ajax({
          type: "GET",
          url: new URL('./test_ooo_spreadsheet.xlsx', window.location.href),
          dataType: "blob"
        })
          .then(function (res) {
            return storage.putAttachment(id, 'data', res.target.response);
          });
      })
      .push(function () {
        return storage.put('CloudoooConversion/bad_document/xlsy', {
          'from': "xlsx",
          'id': 'bad_document',
          'modification_date': "Fri, 17 Aug 2018 11:21:22 +0000",
          'name': "data",
          'status': "convert",
          to: "xlsy"
        });
      })
      .push(function () {
        var div = document.createElement('div');
        div.textContent = 'Document Created';
        gadget.element.appendChild(div);
      });
    });
}(window, rJS, jIO, document, URL));
