function delete_(r) {
  if (r == null) {
    r = {};
  }

  let request = {
    "action": "delete",
    "of": r['of'],
    "token": $('#db_token').val()
  };
  if (r.limit != null) {
    request['limit'] = r.limit;
  }
  if (r.offset != null) {
    request['offset'] = r.offset;
  }
  if (r.where != null) {
    request['where'] = r.where;
  }
  $.post("/", request)
  .done(function (data) {
    last_selected_container = request["of"];
    $('input[name=into], input[name=of]').val(last_selected_container);
    $('input[name=where]').val(r.where);
    $('input[name=limit]').val(r.limit);
    $('input[name=offset]').val(r.offset);
    $('#current_container').text(last_selected_container);
    $('#total_entrys').text(data.total);
    $('#delete_modal').modal('hide');
    display_message( {content:"Delete: Removed: "+data.hits+" entry(s)", color:"#ccc"} );
  })
  .fail(function (data) {
    data = data.responseJSON ? data.responseJSON : {};
    if (data.status == "error") {
      if (data.msg == "unauthorised") {
        display_message( {content:"Unauthorised, please check token", color:"#fa3"} );
        return notify_incorrect_token();
      }
      return display_message( {content:data.msg, color:"#fa3"} );
    } else {
      return display_message( {content:"Unknown Server Error", color:"#f00"} );
    }
  })
}

function start_delete() {
  $('#delete_modal').find('[name=into]').val( last_selected_container )
  $('#delete_modal').find('.need_correction').removeClass('need_correction');
  $('#delete_modal').modal('show');
}

function modal_delete() {
  let col_modal = $('#delete_modal');
  let r = {};
  let table_name = col_modal.find('[name=of]').val();
  if (table_name == "") {
    col_modal.find('[name=of]').addClass('need_correction').focus();
    return ;
  }

  r['of'] = table_name;
  r['where'] = col_modal.find('[name=where]').val();
  r['limit'] = col_modal.find('[name=limit]').val();
  r['offset'] = col_modal.find('[name=offset]').val();

  let t = false;
  if (r.where == "" || r.where == null) {
    t = confirm("WARNING\nYour 'where' field is empty. that will erase all entrys if not hold by\nlimit or offset.\n\nSure you wanna do this?");
  }
  if (t) {
    return delete_(r);
  }
}

