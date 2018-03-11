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

function show_result(data) {
  rrp = $('#result_row_phantom');

  rcip = $('#result_col_input_phantom > div');
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
    rcip_c.addClass('primary-color');
    rcip_c.find('._a').text('id');
    rcip_c.find('._b').attr('value',entry['id']);

    rrp_c.children('.inner').append(rcip_c);
    delete entry['id'];

    // everything else
    for (var data_number in entry) {
      data_content = entry[data_number];

      if (typeof data_content === 'object') {
        rctp_c = rctp.clone();
        rctp_c.addClass('orange');
        rctp_c.find('._a').text(data_number);
        rctp_c.find('._b').text(JSON.stringify(data_content));

        rrp_c.children('.inner').append(rctp_c);
      }

      else if (typeof data_content === 'number') {
        var div_color = "pink";
      }

      else if (typeof data_content === 'string') {
        var div_color = "green";
      }

      else {
        var div_color = "grey";
      }

      if (typeof data_content !== 'object') {
        rcip_c = rcip.clone();
        rcip_c.addClass(div_color);
        rcip_c.find('._a').text(data_number);
        rcip_c.find('._b').attr('value',data_content);

        rrp_c.children('.inner').append(rcip_c);
      }

    }
    $('#result_place').append(rrp_c.html());
  }


}

function get_result(container, limit=null, offset=null) {
  var name = get_origen(container).replace("DATABASE/", "");
  $(".last_selected_container").val(name);

  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'select';
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
    load_container(no_msg=true);
    show_message('Successfull dropped: '+e.replace('DATABASE/', ""));
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

function load_container(no_msg=false) {
  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'show';


  $.post('/', JSON.stringify(r))
    .done(
      function (data) {
        $('#container_list').html('');
        var cont = format_container(data.data, name="DATABASE");

        $('#container_list').append(cont.html());

        if (!no_msg) {
          show_message('Successfull login');
        }

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

    content[$(field).find('.key').val().trim()] = $(field).find('.value').val().trim();

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
    show_message('Successfull deleted '+data['hits']+' entrys');
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

    content[$(field).find('.key').val().trim()] = $(field).find('.value').val().trim();

  }

  var r = {};

  r['token'] = $('#db_token').val();
  r['action'] = 'update';
  r['of'] = $('#update_field').val();
  r['content'] = content;
  r['where'] = where;

  $.post('/', JSON.stringify(r))
  .done(function (data) {
    console.log('success');
    console.log(data);
    show_message('Successfull updated '+data['hits']+' entrys');
    show_reload( $('#update_field').val() );
    $('#update_where').val('');
  })
  .fail(function (data) {
    console.log('fail');
    console.log(data);
    show_error(JSON.stringify(data.responseJSON))
  })

}