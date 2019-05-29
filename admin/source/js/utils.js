// global functions
function isEmpty(o) {
  // null
  if (o == null) { return true; }
  // string
  if (typeof o == "string") { if (o != "") { return false; } }
  // number
  if (typeof o == "number") { if (o != 0) { return false; } }
  // object
  for (var v in o) {
    if (o.hasOwnProperty(v)) {
      return false
    }
  }
  return true;
}

function getValueInRightType(value, type) {
  if (typeof type == "undefined") { throw "2 arguments 'value' and 'type' required" }

  if (type == "string") { return String(value); }
  else if (type == "number") { return Number(value); }
  else if (type == "bool") { return Boolean(value); }
  else if (type == "none") { return null; }
  else if (type == "object") {
    try { return JSON.parse(value); }
    catch (e) { throw "invalid json object"; }
  }
  else { throw "unknown type for value" }
}

// utils classes
class DynamicURL {
  constructor() {
    this.values = {};
    this.init()
  }

  init() {
    this.values['container'] = this.get('container');
    this.values['where'] = this.get('where');
    this.values['limit'] = this.get('limit');
    this.values['offset'] = this.get('offset');
    this.values['modal'] = this.get('modal');
    this.values['fields'] = this.get('fields');
    this.values['settings'] = this.get('settings');
  }

  set(key, value, update=true) {
    this.values[key] = value;
    if (update) { this.update(); }
  }

  get(key) {
    let value = this.values[key];
    if (value == null) {
      value = this.getFromLocation(key);
    }
    return value
  }

  update() {
    let ucurl = "/admin";
    let pre = "?";

    for (var key in this.values) {
      let value = this.values[key];
      if (isEmpty(value)) { continue; }

      ucurl = ucurl + pre + key + "=" + value;
      pre = "&";

    }
    window.history.pushState('obj', 'newtitle', ucurl);
  }

  getFromLocation(name) {
    let url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
  }

  restoreWindow() {
    // restores a window from URL parameters

    // reopen modals
    if ( !isEmpty(this.values.modal) ) {
      Display.showModal(this.values.modal);
    }

    // reopen settings
    if ( !isEmpty(this.values.settings) ) {
      Edit.startSettings();
    }

    // set last viewed container
    if ( !isEmpty(this.values.container) ) {
      _("#current_container").text( this.values.container );
      _('[name=of], [name=into], [name=container]').value(this.values.container);

      let r = {
        "of":this.values.container,
        "where":this.values.where,
        "offset":this.values.offset,
        "limit":this.values.limit,
        "fields":this.values.fields
      };
      Select.execute( r, true );
    }
    if ( !isEmpty(this.values.limit) ) {
      _('[name=limit]').value(this.values.limit);
    }
    if ( !isEmpty(this.values.offset) ) {
      _('[name=offset]').value(this.values.offset);
    }
    if ( !isEmpty(this.values.where) ) {
      _('[name=where]').value(this.values.where);
    }
    if ( !isEmpty(this.values.fields) ) {
      _('[name=fields]').value(this.values.fields);
      Select.showFieldSelect();
    }

  }
}
DynamicURL = new DynamicURL();

class Display {
  constructor() {
    this.color_fail = "#faa631";
    this.color_warn = "#e9a100";
    this.color_success = "#74ff74";
    this.color_neutral = "#c2c2c2";
  }

  showModal(modal, hold_other_open=false) {
    if (!hold_other_open) { this.closeModal(); }
    _("[modal="+modal+"], [modal-close]").addClass("show");
    _("[modal="+modal+"] .need-correction").removeClass("need-correction");
    DynamicURL.set("modal", modal);
  }

  closeModal(modal) {
    if (typeof modal == "undefined") {
      _("[modal], [modal-close]").removeClass("show");
    } else {
      _("[modal="+modal+"], [modal-close]").removeClass("show");
    }
    DynamicURL.set("modal", null);
  }

  changeType(obj, value, override) {
    if (typeof override != "undefined") { value = override; }
    _(obj).attribute("field-type", value);
  }

  message(msg) {
    let content = msg['content'];
    let color = msg['color'];
    let text_color = msg['text'];
    let time = msg['time'];

    var msg_id = (Math.random()*500).toFixed();

    let new_message = _.create('<div class="message text-center">');

    new_message.attribute("msg_id", "MSG"+msg_id);
    new_message.text(content);

    if (color == null) { color = "lightgrey"; }
    new_message.css('background', color);

    if (text_color == null) { text_color = "black"; }
    new_message.css('color', text_color);

    _('#message_space, .message-space').append(new_message, true);

    if (time == null) { time = 5; }

    time = time * 1000
    setTimeout(function () {
      _(".message[msg_id=MSG"+msg_id+"]").remove();
    }, time);

  }
}
Display = new Display();

class Template {
  constructor() {

  }

