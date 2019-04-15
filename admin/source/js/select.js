class Select {
  constructor() {
    this.last = "";
  }

  showFieldSelect() {
    _("[modal=select] [select-fields-btn]").hide();
    _("[modal=select] [select-fields]").show();
  }

  start() {
    let request = {};

    request["of"] = _("[modal='select'] [name=of]").value();

    if (isEmpty(request['of'])) { field.addClass("need-correction"); return; }

    request["where"] = _("[modal='select'] [name=where]").value();
    request["limit"] = _("[modal='select'] [name=limit]").value();
    request["offset"] = _("[modal='select'] [name=offset]").value();
    request["fields"] = _("[modal='select'] [name=fields]").value();

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
    if ( !isEmpty(request['fields']) ) { r['fields'] = request['fields'].split("|"); }

    this.last = request['of'];

    var SelectO = this;
    _.post("/", JSON.stringify(r))
    .done(function (data) {
      DynamicURL.set('container', request['of'], false);
      DynamicURL.set('limit', request['limit'], false);
      DynamicURL.set('offset', request['offset'], false);
      DynamicURL.set('where', request['where'], false);
      DynamicURL.set('fields', request['fields'], false);
      DynamicURL.update();

      _('#current_container').text(request['of']);
      _('[name=of], [name=into], [name=container]').value(request['of']);
      _('#total_entrys').text(data.total);
      Edit.stopEdit();

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
      // id first, if there
      if (!isEmpty(entry['id'])) {
        row.append( Template.generateResultColID(entry['id']) );
        delete entry['id'];
      }

      let sorted_keys = Object.keys(entry).sort(function(a,b){
        a=a.toLowerCase();b=b.toLowerCase();
        return (a<b) ? -1 : (a>b) ? 1 : 0;
      });

      for (var key of sorted_keys) {
        let value = entry[key];
        if (value === null) { row.append(Template.generateResultColNone(key)) }
        else if (typeof value == "string") { row.append(Template.generateResultColString(key, value)) }
        else if (typeof value == "number") { row.append(Template.generateResultColNumber(key, value)) }
        else if (typeof value == "boolean") { row.append(Template.generateResultColBool(key, value)) }
        else if (typeof value == "object") { row.append(Template.generateResultColObject(key, value)) }
        else { row.append(Template.generateResultColUnknown(key, value)) }
      }
      result_space.append(row);
    }
    // add edit event listener
    _("#result_space .result-col").on("dblclick", function () { Edit.selectCol(this) });
  }
}
Select = new Select();
