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
  .done(function (data) {
    console.log(data);
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    if (data.status == "error") {
      if (data.msg == "unauthorised") {
        display_message( {content:"Unauthorised, please check token", color:"#fa3"} );
        display_message_in_modal($('#insert_modal'), {content:"Unauthorised, please check token", color:"#fa3"});
        return notify_incorrect_token();
      }
      display_message_in_modal($('#insert_modal'), {content:data.msg, color:"#fa3"});
      return display_message( {content:data.msg, color:"#fa3"} );
    } else {
      display_message_in_modal($('#insert_modal'), {content:"Unknown Server Error", color:"#f00"});
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
      display_message_in_modal($('#insert_modal'), {content:"no key can be empty", color:"orange"});
      return ;
    }

    new_object[key] = get_value_in_right_type(value, type);
  }


  console.log(new_object);
  return insert({"into":table_name, "content": new_object});

}

function start_insert() {
  $('#insert_modal').find('[name=into]').val( last_selected_container )
  $('#insert_modal').find('.need_correction').removeClass('need_correction');
  $('#insert_modal').modal('show');
}

function get_select_with_options() {
  let x = $('<select class="btn typeof_string" onchange="update_typeof_color($(this), this.value)">');
  x.append( $('<option value="string">String</option>') );
  x.append( $('<option value="number">Number</option>') );
  x.append( $('<option value="bool">Bool</option>') );
  x.append( $('<option value="object">Object</option>') );
  x.append( $('<option value="none">None/null</option>') );
  return x;
}

