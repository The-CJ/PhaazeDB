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

    return update({"of":table_name, "content": new_object});

  }
  else if (method == 'string_content') {

    let exec_string = $('#update_modal [entry-type=string_content] [name=content]').val();
    return update({"of":table_name, "content": exec_string});
  }

}

function start_update() {
  $('#update_modal').find('[name=into]').val( last_selected_container )
  $('#update_modal').find('.need_correction').removeClass('need_correction');
  $('#update_modal').modal('show');
}

function switch_entry_type(entry_type) {
  $('#update_modal [method]').val(entry_type);

  $('[entry-type-button]').removeClass('selected');
  $('[entry-type-button='+entry_type+']').addClass('selected');

  $('[entry-type]').hide();
  $('[entry-type='+entry_type+']').show();

}