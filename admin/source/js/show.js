class Show {
  constructor() {
    this.last = "";
  }

  open(html_btn) {
    html_btn = _(html_btn);

    if (html_btn.attribute('loaded') == "true") {
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
    this.last = path;
    var ShowO = this;
    _.post("/", JSON.stringify(r))
    .done(function (data) {
      ShowO.build(html_btn, data);
    })
    .fail(function (data) {
      if (data.msg == "unauthorised") {
        Display.message( {content:"Unauthorised, please check token", color:Display.color_warn} );
      }
      else {
        Display.message( {content:data.msg ? data.msg : "unknown server error", color:Display.color_fail} );
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
Show = new Show();
