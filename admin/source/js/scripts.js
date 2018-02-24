$('document').ready(
  function () {
    //load_container();
  }
)

function show_error(error) {

  var e = $('#error_phantom').html();

  var i = Math.floor(Math.random() * 10000);

  e = e.replace('{msg}', JSON.stringify(error));
  e = e.replace('{id}', i);

  $('#msg_display').append(e);
  setTimeout(function () {
    $('#msg_display > #'+i).remove();
  }, 5500);
}

function show_message(message) {

  var e = $('#message_phantom').html();

  var i = Math.floor(Math.random() * 10000);

  e = e.replace('{msg}', JSON.stringify(error));
  e = e.replace('{id}', i);

  $('#msg_display').append(e);
  setTimeout(function () {
    $('#msg_display > #'+i).remove();
  }, 5500);
}

function get_result(container, limit=null, offset=null) {
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
        rcp = $('#result_col_phantom > div');
        rcop = $('#result_col_obj_phantom > div');
        rip = $('#result_id_phantom > div');
        $('#result_place').html("");

        for (var number in data.data) {
          entry = data.data[number];

          rrp_c = rrp.clone();

          rip_c = rip.clone();
          rip_c.children('._a').text('id');
          rip_c.children('._b').attr('value',entry['id']);

          rrp_c.children('.inner').append(rip_c);
          delete entry['id'];

          for (var data_number in entry) {
            data_content = entry[data_number];

            if (typeof data_content === 'object') {
              rcop_c = rcop.clone();
              rcop_c.children('._a').text(data_number);
              rcop_c.children('._b').text(JSON.stringify(data_content));

              rrp_c.children('.inner').append(rcop_c);

            } else {
              rcp_c = rcp.clone();
              rcp_c.children('._a').text(data_number);
              rcp_c.children('._b').attr('value',data_content);

              rrp_c.children('.inner').append(rcp_c);
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
        }
      )

    .fail(
      function (data) {
      if (data.responseJSON.status == 'error') {
        show_error(data.responseJSON)
        return ;
      }
    })


}