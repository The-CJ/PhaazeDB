class Create {
  constructor() {
    this.last = "";
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
    let r = {
      'action': 'create',
      'token': _('#db_token').value(),
      'name': name
    };
    this.last = name;
    _.post('/', r)
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
