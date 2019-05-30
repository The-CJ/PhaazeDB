class Option {
  constructor() {
    this.last = "";
  }

  notifyShutdown() {
    Display.message( {content:"PhaazeDB got a shutdown event", color:Display.color_warn} );
    setTimeout(function () {
      var t = _('body');
      t.css('padding', '25%');
      t.addClass('text-center text-white');
      t.html("");
      t.append( _.create('<h1>DB has been shut down</h1>') );
      t.append( _.create('<h2>Restart required</h2>') );
    }, 4000);
  }

  optionLogging(state) {
    if (isEmpty(state)) { state = "" }
    return this.execute("log", state);
  }

  optionShutdown() {
    if (confirm("Shut down PhaazeDB?")) { this.execute("shutdown"); }
  }

  optionPassword() {
    let token = _("[modal=password] [name=token]").value();
    if (isEmpty(token)) {
      alert("You can not leave the token empty");
      return;
    }

    this.execute("password", token);

  }

  execute(name, value) {
    if (name == null) { name = "" }
    if (value == null) { value = "" }

    let r = {
      'action': 'option',
      'token': _('#db_token').value(),
      "option": name,
      "value": value
    };
    this.last = {name: value};
    var OptionO = this;
    _.post('/', JSON.stringify(r))
    .done(function (data) {
      if (name == "shutdown") { OptionO.notifyShutdown() }
      else { Display.message({content:data.msg, color:Display.color_success}); }
    })
    .fail(function (data) {
      Display.message({content:data.msg, color:Display.color_fail});
    })
  }
}
Option = new Option();
