class Describe {
  constructor() {
    this.last = "";
  }

  start() {
    var field = _("[modal='edit'] [name=container]");
    let name = field.value();
    if (isEmpty(name)) {
      field.addClass("need-correction"); return;
    }
    this.execute(name);
  }

  execute(name) {
    let r = {
      'action': 'describe',
      'token': _('#db_token').value(),
      'name': name
    };

    var this2 = this;
    _.post('/', JSON.stringify(r))
    .done(function (data) {
      this2.build(data.default);
    })
    .fail(function (data) {
      return Display.message( {content:data.msg ? data.msg : "unknown server error", color:Display.color_fail} );
    })

  }

  build(data) {
    var describe_result = _("[modal=edit] [default-fields]").html("");
    if (isEmpty(data)) {
      return describe_result.addClass("empty");
    } else {
      describe_result.siblings(".modal-result-footer").show();
      describe_result.removeClass("empty");
    }
    for (var key in data) {
      let value = data[key];

      if (value === null) {
        describe_result.append(Template.getKeyValueField(key, null, "none"))
      }
      else if (typeof value == "string") {
        describe_result.append(Template.getKeyValueField(key, value, "string"))
      }
      else if (typeof value == "number") {
        describe_result.append(Template.getKeyValueField(key, value, "number"))
      }
      else if (typeof value == "boolean") {
        describe_result.append(Template.getKeyValueField(key, value, "bool"))
      }
      else if (typeof value == "object") {
        describe_result.append(Template.getKeyValueField(key, JSON.stringify(value), "object"))
      }

    }
  }
}
Describe = new Describe();

class DefaultSet {
  constructor() {
    this.last = "";
  }

  modalAddField() {
    let n = Template.getKeyValueField();
    _('[modal=edit] [default-fields]').append(n);
  }

  start() {
    let modal = _('[modal=edit]');
    let container = modal.find('[name=container]').value();
    if (isEmpty(container)) { return modal.find('[name=container]').addClass('need-correction'); }

    let new_object = {};

    for (let field of modal.find(".key-value-field").result) {
      field = _(field);
      let key = field.find("[placeholder=Key]").value();
      let value = field.find("[placeholder=Value]").value();
      let type = field.find("select").value();

      if (isEmpty(key)) {
        field.find("[placeholder=Key]").addClass('need-correction');
        return Display.message({content:"no key can be empty", color:Display.color_warn});
      }

      try { new_object[key] = getValueInRightType(value, type); }
      catch (e) {
        Display.message( {content:"invalid json object", color:Display.color_warn} );
        return field.find("[placeholder=Value]").addClass("need-correction");
      }
    }
    return this.execute({"name":container, "content": new_object});
  }

  execute(request) {
    if (request == null) { request = {}; }
    let r = {
      "action": "default",
      "token": _('#db_token').value(),
      "name": request['name'],
      "content": request['content']
    };

    this.last = request['into'];

    _.post("/", JSON.stringify(r))
    .done(function (data) {
      Display.closeModal();
      Display.message( {content:"Successfull set defalut of: "+request.name, color:Display.color_success} );
    })
    .fail(function (data) {
      if (data.msg == "unauthorised") {
        return Display.message( {content:"Unauthorised, please check token", color:Display.color_warn} );
      }
      else {
        return Display.message( {content:data.msg ? data.msg : "unknown server error", color:Display.color_fail} );
      }
    })
  }
}
DefaultSet = new DefaultSet();