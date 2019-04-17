class Delete {
  constructor() {
    this.last = "";
  }

  askEmptyWhere() {
    let mes = [
      "Warning!",
      "Your 'Where' statement is empty!",
      "It will delete all entrys,",
      "if not limited by 'limit' or 'offset'",
      "Continue?"
    ]
    return confirm( mes.join("\n") );
  }

  start() {
    let request = {};

    request["of"] = _("[modal=delete] [name=of]").value();

    if (isEmpty(request['of'])) {
      _("[modal=delete] [name=of]").addClass("need-correction"); return;
    }

    request["where"] = _("[modal=delete] [name=where]").value();
    request["limit"] = _("[modal=delete] [name=limit]").value();
    request["offset"] = _("[modal=delete] [name=offset]").value();

    return this.execute(request);
  }

  execute(request) {
    if (request == null) { request = {}; }
    let r = {
      "action": "delete",
      "token": _('#db_token').value(),
      "of": request['of']
    };
    if ( !isEmpty(request['limit']) ) { r['limit'] = request['limit']; }
    if ( !isEmpty(request['offset']) ) { r['offset'] = request['offset']; }
    if ( !isEmpty(request['where']) ) { r['where'] = request['where']; }
    else {
      if ( !this.askEmptyWhere() ) {return _("[modal=delete] [name=where]").addClass("need-correction");}
    }

    this.last = request['of'];

    _.post("/", JSON.stringify(r))
    .done(function (data) {
      Display.closeModal();
      Display.message( {content:"Successfull deleted "+data.hits+" entry(s) of "+request['of'], color:Display.color_success} );
    })
    .fail(function (data) {
      if (data.status == "error") {
        if (data.msg == "unauthorised") {
          return Display.message( {content:"Unauthorised, please check token", color:Display.color_warn} );
        }
        return Display.message( {content:data.msg, color:Display.color_fail} );
      }
      else {
        return Display.message( {content:"Unknown Server Error", color:Display.color_fail} );
      }
    })
  }
}
Delete = new Delete();
