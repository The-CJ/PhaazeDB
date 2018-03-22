var block_footer = false;
var last_opened_footer = "";

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

$('document').ready(
  function () {
    //load_container();
  }
)

function show_error(error) {

  var e = $('#error_phantom').html();

  var i = Math.floor(Math.random() * 10000);

  if (typeof error === 'object') {
    e = e.replace('{msg}', JSON.stringify(error));
  }
  else {
    e = e.replace('{msg}', error);
  }

  e = e.replace('{id}', i);

  $('#msg_display').append(e);
  setTimeout(function () {
    $('#msg_display > #'+i).remove();
  }, 5500);
}

function show_message(message) {

  var e = $('#message_phantom').html();

  var i = Math.floor(Math.random() * 10000);

  if (typeof message === 'object') {
    e = e.replace('{msg}', JSON.stringify(message));
  }
  else {
    e = e.replace('{msg}', message);
  }

  e = e.replace('{id}', i);

  $('#msg_display').append(e);
  setTimeout(function () {
    $('#msg_display > #'+i).remove();
  }, 5500);
}

function get_right_col_type(data_content, data_number) {
  let color = 'black';
  let field = 'none';
  let type = 'text';
  let cont = 'string';

  if (data_content === null) {
    color = 'grey';
    field = 'none';
    type = 'text';
    cont = 'null';
  }

  else if (typeof data_content === 'boolean') {
    color = 'unique-color';
    field = 'bool';
    type = 'checkbox';
    cont = 'bool';
  }

  else if (typeof data_content === 'number') {
    color = 'red';
    field = 'input';
    type = 'number';
    cont = 'number';
  }

  else if (typeof data_content === 'string') {
    color = 'green';
    field = 'input';
    type = 'text';
    cont = 'string';
  }

  else if (typeof data_content === 'object') {
    color = 'orange';
    field = 'textarea';
    type = 'textarea';
    cont = 'object';
  }

  // Need color, field

  if (field == "textarea") {
    field = rctp.clone();
    field.addClass(color);
    field.attr("data-savetype", cont);
    field.find('._a').text(data_number);
    field.find('._b').text(JSON.stringify(data_content));
  }

  else if (field == "none") {
    field = rcnp.clone();
    field.attr("data-savetype", cont);
    field.addClass(color);
    field.find('._a').text(data_number);
  }

  else if (field == "input") {
    field = rcip.clone();
    field.attr("data-savetype", cont);
    field.addClass(color);
    field.find('._a').text(data_number);
    field.find('._b').attr('type',type);
    field.find('._b').attr('value',data_content);
  }

  else if (field == "bool") {
    field = rcbp.clone();
    field.attr("data-savetype", cont);
    field.addClass(color);
    field.find('._a').text(data_number);
    if (data_content) {
      field.find('._b').attr('checked',true);
    }
  }

  return field;
}

function show_result(data) {
  if (data['hits'] >= 300 || data['hits_field'] >= 500) {
    c = confirm("There are "+data['hits']+" results with "+data['hits_field']+" fields, sure you want to display all?");
    if (!c) {
      return ;
    }
  }

  rrp = $('#result_row_phantom');

  rcip = $('#result_col_input_phantom > div');
  rcbp = $('#result_col_bool_phantom > div');
  rcnp = $('#result_col_none_phantom > div');
  rctp = $('#result_col_textarea_phantom > div');

  $('#result_place').html("");

  if (data.data.length == 0) {
    $('#result_place').html("<h1>No Entrys</h1>");
  }

  for (var number in data.data) {
    entry = data.data[number];
    rrp_c = rrp.clone();

    //id extra case

    rcip_c = rcip.clone();
    rcip_c.attr('data-savetype', "id");
    rcip_c.addClass('primary-color');
    rcip_c.find('._a').text('id');
    rcip_c.find('._b').attr('value',entry['id']);
    rcip_c.find('._b').attr('disabled', true);

    rrp_c.children('.inner').append(rcip_c);
    delete entry['id'];

    // everything else
    for (var data_number in entry) {
      data_content = entry[data_number];

      field = get_right_col_type(data_content, data_number);

      rrp_c.children('.inner').append(field);

    }
    $('#result_place').append(rrp_c.html());
  }

}

function get_result(container, limit=null, offset=null) {
  var name = get_origen(container).replace("DATABASE/", "");
  $(".last_selected_container").val(name);

  if (limit == null) {
    limit = 10;
  }

  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'select';
  r['limit'] = limit;
  r['offset'] = 0;
  r['of'] = name;


  $.post('/', JSON.stringify(r))
    .fail(
      function (data) {
        if (data.responseJSON.status == 'error') {
          show_error(data.responseJSON)
          return ;
        }
      })
    .done(
      function (data) {
        show_result(data);
      }
    )

}

function show_reload(name) {
  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'select';
  r['of'] = name;
  r['limit'] = 10;
  r['offset'] = 0;

  $.post('/', JSON.stringify(r))
    .fail(
      function (data) {
        if (data.responseJSON.status == 'error') {
          show_error(data.responseJSON)
          return ;
        }
      })
    .done(
      function (data) {
        show_result(data);
      }
    )

}

