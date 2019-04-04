function insert(r) {
  if (r == null) {
    r = {};
  }

  let request = {
    "action": "insert",
    "into": r['into'],
    "token": $('#db_token').val(),
    "content": r['content']
  };
  $.post("/", JSON.stringify(request))
  .done(function (result) {
    $('#insert_modal').modal('hide');
    display_message({content:"Successfull inserted into '"+request.into+"' - ID: "+result.data.id, color:"#afa"});
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

function modal_insert() {
  let modal = $('#insert_modal');
  let table_name = modal.find('[name=into]').val();
  if (table_name == "") {
    modal.find('[name=into]').addClass('need_correction').focus();
    return ;
  }

  let new_object = {};
  for (field of $('#insert_modal').find('.field_key_value') ) {
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

  return insert({"into":table_name, "content": new_object});

}

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
    console.log(request);

  }
}

Insert = new Insert();
