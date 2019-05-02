class Create {
  constructor() {
    this.last = "";
  }
  start() {
    var field = _("[modal='create'] [name=container]");
    let new_name = field.value();
    if (isEmpty(new_name)) {
      field.addClass("need-correction"); return;
    }
    this.execute(new_name);
  }
  execute(name) {
    let r = {
      'action': 'create',
      'token': _('#db_token').value(),
      'name': name
    };
    this.last = name;
    _.post('/', JSON.stringify(r))
    .done(function (data) {
      Display.closeModal();
      Display.message( {content:"Successfull created '"+name+"'", color:Display.color_success} );
    })
    .fail(function (data) {
      return Display.message( {content:data.msg ? data.msg : "unknown server error", color:Display.color_fail} );
    })
  }
}
Create = new Create();
