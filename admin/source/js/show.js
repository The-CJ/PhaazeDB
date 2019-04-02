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

class Show {
  constructor() {

  }
  open(html_btn) {
    html_btn = _(html_btn);
    if (html_btn.attribute('loaded') == "true") {
      console.log(html_btn.siblings('.collapse'));
      html_btn.siblings('.collapse').collapse('hide');
      html_btn.attribute('loaded', 'false');
      return ;
    }

    let path = html_btn.attribute('path');
    let r = {
      "action":"show",
      "token":_('#db_token').value(),
      "path":path
    };
    var ShowO = this;
    _.get("/", r)
    .done(function (data) {
      ShowO.build(html_btn, data);
    })
    .fail(function (data) {
      if (data.msg == "unauthorised") {
        Display.message( {content:"Unauthorised, please check token", color:Display.color_warn} );
      }
      else {
        Display.message( {content:"Unknown Server Error", color:Display.color_fail} );
      }
    })
  }

  build(start_element, data) {
    var content_list = start_element.siblings('.collapse.content-list');
    content_list.html('');

    for (let supercontainer in data.tree.supercontainer) {
      let folder_supercontainer = _.create('<div class="supercontainer">');
      let btn_supercontainer = _.create('<button class="btn">');
      btn_supercontainer.attribute('onclick', "Show.open(this)");
      btn_supercontainer.attribute('path', start_element.attribute('path')+"/"+supercontainer);
      btn_supercontainer.text(supercontainer);
      folder_supercontainer.append(btn_supercontainer);
      let next_content_list = _.create('<div class="collapse content-list">');
      folder_supercontainer.append(next_content_list);

      content_list.append(folder_supercontainer);

    }

    for (let container of data.tree.container) {
      let btn_container = _.create('<button class="btn">');
      btn_container.attribute('path', start_element.attribute('path')+"/"+container);
      btn_container.attribute('onclick', "Select.preview(this)");
      btn_container.text(container);

      content_list.append(btn_container);
    }
    
    start_element.attribute('loaded', "true");
    content_list.collapse('show');
  }

}

Show = new Show;