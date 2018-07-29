var last_selected_container = "";
var curl = {};

$('document').ready(function () {
  extract_curl();
  set_window_from_url();
});

function display_message(message_obj) {

  content = message_obj['content'];
  color = message_obj['color'];
  text_color = message_obj['text_color'];
  time = message_obj['time'];

  let message = $('<div class="message text-center">');
  message.text(content);

  if (color == null) {
    color = "lightgrey";
  }
  message.css('background', color);

  if (text_color == null) {
    text_color = "black";
  }
  message.css('color', text_color);

  $('#message-space').append(message);

  if (time == null) {
    time = 5;
  }

  time = time * 1000
  setTimeout(function () {
    message.remove();
  }, time);

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

function add_key_value_field(into) {
  let field_space = into;
  let field = $('<div class="row field_key_value">');
  let inputs = $('<div class="col">').append( $('<div class="row">') );
  let controlls = $('<div class="col-3">').append( $('<div class="row">') );

  inputs.children('div').append( $('<input class="col" type="text" placeholder="key">') );
  inputs.children('div').append( $('<span class="col-1 text-center">').text('-')  );
  inputs.children('div').append( $('<input class="col" type="text" placeholder="value">') );
  field.append(inputs);

  controlls.children('div').append( $('<div class="col">').append( get_select_with_options() ) );
  controlls.children('div').append( $('<div class="col">').append( $('<button type="button" class="btn btn-warning">').text("X") ) );
  controlls.find('button').attr('onclick', '$(this).closest(".field_key_value").remove()');
  field.append(controlls);

  field_space.append(field);
}

function update_typeof_color(obj, val) {
  let new_status = val;
  obj.removeClass('typeof_bool typeof_none typeof_number typeof_object typeof_string');
  obj.addClass('typeof_'+val)
}

function get_value_in_right_type(value, type, key) {
  if (type == "string") {
    return String(value);
  }
  else if (type == "number") {
    return Number(value);
  }
  else if (type == "bool") {
    return Boolean(value);
  }
  else if (type == "none") {
    return null;
  }
  else if (type == "object") {
    try {
      let obj = JSON.parse(value);
      return obj;
    }
    catch (e) {
      var inputfield = $('.modal:visible input').filter(function () {
          return $(this).val() == value && $(this).closest('.field_key_value').find('select').val() == 'object';
      });
      inputfield.addClass('need_correction');
      display_message({content:"invalid json object", color:"orange"});
      throw "invalid json object";
    }
  }
  else {
    alert(value)
  }
}

function update_curl() {

  let ucurl = "/admin";
  let pre = "?";

  for (var key in curl) {
    let value = curl[key];
    if (value == null) {
      continue;
    }

    ucurl = ucurl + pre + key + "" + value;
    pre = "&";

  }
  window.history.pushState('obj', 'newtitle', ucurl);

}

function extract_curl() {

  let ncurl = {};

  ncurl['container'] = getParameter('container');
  ncurl['where'] = getParameter('where');
  ncurl['limit'] = getParameter('limit');
  ncurl['offset'] = getParameter('offset');
  ncurl['modal'] = getParameter('modal');

  curl = ncurl;
}

function getParameter(name) {
    let url = window.location.href;
    name = name.replace(/[\[\]]/g, '\\$&');
    var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

function set_window_from_url() {

  if (curl.container != null) {
    $('[name=of], [name=into]').val(curl.container);
    $('#current_container').val(curl.container);
  }
  if (curl.limit != null) {
    $('[name=limit]').val(curl.limit);
  }
  if (curl.offset != null) {
    $('[name=offset]').val(curl.offset);
  }
  if (curl.where != null) {
    $('[name=where]').val(curl.where);
  }

}