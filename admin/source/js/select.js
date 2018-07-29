function select(r, preview=false) {
  if (r == null) {
    r = {};
  }

  let request = {
    "action": "select",
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
  $.get("/", request)
  .done(function (data) {
    last_selected_container = request["of"];
    $('input[name=into], input[name=of]').val(last_selected_container);
    $('input[name=where]').val(r.where);
    $('#current_container').text(last_selected_container);
    $('#total_entrys').text(data.total);
    if (preview == false) {
      display_message( {content:"Select: Returned: "+data.hits+" entry(s)", color:"#ccc"} );
    }
    if (data.hits == 0) {
      $('#result_space').html('<div class="center-item-row" style="height:100%;"><div class="no-results"></div></div>');
      return ;
    }
    return fill_entrys(data.data);
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

function start_select() {
  if ($('#select_modal').is(':visible')) {
    $('#select_modal').collapse('hide');
    return ;
  }
  $('#modal-space > .collapse').collapse('hide');
  $('#select_modal').find('[name=of]').val( last_selected_container );
  $('#select_modal').find('.need_correction').removeClass('need_correction');
  $('#select_modal').collapse('show');
}

function modal_select() {
  let col_modal = $('#select_modal');
  let r = {};

  r['of'] = col_modal.find('[name=of]').val();
  r['where'] = col_modal.find('[name=where]').val();
  r['limit'] = col_modal.find('[name=limit]').val();
  r['offset'] = col_modal.find('[name=offset]').val();

  return select(r);
}

function preview(btn) {
  btn = $(btn);
  let table_name = btn.attr('path');
  return select( {"of":table_name, "limit":10}, true );
}

function fill_entrys(data_list) {
  var result_space = $('#result_space').html('');
  for (entry of data_list) {
    var row = $('<div class="center-item-row result_row">');
    let id_col = generate_id(entry['id']);
    row.append(id_col);
    delete entry['id'];

    let sorted_entry = {};
    Object.keys(entry).sort(function(a, b) {
      let keya = a.toLowerCase();
      let keyb = b.toLowerCase();
      return (keya < keyb) ? -1 : (keya > keyb) ? 1 : 0;
    }).forEach(function(key) { sorted_entry[key] = entry[key] });
    for (entry_key in sorted_entry) {

      entry_value = sorted_entry[entry_key];
      let col_object = null;

      if (entry_value == null) {
        col_object = generate_none(entry_key);
      }
      else if (typeof entry_value == "string") {
        col_object = generate_string(entry_key, entry_value);
      }
      else if (typeof entry_value == "number") {
        col_object = generate_number(entry_key, entry_value);
      }
      else if (typeof entry_value == "boolean") {
        col_object = generate_bool(entry_key, entry_value);
      }
      else if (typeof entry_value == "object") {
        col_object = generate_object(entry_key, entry_value);
      }
      if (col_object != null) {
        row.append(col_object);
      }
    }
    result_space.append(row);
  }

}

function generate_id(id) {
  let ob = $('<div class="result_col typeof_id"></div>');
  ob.append( $('<div class="key">').text("id") );
  ob.append( $('<input readonly type="number">').val(id) );
  return ob;
}
function generate_none(key) {
  let ob = $('<div class="result_col typeof_none"></div>');
  ob.append( $('<div class="key">').text(key) );
  ob.append( $('<input disabled type="text">').val('None/null') );
  return ob;
}
function generate_string(key, value) {
  let ob = $('<div class="result_col typeof_string"></div>');
  ob.append( $('<div class="key">').text(key) );
  ob.append( $('<input type="text">').val(value) );
  return ob;
}
function generate_number(key, value) {
  let ob = $('<div class="result_col typeof_number"></div>');
  ob.append( $('<div class="key">').text(key) );
  ob.append( $('<input type="number">').val(value) );
  return ob;
}
function generate_bool(key, value) {
  let ob = $('<div class="result_col typeof_bool"></div>');
  ob.append( $('<div class="key">').text(key) );
  let s = $('<div class="switch">');
  s.attr('state', String(value));
  s.attr('onclick', 'if ($(this).attr("state") == "true") {$(this).attr("state", "false")} else {$(this).attr("state", "true")}');
  ob.append(s);
  return ob;
}
function generate_object(key, value) {
  let ob = $('<div class="result_col typeof_object"></div>');
  ob.append( $('<div class="key">').text(key) );
  ob.append( $('<textarea>').val(JSON.stringify(value)) );
  return ob;
}