class Drop {
  constructor() {
    this.last = "";
  }
  start() {
    var field = _("[modal='drop'] [name=container]");
    let container_name = field.value();
    if (container_name == false) {
      field.addClass("need-correction"); return;
    }
    this.execute(container_name);
  }
  execute(name) {
    let r = {
      'action': 'drop',
      'token': _('#db_token').value(),
      'name': name
    };
    this.last = name;
    _.post('/', JSON.stringify(r))
    .done(function (data) {
      Display.closeModal();
      Display.message( {content:"Successfull dropped '"+name+"'", color:Display.color_success} );
    })
    .fail(function (data) {
      return Display.message( {content:data.msg ? data.msg : "unknown server error", color:Display.color_fail} );
    })
  }
}
Drop = new Drop();
