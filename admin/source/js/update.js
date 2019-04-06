function update(r) {
  if (r == null) {
    r = {};
  }

  let request = {
    "action": "update",
    "of": r['of'],
    "token": $('#db_token').val(),
    "content": r['content']
  };
  if (r.limit != null) {
    request['limit'] = r.limit;
  }
  if (r.offset != null) {
    request['offset'] = r.offset;
  }
  if (r.where != null) {
    request['where'] = r.where;
  }
  $.post("/", JSON.stringify(request))
  .done(function (result) {
    $('#update_modal').modal('hide');
    display_message({content:"Update: affected '"+result.hits+"' entry(s)", color:"#afa"});
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    if (data.status == "error") {
      if (data.msg == "unauthorised") {
        display_message( {content:"Unauthorised, please check token", color:"#fa3"} );
        return notify_incorrect_token();
      }
      return display_message( {content:data.msg, color:"#fa3"} );
    } else {
      return display_message( {content:"Unknown Server Error", color:"#f00"} );
    }
  })
}

function modal_update() {
  let modal = $('#update_modal');
  let table_name = modal.find('[name=of]').val();
  if (table_name == "") {
    modal.find('[name=of]').addClass('need_correction').focus();
    return ;
  }

  let method = $('#update_modal [method]').val();
  if (method == 'field_content') {

    let new_object = {};
    for (field of $('#update_modal').find('.field_key_value') ) {
      field = $(field);
      let key = field.find('[placeholder=key]').val();
      let type = field.find('select').val();
      let value = field.find('[placeholder=value]').val();

      if (key == "") {
        field.find('[placeholder=key]').addClass('need_correction');
        display_message({content:"no key can be empty", color:"orange"});
        return ;
      }

      new_object[key] = get_value_in_right_type(value, type, key);
    }

    let r = {};
    r['of'] = table_name;
    r['where'] = modal.find('[name=where]').val();
    r['limit'] = modal.find('[name=limit]').val();
    r['offset'] = modal.find('[name=offset]').val();
    r["content"] = new_object;

    return update(r);

  }
  else if (method == 'string_content') {

    let exec_string = $('#update_modal [entry-type=string_content] [name=content]').val();
    let r = {};
    r['of'] = table_name;
    r['where'] = modal.find('[name=where]').val();
    r['limit'] = modal.find('[name=limit]').val();
    r['offset'] = modal.find('[name=offset]').val();
    r["content"] = exec_string;

    return update(r);
  }

}
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
    console.log(request);
  }
}
Update = new Update();