function format_container(folder, name=null, folder_before="") {
  var d = $('#sc_phantom > div').clone();
  d.children('div').children('button').children('.name_space').text(name);

  for (var thing in folder.supercontainer) {
    obj = folder.supercontainer[thing];
    let n = format_container(obj, name=thing, ""+folder_before+thing+"/");
    d.children('div').children('.sc_inner').append(n);
  }

  for (var thing in folder.container) {
    name = folder.container[thing];
    let a =  $('#c_phantom > div').clone();
    a.children('div').children('button').children('.name_space').text(name);
    d.children('div').children('.sc_inner').append(a);
  }

  return d;

}

/* DB utils */

function shutdown() {
  var c = confirm('Sure you want to shutdown the PhaazeDB?');
  if (!c) {return ;}

  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'shutdown';

  $.post('/', JSON.stringify(r))
  .fail(
    function (data) {
    if (data.responseJSON.status == 'error') {
      show_error(data.responseJSON)
      return ;
    }
  })
  .done(
    function (data) {
      console.log(data);
    if (data.status == 'success') {
      show_message("PhaazeDB is shutting down.");
      setTimeout(function () {
        $('html').html('<head></head><body style="background:#212529;"><h1 style="color:white;font-size: 5em;text-align: center;margin-top: 30vh;">PhaazeDB Offline</h1></body>')
      }, 5000);
    }
  })

}

async function add_container(button_obj) {

  var upper_container = await get_origen(button_obj);
  var new_name = prompt("Please enter the container name\n\n"+upper_container+"[Container]", "");
  if (new_name == null) {return ;}

  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'create';
  r['name'] = upper_container.replace('DATABASE/', "")+new_name;


  $.post('/', JSON.stringify(r), function () {
    load_container(no_msg=true);
    show_message('Successfull created: '+upper_container.replace('DATABASE/', "")+new_name);
  })

}

async function remove_container(button_obj) {
  var e = await get_origen($(button_obj).closest('button'));

  var a = confirm("Sure you want to drop the container: `"+e+"` ?" );
  if (!a) {
    return ;
  }

  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'drop';
  r['name'] = e.replace('DATABASE/', "");

  $.post('/', JSON.stringify(r), function () {
    show_message('Successfull dropped: '+e.replace('DATABASE/', ""));
    load_container();
  })
}

async function show_footer(id) {
  if (block_footer) { return ;}
  block_footer = true;

  if (id == last_opened_footer) {
    $('#'+id).collapse('hide');
    last_opened_footer = "";
    await sleep(500);
    block_footer = false;
  }
  else if (last_opened_footer == "") {
    $('#'+id).collapse('show');
    last_opened_footer = id;
    await sleep(500);
    block_footer = false;
  }
  else {
    $('.multi_use_footer').find('.collapse').collapse('hide');
    await sleep(500);
    $('#'+id).collapse('show');
    await sleep(500);
    last_opened_footer = id;
    block_footer = false;
  }


}

/* DB functions */

function load_container() {
  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'show';


  $.post('/', JSON.stringify(r))
    .done(
      function (data) {
        $('#container_list').html('');
        var cont = format_container(data.data, name="DATABASE");

        $('#container_list').append(cont.html());

        }
      )

    .fail(
      function (data) {
      if (data.responseJSON.status == 'error') {
        show_error('Login failed.')
        show_error(data.responseJSON)
        return ;
      }
    })


}

function submit_insert() {

  var new_fields = $('#insert_fields > .entry');

  var r = {};
  var content = {};

  for (var field of new_fields) {

    field_key = $(field).find('.key').val().trim();
    field_value = $(field).find('.value').val().trim();
    field_type = $(field).find('.selected_type').val().trim();

    if (field_type == "string") {
      field_value = String(field_value);
    }
    else if (field_type == "bool") {
      field_value = Boolean(field_value);
    }
    else if (field_type == "number") {
      field_value = Number(field_value);
    }
    else if (field_type == "object") {
      try {
        field_value = JSON.parse(field_value);
      } catch (e) {
        show_error('Invalid Content Type');
        return ;
      }
    }
    else if (field_type == "null") {
      field_value = null;
    }

    // add to content
    content[field_key] = field_value;

  }

  r['token'] = $('#db_token').val();
  r['action'] = 'insert';
  r['into'] = $('#insert_field').val();
  r['content'] = content;

  $.post('/', JSON.stringify(r))
  .done(function (data) {
    show_message('Data Successfull inserted.');
    show_reload( $('#insert_field').val() );
    $('#insert_fields').html('');
  })
  .fail(function (data) {
    show_error(JSON.stringify(data.responseJSON))
  })
}

function submit_delete() {

  var where = $('#delete_where').val();
  if (where == "") {
    var c = confirm('WARNING: Delete where statement is empty.\nThis will delete everything in the seleted container.\n\nAre you sure?');
    if (!c) {
      return ;
    }
  }

  var r = {};

  r['token'] = $('#db_token').val();
  r['action'] = 'delete';
  r['of'] = $('#delete_field').val();
  r['where'] = where;

  $.post('/', JSON.stringify(r))
  .done(function (data) {
    show_message('Successfull deleted '+data['hits']+' entry(s)');
    show_reload( $('#delete_field').val() );
    $('#delete_where').val('');
  })
  .fail(function (data) {
    show_error(JSON.stringify(data.responseJSON))
  })

}

