function start_container_create() {
  $('#container_create_modal').find('[name=container]').val( last_selected_container );
  $('#container_create_modal').find('.need_correction').removeClass('need_correction');
  $('#container_create_modal').modal('show');
  curl['modal'] = 'container_create';
  update_curl();
}

function modal_create() {
  let name = $('#container_create_modal [name=container]').val();
  return create(name);
}

function create(name) {
  let d = {
    'action': 'create',
    'token': $('#db_token').val(),
    'name': name
  };
  $.post('/', d)
  .done(function (data) {
    $('#container_create_modal').modal('hide');
    display_message({content:"Successfull created '"+request.into+"'", color:"#afa"});
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    display_message({content:data.msg, color:"#fa3"});
  })

}