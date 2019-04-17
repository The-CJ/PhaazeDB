function start_container_edit() {
  $('#container_edit_modal').find('[name=container]').val( last_selected_container );
  $('#container_edit_modal').find('.need_correction').removeClass('need_correction');
  $('#container_edit_modal').modal('show');
  curl['modal'] = 'container_edit';
  update_curl();
}

function describe() {
  let name = $('#container_edit_modal [name=container]').val();
  let d = {
    'action': 'describe',
    'token': $('#db_token').val(),
    'name': name
  };
  $.post('/', d)
  .done(function (data) {
    display_describe(data);
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    display_message({content:data.msg, color:"#fa3"});
  })

}

function display_describe(data) {
  var result_space = $("#container_edit_modal .modal-result").html("");

  result_space.append($("<h3>").text("Default: "+data.container));

  default_template = data.default;
  if (isEmpty(default_template)) {
    result_space.append($("<h2>").text("No defaults set"));
  }

  let key_value_btn = $('<button type="button" class="btn btn-block btn-warning">').text("Add");
  key_value_btn.click(function () {
    add_key_value_field(result_space);
  })
  let save_btn = $('<button type="button" class="btn btn-block btn-success">').text("Save");
  save_btn.click(function () {
    set_default();
  })

  $("#container_edit_modal .modal-result-footer").html("").append(key_value_btn).append(save_btn);

}

function set_default() {
  var new_default = {};
  var fields = $("#container_edit_modal .modal-result .field_key_value");
  for (field of fields) {
    field = $(field);
    let key = field.find('[placeholder=key]').val();
    let type = field.find('select').val();
    let value = field.find('[placeholder=value]').val();

    if (key == "") {
      field.find('[placeholder=key]').addClass('need_correction');
      display_message({content:"no key can be empty", color:"orange"});
      return ;
    }

    new_default[key] = get_value_in_right_type(value, type, key);

  }
  let name = $('#container_edit_modal [name=container]').val();
  let d = {
    'action': 'default',
    'token': $('#db_token').val(),
    'container': name,
    'default': new_default
  };
  $.post('/', JSON.stringify(d))
  .done(function (data) {
    display_message( {content:"Successfull updated default template for: "+data.container, color:"#ccc"} );
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    display_message({content:data.msg, color:"#fa3"});
  })
}
