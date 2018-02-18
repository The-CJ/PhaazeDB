$('document').ready(
  function () {
    //load_container();
  }
)

function format_container(folder, name=null) {
  console.log(folder);
  let d = $('#sc_phantom').clone().removeAttr('hidden');

  //must work with id
  d.find('.name_space').text(name);


  for (var thing in folder.supercontainer) {
    obj = folder.supercontainer[thing];
    let n = format_container(obj, name=thing);
    d.find('.sc_inner').append(n);
  }

  for (var thing in folder.container) {
    name = folder.container[thing];
    let a =  $('#c_phantom').clone().removeAttr('hidden');
    a.find('button').text(name);
    d.find('.sc_inner').append(a)
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