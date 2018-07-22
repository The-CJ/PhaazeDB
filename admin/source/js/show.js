function show_container(button_obj) {
  let btn = $(button_obj);
  let path = btn.attr('path');
  let token = $('#db_token').val();

  let x = {"action":"show", "token":token, "path":path};

  $.get('/', x)
  .done(function (data) {
    console.log(data);
  })
  .fail(function (data) {
    data = data.responseJSON;
    console.log(data);
  })

}