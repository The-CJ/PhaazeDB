function option_change(option, value) {
  if (option == null) { option = "" }
  if (value == null) { value = "" }

  let request = {
    "action":"option",
    "token": $('#db_token').val(),
    "option": option,
    "value": value
  };
  $.post('/', request)
  .done(function (data) {
    if (option == "shutdown") {
      display_message( {content:"DB is shutting down", color:"#ff8d55"} );
      setTimeout(function () {
        display_message( {content:"3", color:"#fa5"} );
      }, 1000);
      setTimeout(function () {
        display_message( {content:"2", color:"#fa5"} );
      }, 2000);
      setTimeout(function () {
        display_message( {content:"1", color:"#fa5"} );
      }, 3000);
      setTimeout(function () {
        var t = $('body');
        t.css('padding', '25%');
        t.addClass('text-center white-text');
        t.html('<h1>DB has been shut down</h1>');
        t.append('<h2>Restart required</h2>');
      }, 4000);
    }
    else {
      display_message( {content:data.msg, color:"#ddd"} );
    }

  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    display_message( {content:"Error", color:"#f44"} );
  })

}