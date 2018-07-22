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