function delete_(r, preview=false) {
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
    $('input[name=where]').val(r.where);
    $('input[name=limit]').val(r.limit);
    $('input[name=offset]').val(r.offset);
    $('#current_container').text(last_selected_container);
    $('#total_entrys').text(data.total);
    if (preview == false) {
      display_message( {content:"Delete: Removed: "+data.hits+" entry(s)", color:"#ccc"} );
    }
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
  if ($('#delete_modal').is(':visible')) {
    $('#delete_modal').collapse('hide');
    return;
  }
  $('#modal-space > .collapse').collapse('hide');
  $('#delete_modal').find('[name=of]').val( last_selected_container );
  $('#delete_modal').find('.need_correction').removeClass('need_correction');
  $('#delete_modal').collapse('show');
}

function modal_delete() {
  let col_modal = $('#delete_modal');
  let r = {};

  r['of'] = col_modal.find('[name=of]').val();
  r['where'] = col_modal.find('[name=where]').val();
  r['limit'] = col_modal.find('[name=limit]').val();
  r['offset'] = col_modal.find('[name=offset]').val();

  return delete_(r);
}

