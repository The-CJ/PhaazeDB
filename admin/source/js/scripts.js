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

function get_result(container, limit=null, offset=null) {
  $(".last_selected_container").val(container);

  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'select';
  r['of'] = container;


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
    a.children('div').children('button').text(folder_before+name);
    d.children('div').children('.sc_inner').append(a);
  }

  return d;

}

function load_container() {
  var r = {};
  r['token'] = $('#db_token').val();
  r['action'] = 'show';


  $.post('/', JSON.stringify(r))
    .done(
      function (data) {
        $('#container_list').html('');
        var cont = format_container(data.data, name="DB");

        $('#container_list').append(cont.html());

        show_message('Successfull login');
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
