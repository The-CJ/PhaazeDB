function start_container_drop() {
  $('#container_drop_modal').find('[name=container]').val( last_selected_container );
  $('#container_drop_modal').find('.need_correction').removeClass('need_correction');
  $('#container_drop_modal').modal('show');
  curl['modal'] = 'container_drop';
  update_curl();
}

function modal_drop() {
  let name = $('#container_drop_modal [name=container]').val();
  return drop(name);
}
function drop(name) {
  let d = {
    'action': 'drop',
    'token': $('#db_token').val(),
    'name': name
  };
  $.post('/', d)
  .done(function (data) {
    $('#container_drop_modal').modal('hide');
    display_message({content:"Successfull dropped '"+request.into+"'", color:"#afa"});
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    display_message({content:data.msg, color:"#fa3"});
  })

}