  getKeyValueField(key, value, type) {
    let element = _.create('<div class="center-item-row key-value-field"></div>');
    let inputs = _.create('<div class="col center-item-row">');
    let controlls = _.create('<div class="center-item-row">');

    inputs.append( _.create('<input class="col" type="text" placeholder="Key">').value(key ? key : "") );
    inputs.append( _.create('<span>').text("-") );
    inputs.append( _.create('<input class="col" type="text" placeholder="Value">').value(value ? value : "") );

    let button = _.create('<button type="button" class="btn orange">');
    button.text("X");
    button.attribute('onclick', '_(this).closest(".key-value-field").remove()');
    controlls.append( _.create('<div class="col">').append( this.getTypeSelect(type) ) );
    controlls.append( _.create('<div class="col">').append( button ) );

    element.append(inputs);
    element.append(controlls);
    return element;
  }

  getTypeSelect(type) {
    let ts = _.create('<select class="btn" field-type="string" onchange="Display.changeType(this, this.value)">');
    ts.append( _.create('<option value="string">String</option>').attribute("selected", type == "string" ? true : null) );
    ts.append( _.create('<option value="number">Number</option>').attribute("selected", type == "number" ? true : null) );
    ts.append( _.create('<option value="bool">Bool</option>').attribute("selected", type == "bool" ? true : null) );
    ts.append( _.create('<option value="object">Object</option>').attribute("selected", type == "object" ? true : null) );
    ts.append( _.create('<option value="none">None/null</option>').attribute("selected", type == "none" ? true : null) );
    Display.changeType(ts.result[0], null, type ? type : "string")
    return ts;
  }

  generateResultColID(value) {
    let obj = _.create('<div class="result-col" field-type="id"></div>');
    obj.append( _.create('<div class="key">').text("ID") );
    obj.append( _.create('<input class="value" readonly type="number">').value(value) );
    return obj;
  }

  generateResultColNone(key) {
    let obj = _.create('<div class="result-col" field-type="none"></div>');
    obj.append( _.create('<div class="key">').text(key) );
    obj.append( _.create('<input class="value" disabled type="text">').value('None/null') );
    return obj;
  }

  generateResultColString(key, value="") {
    let obj = _.create('<div class="result-col" field-type="string"></div>');
    obj.append( _.create('<div class="key">').text(key) );
    obj.append( _.create('<input class="value" type="text">').value(value) );
    return obj;
  }

  generateResultColNumber(key, value="0") {
    let obj = _.create('<div class="result-col" field-type="number"></div>');
    obj.append( _.create('<div class="key">').text(key) );
    obj.append( _.create('<input class="value" type="number">').value(value) );
    return obj;
  }

  generateResultColObject(key, value="{}") {
    let obj = _.create('<div class="result-col" field-type="object"></div>');
    obj.append( _.create('<div class="key">').text(key) );
    obj.append( _.create('<textarea class="value">').value(JSON.stringify(value)) );
    return obj;
  }

  generateResultColBool(key, value="false") {
    let obj = _.create('<div class="result-col" field-type="bool"></div>');
    obj.append( _.create('<div class="key">').text(key) );
    let s = _.create('<div class="switch value">');
    s.attribute('state', String(value));
    s.attribute('onclick', 'let t = _(this); t.attribute("state") == "true" ? t.attribute("state", "false") : t.attribute("state", "true")');
    obj.append(s);
    return obj;
  }

  generateResultColRemove(key) {
    let obj = _.create('<div class="result-col" field-type="remove"></div>');
    obj.append( _.create('<div class="key">').text(key) );
    obj.append( _.create('<input disabled class="value" type="text">').value('Save to remove') );
    return obj;
  }

}
Template = new Template();

class Utils {
  constructor() {

  }

  saveToken() {
    let x = _('#db_token').value();
    window.sessionStorage.setItem('token', x);
    _('.token-input > .input-end').addClass('green').find('span').text('Saved for this session');
    setTimeout(function () { _('.token-input > .input-end').removeClass('green').find('span').text(''); }, 3000);
  }

  loadToken() {
    let x = window.sessionStorage.getItem('token');
    if (x != null) { _('#db_token').value(x); }
  }
}
Utils = new Utils();

class Edit {
  constructor() {
    this.last = {};
  }

