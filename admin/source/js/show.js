function show_container(button_obj) {
  let btn = $(button_obj);
  let path = btn.attr('path');
  let token = $('#db_token').val();

  if (btn.attr('loaded') == "true") {
    btn.siblings('.collapse').collapse('hide');
    btn.attr('loaded', 'false');
    return ;
  }

  let x = {"action":"show", "token":token, "path":path};

  $.get('/', x)
  .done(function (data) {
    var content_list = btn.siblings('.collapse').find('.content-list');
    content_list.html('');
    for (supercontainer in data.tree.supercontainer) {
      let sc = $('<div class="supercontainer">');
      let bu = $('<button class="btn">');
      bu.attr('onclick', "show_container(this)");
      bu.attr('path', btn.attr('path') + "/" + supercontainer);
      bu.text(supercontainer);
      sc.append(bu);
      let c = $('<div class="collapse">');
      c.append( $('<div class="content-list">') );
      sc.append(c);

      content_list.append(sc);

    }
    for (container of data.tree.container) {
      let b = $('<button>');
      b.addClass('btn container_button');
      b.attr('path', btn.attr('path') + "/" + container);
      b.attr('onclick', "preview_select(this)");
      b.text(container);

      content_list.append(b);
    }
    btn.attr('loaded', "true");
    content_list.closest('.collapse').collapse('show');
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    if (data.msg == "unauthorised") {
      display_message( {content:"Unauthorised, please check token", color:"#fa3"} );
      notify_incorrect_token();
    } else {
      display_message( {content:"Unknown Server Error", color:"#f00"} );
    }
  })

}