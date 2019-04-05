function fill_entrys(data_list) {
  var result_space = $('#result_space').html('');
  for (entry of data_list) {
    var row = $('<div class="center-item-row result-row">');
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

function generate_none(key) {
  let ob = $('<div class="result_col typeof_none" ondblclick="edit_select(this)"></div>');
  ob.attr('object_type', 'none');
  ob.append( $('<div class="key">').text(key) );
  ob.append( $('<input disabled type="text">').val('None/null') );
  return ob;
}
function generate_string(key, value) {
  let ob = $('<div class="result_col typeof_string" ondblclick="edit_select(this)"></div>');
  ob.attr('object_type', 'string');
  ob.append( $('<div class="key">').text(key) );
  ob.append( $('<input type="text">').val(value) );
  return ob;
}
function generate_number(key, value) {
  let ob = $('<div class="result_col typeof_number" ondblclick="edit_select(this)"></div>');
  ob.attr('object_type', 'number');
  ob.append( $('<div class="key">').text(key) );
  ob.append( $('<input type="number">').val(value) );
  return ob;
}
function generate_bool(key, value) {
  let ob = $('<div class="result_col typeof_bool" ondblclick="edit_select(this)"></div>');
  ob.attr('object_type', 'bool');
  ob.append( $('<div class="key">').text(key) );
  let s = $('<div class="switch">');
  s.attr('state', String(value));
  s.attr('onclick', 'if ($(this).attr("state") == "true") {$(this).attr("state", "false")} else {$(this).attr("state", "true")}');
  ob.append(s);
  return ob;
}
function generate_object(key, value) {
  let ob = $('<div class="result_col typeof_object" ondblclick="edit_select(this)"></div>');
  ob.attr('object_type', 'object');
  ob.append( $('<div class="key">').text(key) );
  ob.append( $('<textarea>').val(JSON.stringify(value)) );
  return ob;
}
function generate_remove(key) {
  let ob = $('<div class="result_col typeof_remove" ondblclick="edit_select(this)"></div>');
  ob.attr('object_type', 'remove');
  ob.append( $('<div class="key">').text(key) );
  ob.append( $('<input disabled type="text">').val('Remove') );
  return ob;
}

class Select {
  constructor() {
    this.last = "";
  }

  start() {
    let request = {};

    request["of"] = _("[modal='select'] [name=of]").value();
    request["where"] = _("[modal='select'] [name=where]").value();
    request["limit"] = _("[modal='select'] [name=limit]").value();
    request["offset"] = _("[modal='select'] [name=offset]").value();

    return this.execute(request);
  }

  preview(btn) {
    let container_name = _(btn).attribute('path');
    return this.execute({"of":container_name, "limit":10}, true);
  }

  execute(request, preview=false) {
    if (request == null) { request = {}; }
    let r = {
      "action": "select",
      "token": _('#db_token').value(),
      "of": request['of']
    };
    if ( !isEmpty(request['limit']) ) { r['limit'] = request['limit']; }
    if ( !isEmpty(request['offset']) ) { r['offset'] = request['offset']; }
    if ( !isEmpty(request['where']) ) { r['where'] = request['where']; }

    this.last = request['of'];

    var SelectO = this;
    _.post("/", JSON.stringify(r))
    .done(function (data) {
      DynamicURL.set('container', request['of'], false);
      DynamicURL.set('limit', request['limit'], false);
      DynamicURL.set('offset', request['offset'], false);
      DynamicURL.set('where', request['where'], false);
      DynamicURL.update();

      _('#current_container').text(request['of']);
      _('#total_entrys').text(data.total);

      if (preview == false) {
        Display.message( {content:"Select: Returned: "+data.hits+" entry(s)", color:Display.color_neutral} );
      }
      if (data.hits == 0) {
        _('#result_space').html('<div class="center-item-row" style="height:100%;"><div class="no-results"></div></div>');
        return ;
      }
      return SelectO.build(data.data);
    })
    .fail(function (data) {
      if (data.status == "error") {
        if (data.msg == "unauthorised") {
          return Display.message( {content:"Unauthorised, please check token", color:Display.color_warn} );
        }
        return Display.message( {content:data.msg, color:Display.color_fail} );
      }
      else {
        return Display.message( {content:"Unknown Server Error", color:Display.color_fail} );
      }
    })

  }

  build(data) {
    var result_space = _('#result_space').html('');
    for (var entry of data) {
      var row = _.create('<div class="center-item-row result-row">');
      row.append( Template.generateResultColID(entry['id']) );


      result_space.append(row);
    }
    console.log(data);
  }
}
Select = new Select();
