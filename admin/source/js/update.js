class Update {
  constructor() {
    this.last = "";
  }

  setMethod(method) {
    _("[modal=update] button[method]").removeClass("selected");
    _("[modal=update] div[method]").hide();

    _("[modal=update] button[method="+method+"]").addClass("selected");
    _("[modal=update] div[method="+method+"]").show();

    _("[modal=update] data[method]").value(method);
  }

  modalAddField() {
    let n = Template.getKeyValueField();
    _('[modal=update] [update-fields]').append(n);
  }

  modalClearFields() {
    _('[modal=update] [update-fields]').html("");
  }

  start() {
    let m = _("[modal=update] data[method]").value();
    if (isEmpty(m)) { return _("[modal=update] data[method]").parent().addClass("need-correction"); }

    if (m == "string") { return this.startMethodString() }
    else if (m == "fields") { return this.startMethodFields() }
  }

  startMethodFields() {
    let request = {};

    request["of"] = _("[modal=update] [name=of]").value();
    if (isEmpty(request["of"])) { return _("[modal='update'] [name=of]").addClass('need-correction'); }
    request["where"] = _("[modal=update] [name=where]").value();
    request["limit"] = _("[modal=update] [name=limit]").value();
    request["offset"] = _("[modal=update] [name=offset]").value();

    let content = {};
    for (let field of _("[modal=update] [update-fields] .key-value-field").result) {
      field = _(field);
      let key = field.find("[placeholder=Key]").value();
      let value = field.find("[placeholder=Value]").value();
      let type = field.find("select").value();

      if (isEmpty(key)) {
        field.find("[placeholder=Key]").addClass('need-correction');
        return Display.message({content:"no key can be empty", color:Display.color_warn});
      }

      try { content[key] = getValueInRightType(value, type); }
      catch (e) {
        Display.message( {content:"invalid json object", color:Display.color_warn} );
        return field.find("[placeholder=Value]").addClass("need-correction");
      }
    }

    if (isEmpty(content)) { return _("[modal=update] [method=fields] .green").addClass('need-correction'); }

    request["content"] = content;
    return this.execute(request);
  }

  startMethodString() {
    let request = {};

    request["of"] = _("[modal='update'] [name=of]").value();
    if (isEmpty(request["of"])) { return _("[modal='update'] [name=of]").addClass('need-correction'); }
    request["where"] = _("[modal='update'] [name=where]").value();
    request["limit"] = _("[modal='update'] [name=limit]").value();
    request["offset"] = _("[modal='update'] [name=offset]").value();
    request["content"] = _("[modal='update'] [name=content]").value();

    return this.execute(request);
  }

  execute(request) {
    if (request == null) { request = {}; }
    let r = {
      "action": "update",
      "token": _('#db_token').value(),
      "of": request['of'],
      "content": request['content']
    };
    if ( !isEmpty(request['limit']) ) { r['limit'] = request['limit']; }
    if ( !isEmpty(request['offset']) ) { r['offset'] = request['offset']; }
    if ( !isEmpty(request['where']) ) { r['where'] = request['where']; }

    this.last = request['of'];
    _.post("/", JSON.stringify(r))
    .done(function (data) {
      Display.closeModal();
      Display.message( {content:"Successfull updated "+data.hits+" entry(s) of "+request['of'], color:Display.color_success} );
    })
    .fail(function (data) {
      if (data.status == "error") {
        if (data.msg == "unauthorised") {
          return Display.message( {content:"Unauthorised, please check token", color:Display.color_warn} );
        }
        return Display.message( {content:data.msg, color:Display.color_fail} );
      } else {
        return Display.message( {content:"Unknown Server Error", color:Display.color_fail} );
      }
    })
  }
}
Update = new Update();