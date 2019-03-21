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
  let key_value_btn = $('<button type="button" class="btn btn-block btn-success">').text("Add");
  key_value_btn.click(function () {
    add_key_value_field(result_space);
  })
  $("#container_edit_modal .modal-result-footer").append(key_value_btn);

}
