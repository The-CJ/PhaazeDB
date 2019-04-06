// global vars
var last_selected_container = "";
var curl = {};

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
      console.log(r);
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
    _("[modal="+modal+"] input").removeClass("need-correction");
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

  changeType(obj, value) {
    _(obj).attribute("field-type", value);
  }

  message(msg) {
    let content = msg['content'];
    let color = msg['color'];
    let text_color = msg['text'];
    let time = msg['time'];

    let new_message = _.create('<div class="message text-center">');
    new_message.text(content);

    if (color == null) { color = "lightgrey"; }
    new_message.css('background', color);

    if (text_color == null) { text_color = "black"; }
    new_message.css('color', text_color);

    _('#message_space').append(new_message);

    if (time == null) { time = 5; }

    time = time * 1000
    setTimeout(function () {
      new_message.remove();
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

    inputs.append( _.create('<input class="col" type="text" placeholder="Key">') );
    inputs.append( _.create('<span>').text("-") );
    inputs.append( _.create('<input class="col" type="text" placeholder="Value">') );

    let button = _.create('<button type="button" class="btn orange">');
    button.text("X");
    button.attribute('onclick', '_(this).closest(".key-value-field").remove()');
    controlls.append( _.create('<div class="col">').append( this.getTypeSelect(type) ) );
    controlls.append( _.create('<div class="col">').append( button ) );

    element.append(inputs);
    element.append(controlls);
    return element;
  }

  getTypeSelect() {
    let ts = _.create('<select class="btn" field-type="string" onchange="Display.changeType(this, this.value)">');
    ts.append( _.create('<option value="string">String</option>') );
    ts.append( _.create('<option value="number">Number</option>') );
    ts.append( _.create('<option value="bool">Bool</option>') );
    ts.append( _.create('<option value="object">Object</option>') );
    ts.append( _.create('<option value="none">None/null</option>') );
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

  generateResultColString(key, value) {
    let obj = _.create('<div class="result-col" field-type="string"></div>');
    obj.append( _.create('<div class="key">').text(key) );
    obj.append( _.create('<input class="value" type="text">').value(value) );
    return obj;
  }

  generateResultColNumber(key, value) {
    let obj = _.create('<div class="result-col" field-type="number"></div>');
    obj.append( _.create('<div class="key">').text(key) );
    obj.append( _.create('<input class="value" type="number">').value(value) );
    return obj;
  }

  generateResultColObject(key, value) {
    let obj = _.create('<div class="result-col" field-type="object"></div>');
    obj.append( _.create('<div class="key">').text(key) );
    obj.append( _.create('<textarea class="value">').value(JSON.stringify(value)) );
    return obj;
  }

  generateResultColBool(key, value) {
   let obj = _.create('<div class="result-col" field-type="bool"></div>');
   obj.append( _.create('<div class="key">').text(key) );
   let s = _.create('<div class="switch value">');
   s.attribute('state', String(value));
   s.attribute('onclick', 'let t = _(this); t.attribute("state") == "true" ? t.attribute("state", "false") : t.attribute("state", "true")');
   obj.append(s);
   return obj;
 }

  generateResultColRemove(key) {
    let obj = $('<div class="result-col" field-type="remove"></div>');
    obj.append( $('<div class="key">').text(key) );
    obj.append( $('<input disabled class="value" type="text">').value('Remove') );
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

// events
document.addEventListener("DOMContentLoaded", function () {
  // restore view
  Utils.loadToken();
  DynamicURL.restoreWindow();
})










  //extract_curl();

  //let t = window.sessionStorage.getItem('token');
  //if (t != null) { $('#db_token').val(t) }

  //set_window_from_url();

  //if (curl['container'] != "" && curl['container'] != null) {
  //  let r = curl;
  //  r['of'] = curl['container'];
  //  select(r, preview=true);
  //}

function edit_select(entry_col) {
  let c = $(entry_col);
  if (c.hasClass("selected")) {
    $('#result_space').find(".selected").removeClass("selected");
    $('#col_edit_menu').collapse('hide');
    return ;
  }
  $('#result_space').find(".selected").removeClass("selected");
  c.addClass("selected");
  $('#col_edit_menu').collapse('show');
}

function close_all_edit() {
  $('#result_space').find(".selected").removeClass("selected");
  $('#col_edit_menu').collapse('hide');
}

function change_col_type(type) {
  let C = $('#result_space .selected');
  let key = C.find('.key').text();

  let x = null;

  if (type == "string") {
    x = generate_string(key);
  }
  else if (type == "none") {
    x = generate_none(key);
  }
  else if (type == "number") {
    x = generate_number(key);
  }
  else if (type == "bool") {
    x = generate_bool(key);
  }
  else if (type == "object") {
    x = generate_object(key);
  }
  else if (type == "remove") {
    x = generate_remove(key);
  }
  else {
    alert('Error');
  }
  x.addClass('selected');
  C.replaceWith(x);
}

function save_col_changes() {
  let selected_col = $('#result_space .selected');
  let entry_key = selected_col.find('.key').text();

  let entry_val = selected_col.find('input, textarea').val();
  if (entry_val == null) {
    entry_val = selected_col.find('.switch').attr('state');
    if (entry_val == "true") {
      entry_val = true;
    } else {
      entry_val = false;
    }
  }

  let entry_row = selected_col.closest('.result_row');
  let entry_id = entry_row.find('.typeof_id').find('input').val();
  let type = selected_col.attr('object_type');

  let r = {};
  r['of'] = $('#current_container').text();
  if (type != "remove") {
    r['content'] = {};
    r['content'][entry_key] = get_value_in_right_type(entry_val, type);
  }
  else {
    r['content'] = "del data['"+entry_key+"']";
    selected_col.remove();
  }
  r['where'] = "data['id'] == "+entry_id;
  r['limit'] = 1;

  update(r);

}

function notify_incorrect_token() {
  $('#db_token').focus();
  $('#db_token').css('background', '#fa0');
  setTimeout(function () {
    $('#db_token').css('background', 'none');
  }, 500);
  setTimeout(function () {
    $('#db_token').css('background', '#fa0');
  }, 1000);
  setTimeout(function () {
    $('#db_token').css('background', 'none');
  }, 1500);
}