function submit_update() {

  var where = $('#update_where').val();
  if (where == "") {
    var c = confirm('WARNING: Update where statement is empty.\nThis will update all entrys in the seleted container.\n\nAre you sure?');
    if (!c) {
      return ;
    }
  }

  var update = $('#update_fields > .entry');
  var content = {};

  for (var field of update) {

    field_key = $(field).find('.key').val().trim();
    field_value = $(field).find('.value').val().trim();
    field_type = $(field).find('.selected_type').val().trim();

    if (field_type == "string") {
      field_value = String(field_value);
    }
    else if (field_type == "bool") {
      field_value = Boolean(field_value);
    }
    else if (field_type == "number") {
      field_value = Number(field_value);
    }
    else if (field_type == "object") {
      try {
        field_value = JSON.parse(field_value);
      } catch (e) {
        show_error('Invalid Content Type');
        return ;
      }
    }
    else if (field_type == "null") {
      field_value = null;
    }

    // add to content
    content[field_key] = field_value;

  }

  var r = {};

  r['token'] = $('#db_token').val();
  r['action'] = 'update';
  r['of'] = $('#update_field').val();
  r['content'] = content;
  r['where'] = where;

  $.post('/', JSON.stringify(r))
  .done(function (data) {
    show_message('Successfull updated '+data['hits']+' entry(s)');
    // show_reload( $('#update_field').val() );
    $('#update_where').val('');
  })
  .fail(function (data) {
    console.log('fail');
    console.log(data);
    show_error(JSON.stringify(data.responseJSON))
  })

}

function submit_select() {
  var where = $('#select_where').val();

  var r = {};

  r['token'] = $('#db_token').val();
  r['action'] = 'select';
  r['of'] = $('#select_field').val();
  r['where'] = where;
  var fields = $('#select_cols').val();
  if (fields != "") {
    fields = fields.split(";");
    fields.push('id')
    r['fields'] = fields;
  }
  r['limit'] = $('#select_limit').val();
  r['offset'] = $('#select_offset').val();

  $.post('/', JSON.stringify(r))
  .done(function (data) {
    show_message('Show: '+data['hits']+' entry(s) | In Container: '+data['total']);
    show_result(data);
    $(".last_selected_container").val($('#select_field').val());
  })
  .fail(function (data) {
    show_error(JSON.stringify(data.responseJSON))
  })


}

/* Field utils */

function edit_field_type(obj) {
  $('.selected_col').removeClass('selected_col');
  $(obj).closest('.value_field').addClass('selected_col');
}

function change_input_field(obj, type) {
  $(obj).removeClass("green red orange grey unique-color");
  if (type == "null") {
    $(obj).addClass('grey');
    $(obj).parent().parent().find('input.value').attr('type', 'hidden');
  }
  if (type == "string") {
    $(obj).addClass('green');
    $(obj).parent().parent().find('input.value').attr('type', "text");
   }
  if (type == "number") {
    $(obj).addClass('red');
    $(obj).parent().parent().find('input.value').attr('type', "number");
  }
  if (type == "object") {
    $(obj).addClass('orange');
    $(obj).parent().parent().find('input.value').attr('type', "text");
  }
  if (type == "bool") {
    $(obj).addClass('unique-color');
    $(obj).parent().parent().find('input.value').attr('type', 'text');
 }

}

function change_col_type(type) {

  var field = $('.selected_col');
  if (field.length != 1) {
    return ;
  }
  field_name = field.find('._a').text();
  new_field = get_right_col_type(type, field_name);
  new_field.addClass('selected_col');

  field.replaceWith(new_field);

}

function save_col() {
  var field = $('.selected_col');
  if (field.length != 1) {
    return ;
  }

  field_id = field.closest('.inner').find('[data-savetype=id]').find('._b').val();
  field_name = field.find('._a').text();
  field_value = field.find('._b').val();

  field_type = field.attr("data-savetype");

  // convert
  if (field_type == "string") {
    field_value = String(field_value);
  }
  else if (field_type == "bool") {
    field_value = field.find('._b').prop( "checked" );
  }
  else if (field_type == "number") {
    field_value = Number(field_value);
  }
  else if (field_type == "object") {
    try {
      field_value = JSON.parse(field_value);
    } catch (e) {
      show_error('Invalid Content Type');
      return ;
    }
  }
  else if (field_type == "null") {
    field_value = null;
  }

  let content = {};
  content[field_name] = field_value;

  let r = {};
  r['token'] = $('#db_token').val();
  r['action'] = "update";
  r['of'] = $('#current_view_container').val();
  r['action'] = "update";
  r['content'] = content;
  r['where'] = "data['id'] == "+field_id;

  $.post('/', JSON.stringify(r))
    .done(function () {
      show_message('Successfull updated field');
    });


}