  save() {
    let selected = _('#result_space .selected');
    let row = selected.closest(".result-row");
    let entry_id = row.find("[field-type=id] .value").value();
    if (isEmpty(entry_id)) { return Display.message( { content:"Could not find a ID Field in this row, can't quick edit", color:Display.color_warn } ); }

    let container = Select.last;
    let content = {};

    let selected_type = selected.attribute("field-type");
    let selected_key = selected.find(".key").text();
    let selected_value;
    let need_convert = true;

    if (selected_type == "bool") {
      selected_value = selected.find(".value").attribute("state") == "true" ? true : false ;
    }
    else if (selected_type == "remove") {
      selected_value = "del data["+JSON.stringify(selected_key)+"]";
      selected.remove();
      need_convert = false;
    }
    else {
      selected_value = selected.find(".value").value();
    }

    if (need_convert) {
      try {
        content[selected_key] = getValueInRightType(selected_value, selected_type);
      }
      catch (e) {
        return Display.message( {content:e, color:Display.color_warn} );
      }
    }
    else {
      content = selected_value;
    }

    let request = {
      "of": container,
      "where": "data['id'] == "+entry_id,
      "limit": 1,
      "content": content
    }
    this.last = request;
    return Update.execute(request);
  }

  saveSetting(option) {
    let r = {
      "action": "option",
      "option": option,
      "token": _('#db_token').value(),
    };
    r["value"] = _("[config="+option+"]").value();
    _.post("/", JSON.stringify(r))
    .done(function (data) {
      return Display.message( {content:data.msg + ": " + data.changed + " = " + data.new_value, color:Display.color_success} );
    })
    .fail(function (data) {
      if (data.msg == "unauthorised") {
        return Display.message( {content:"Unauthorised, please check token", color:Display.color_warn} );
      }
      else {
        return Display.message( {content:data.msg ? data.msg : "unknown server error", color:Display.color_fail} );
      }
    })
  }

  changeCol(type) {
    if (type == null) { type = "string" }
    let field = _('#result_space .selected');
    if (isEmpty(field.result)) {return ;}

    let key = field.find(".key").text();
    let value = field.find(".value").value();

    let new_field = null;

    if (type == "none") { new_field = Template.generateResultColNone(key) }
    else if (type == "string") { new_field = Template.generateResultColString(key, value) }
    else if (type == "number") { new_field = Template.generateResultColNumber(key, value) }
    else if (type == "bool") { new_field = Template.generateResultColBool(key, value) }
    else if (type == "object") { new_field = Template.generateResultColObject(key, value) }
    else if (type == "remove") { new_field = Template.generateResultColRemove(key) }
    else { new_field = Template.generateResultColUnknown(key, value) }

    if (new_field == null) { throw "Could not generate field"; }

    var EditO = this;
    new_field.addClass("selected");
    new_field.on("dblclick", function () { EditO.selectCol(this) });

    field.replaceWith(new_field);
  }

  selectCol(entry_col) {
    let c = _(entry_col);
    if (c.result[0].getAttribute("field-type") == "id") {return;}
    _('#result_space .selected').removeClass("selected");
    c.addClass("selected");
    _('#col_edit_menu').collapse('show');
  }

  stopEdit() {
    _('#result_space .selected').removeClass("selected");
    _('#col_edit_menu').collapse('hide');
  }

  startSettings() {
    DynamicURL.set("settings", "1");
    _("#overlay").addClass("show");
    let r = {
      "action": "option",
      "option": "config",
      "token": _('#db_token').value(),
    };
    _.post("/", JSON.stringify(r))
    .done(function (data) {
      for (var option in data.config) {
        let field = _("[config="+option+"]");
        field.value(data.config[option]);
      }
    })
    .fail(function (data) {
      if (data.msg == "unauthorised") {
        return Display.message( {content:"Unauthorised, please check token", color:Display.color_warn} );
      }
      else {
        return Display.message( {content:data.msg ? data.msg : "unknown server error", color:Display.color_fail} );
      }
    })
  }

  stopSettings() {
    DynamicURL.set("settings", null);
    _("#overlay").removeClass("show");
  }

}
Edit = new Edit();

class Store {
  constructor() {
    this.last = "";
  }

  start() {
    let request = {};

    request["container"] = _("[modal='store'] [name=container]").value();

    return this.execute(request);
  }

  import() {
    _('[modal=import] [name=token]').value(_('#db_token').value())
  }

  export() {
    _('[modal=export] [name=token]').value(_('#db_token').value())
    return;
  }

  execute(request) {
    if (request == null) { request = {}; }
    let r = {
      "action": "option",
      "option": "store",
      "token": _('#db_token').value(),
      "value": request['container']
    };
    this.last = request['container'];
    _.post("/", JSON.stringify(r))
    .done(function (data) {
      Display.closeModal();
      Display.message( {content:data.msg, color:Display.color_success} );
    })
    .fail(function (data) {
      if (data.msg == "unauthorised") {
        return Display.message( {content:"Unauthorised, please check token", color:Display.color_warn} );
      }
      else {
        return Display.message( {content:data.msg ? data.msg : "unknown server error", color:Display.color_fail} );
      }
    })
  }

}
Store = new Store();

// events
document.addEventListener("DOMContentLoaded", function () {
  // restore view
  Utils.loadToken();
  DynamicURL.restoreWindow();
})
