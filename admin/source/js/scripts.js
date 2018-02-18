$('document').ready(
  function () {
    //load_container();
  }
)

function format_container(folder, name=null) {
  //let d = $('#sc_phantom > div').clone();

  var d = $('#sc_phantom > div').clone();
  d.children('div').children('button').children('.name_space').text(name);

  for (var thing in folder.supercontainer) {
    obj = folder.supercontainer[thing];
    let n = format_container(obj, name=thing);
    d.children('div').children('.sc_inner').append(n);
  }

  for (var thing in folder.container) {
    name = folder.container[thing];
    let a =  $('#c_phantom > div').clone();
    a.children('div').children('button').text(name);
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
      console.log(data);
      if (data.responseJSON.status == 'error') {
        console.log('error');
        return ;
      }
    })


}