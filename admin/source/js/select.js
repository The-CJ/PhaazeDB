function select(r, preview=false) {
  if (r == null) {
    r = {};
  }

  let request = {
    "action": "select",
    "of": r['of'],
    "limit": r['limit'],
    "token": $('#db_token').val()
  };
  $.get("/", request)
  .done(function (data) {
    last_selected_container = request["of"];
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
  let ob = $('<div class="result_col typeof_bool">x</div>');
  return ob;
}
function generate_object(key, value) {
  let ob = $('<div class="result_col typeof_object">x</div>');
  return ob;
}