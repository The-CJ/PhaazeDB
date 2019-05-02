class Insert {
  constructor() {
    this.last = "";
  }

  modalAddField() {
    let n = Template.getKeyValueField();
    _('[modal=insert] [insert-fields]').append(n);
  }

  modalClearFields() {
    _('[modal=insert] [insert-fields]').html("");
  }

  start() {
    let modal = _('[modal=insert]');
    let container = modal.find('[name=into]').value();
    if (isEmpty(container)) { return modal.find('[name=into]').addClass('need-correction'); }

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
    return this.execute({"into":container, "content": new_object});
  }

  execute(request) {
    if (request == null) { request = {}; }
    let r = {
      "action": "insert",
      "token": _('#db_token').value(),
      "into": request['into'],
      "content": request['content']
    };

    this.last = request['into'];

    _.post("/", JSON.stringify(r))
    .done(function (data) {
      Display.closeModal();
      Display.message( {content:"Successfull inserted into '"+request.into+"' - ID: "+data.data.id, color:Display.color_success} );
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
Insert = new Insert();
