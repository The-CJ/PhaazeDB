var last_selected_container = ""

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

function update_typeof_color(obj, val) {
  let new_status = val;
  obj.removeClass('typeof_bool typeof_none typeof_number typeof_object typeof_string');
  obj.addClass('typeof_'+val)
}