class Describe {
  constructor() {
    this.last = "";
  }

  start() {
    var field = _("[modal='edit'] [name=container]");
    let name = field.value();
    if (isEmpty(name)) {
      field.addClass("need-correction"); return;
    }
    this.execute(name);
  }

  execute(name) {
    let r = {
      'action': 'describe',
      'token': _('#db_token').value(),
      'name': name
    };

    var this2 = this;
    _.post('/', JSON.stringify(r))
    .done(function (data) {
      this2.build(data.default);
    })
    .fail(function (data) {
      return Display.message( {content:data.msg ? data.msg : "unknown server error", color:Display.color_fail} );
    })

  }

  build(data) {
    var describe_result = _("[modal=edit] [default-fields]").html("");
    if (isEmpty(data)) {
      describe_result.siblings(".modal-result-footer").hide();
      return describe_result.addClass("empty");
    } else {
      describe_result.siblings(".modal-result-footer").show();
      describe_result.removeClass("empty");
    }
    for (var key in data) {
      let value = data[key];

      if (value === null) {
        describe_result.append(Template.getKeyValueField(key, null, "none"))
      }
      else if (typeof value == "string") {
        describe_result.append(Template.getKeyValueField(key, value, "string"))
      }
      else if (typeof value == "number") {
        describe_result.append(Template.getKeyValueField(key, value, "number"))
      }
      else if (typeof value == "boolean") {
        describe_result.append(Template.getKeyValueField(key, value, "bool"))
      }
      else if (typeof value == "object") {
        describe_result.append(Template.getKeyValueField(key, JSON.stringify(value), "object"))
      }

    }
  }
}
Describe = new Describe();

function set_default() {
  var new_default = {};
  var fields = $("#container_edit_modal .modal-result .field_key_value");
  for (field of fields) {
    field = $(field);
    let key = field.find('[placeholder=key]').val();
    let type = field.find('select').val();
    let value = field.find('[placeholder=value]').val();

    if (key == "") {
      field.find('[placeholder=key]').addClass('need_correction');
      display_message({content:"no key can be empty", color:"orange"});
      return ;
    }

    new_default[key] = get_value_in_right_type(value, type, key);

  }
  let name = $('#container_edit_modal [name=container]').val();
  let d = {
    'action': 'default',
    'token': $('#db_token').val(),
    'container': name,
    'default': new_default
  };
  $.post('/', JSON.stringify(d))
  .done(function (data) {
    display_message( {content:"Successfull updated default template for: "+data.container, color:"#ccc"} );
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    display_message({content:data.msg, color:"#fa3"});
  })
}
