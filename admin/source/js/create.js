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
    display_message({content:"Successfull created '"+name+"'", color:"#afa"});
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    display_message({content:data.msg, color:"#fa3"});
  })

}

class Create {
  constructor() {

  }
  start() {
    var field = _("[modal='create'] [name=container]");
    let new_name = field.value();
    if (new_name == false) {
      field.addClass("need-correction"); return;
    }
    this.execute(new_name);
  }
  execute(name) {
    let d = {
      'action': 'create',
      'token': _('#db_token').value(),
      'name': name
    };
    _.post('/', d)
    .done(function (data) {
      Display.closeModal();
      Display.message( {content:"Successfull created '"+name+"'", color:Display.color_success} );
    })
    .fail(function (data) {
      Display.message({content:data.msg, color:Display.color_fail});
    })
  }
}

Create = new Create();
