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

  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};

  })

}