// because JQuery is to huge, i want a light wight framework, AND i have a lot of freetime, so i made my own

function _(query) {
  return new PhaazeQuery(query);
}

_.get = function (url, parameter) {
  if (typeof url == "undefined") {throw "1 arguments 'url' required"}
  return new PhaazeRequest("GET", url, parameter);
}

_.post = function (url, parameter) {
  if (typeof url == "undefined") {throw "1 arguments 'url' required"}
  return new PhaazeRequest("POST", url, parameter);
}

_.create = function (DOMstring) {
  var html = new DOMParser().parseFromString(DOMstring, 'text/html');
  var PQ = new PhaazeQuery()
  PQ.result = [html.body.firstChild];
  return PQ;
}

class PhaazeRequest {
  constructor(method, url, parameter) {
    this.method = method;
    this.url = url;
    this.parameter = parameter;
    this.status = null;
    this.request = null;
    this.data = null;

    this.functions_done = [];
    this.functions_fail = [];
    this.functions_always = [];

    this.call();
  }
  done(func) {
    if (typeof func == "undefined") { throw "1 argument 'func' required" }
    if (this.status === null) { this.functions_done.push(func); return this; }
    if (200 <= this.status && this.status <= 299) { return this.always(func) }
    else {return this}
  }
  fail(func) {
    if (typeof func == "undefined") { throw "1 argument 'func' required" }
    if (this.status === null) { this.functions_fail.push(func); return this; }
    if (400 <= this.status) { return this.always(func) }
    else {return this}
  }
  always(func) {
    if (typeof func == "undefined") { throw "1 argument 'func' required" }
    if (this.status === null) { this.functions_always.push(func); return this; }

    var data = [this.getData(), this.request, this];
    (async function(){func(data[0], data[1], data[2])})()
    return this;
  }
  call() {
    var param = null;

    // paramether convertion
    if (typeof this.parameter == "undefined") { /*nothing*/ }
    else if (typeof this.parameter == "string") {
        param = this.parameter;
    }
    else if (typeof this.parameter == "object") {
      // get
      if (this.method == "GET") {
        let li = []
        for (var key in this.parameter) {
          li.push( encodeURIComponent(key) + '=' + encodeURIComponent(this.parameter[key]) );
        }
        param = li.join("&");
      }
      // post and everything else
      else {
        param = new FormData();
        for (var key in this.parameter) { param.append(key, this.parameter[key]); }
      }
    }

    var this2 = this;
    var r = new XMLHttpRequest();

    // call back function
    r.onload = function () {
      this2.request = r;
      this2.status = r.status;
      // execute stored call backs
      while (1) {
        let fd = this2.functions_done.shift();
        if (fd) { this2.done(fd); } else { break; }
      }
      while (1) {
        let ff = this2.functions_fail.shift();
        if (ff) { this2.fail(ff); } else { break; }
      }
      while (1) {
        let fa = this2.functions_always.shift();
        if (fa) { this2.always(fa); } else { break; }
      }
    }

    if (this.method == "GET") {
      let firstArg = this.url.includes("?") ? "&" : "?"
      r.open( this.method, param ? (this.url + firstArg + param) : (this.url) );
      r.send();
    }
    else {
      r.open(this.method, this.url);
      r.send(param);
    }

  }
  getData() {
    if (this.data !== null) { return this.data; }
    else {
      var request_data;
      if (this.request.getResponseHeader("Content-Type") == "Application/json") {
        try { request_data = JSON.parse(this.request.response); }
        catch (e) { request_data = this.request.response; }
      }
      else { request_data = this.request.response; }
      this.data = request_data;
      return request_data
    }
  }

}

class PhaazeQuery {
  // yeah i actully name it PhaazeQuery, fight me REEEEEEEEEE
  constructor(query) {
    if (query instanceof HTMLElement) {
      this.result = [query];
    }
    else {
      this.result = document.querySelectorAll(query);
    }
  }

  text(string) {
    let string_result = [];
    let mode = 0; // set mode
    if (typeof string == "undefined") {
      mode = 1; //get mode
    }
    for (let node of this.result) {
      if (mode) {
        string_result.push(node.innerText);
      } else {
        node.innerText = string;
      }
    }

    if (mode) {
      if (string_result.length == 1) { return string_result[0]; }
      else if (string_result.length == 0) { return null; }
      else { return string_result; }
    }
    return this;
  }

  value(val) {
    let val_result = [];
    let mode = 0; // set mode
    if (typeof val == "undefined") {
      mode = 1; //get mode
    }
    for (let node of this.result) {
      if (mode) {
        val_result.push(node.value);
      } else {
        node.value = val;
      }
    }

    if (mode) {
      if (val_result.length == 1) { return val_result[0]; }
      else if (val_result.length == 0) { return null; }
      else { return val_result; }
    }
    return this;
  }

  attribute(name, val) {
    if (typeof name == "undefined") { throw TypeError("1 arguments 'name' required") }

    let val_result = [];
    let mode = 0; // set mode
    if (typeof val == "undefined") {
      mode = 1; //get mode
    }
    for (let node of this.result) {
      if (mode) {
        val_result.push(node.getAttribute(name));
      } else {
        if (val === null) {
          node.removeAttribute(name);
        } else {
          node.setAttribute(name, val);
        }
      }
    }

    if (mode) {
      if (val_result.length == 1) { return val_result[0]; }
      else if (val_result.length == 0) { return null; }
      else { return val_result; }
    }
    return this;
  }

  css(name, val) {
    if (typeof name == "undefined") { throw TypeError("1 arguments 'name' required") }

    let val_result = [];
    let mode = 0; // set mode
    if (typeof val == "undefined") {
      mode = 1; //get mode
    }
    for (let node of this.result) {
      var style = getComputedStyle(node);
      if (mode) {
        val_result.push(style.getPropertyValue(name));
      } else {
        node.style.setProperty(name, val);
      }
    }

    if (mode) {
      if (val_result.length == 1) { return val_result[0]; }
      else if (val_result.length == 0) { return null; }
      else { return val_result; }
    }
    return this;
  }

  html(content) {
    let html_result = [];
    let mode = 0; // set mode
    if (typeof content == "undefined") {
      mode = 1; //get mode
    }
    for (let node of this.result) {
      if (mode) {
        html_result.push(node.innerHTML );
      } else {
        node.innerHTML  = content;
      }
    }
    if (mode) {
      if (html_result.length == 1) { return html_result[0]; }
      else if (html_result.length == 0) { return null; }
      else { return html_result; }
    }
    return this;
  }

  // class managment
  addClass(cssclasses) {
    for (let node of this.result) {
      if (typeof cssclasses == "string") { cssclasses = cssclasses.split(" "); }
      for (let cssclass of cssclasses) {
        node.classList.add(cssclass);
      }
    }
    return this;
  }

  removeClass(cssclasses) {
    for (let node of this.result) {
      if (typeof cssclasses == "string") { cssclasses = cssclasses.split(" "); }
      for (let cssclass of cssclasses) {
        node.classList.remove(cssclass);
      }
    }
    return this;
  }

  // collapse
  collapse(state, options) {
    // .collapse = Close
    // .collapsing = Opening/Closing
    // .collapse.show = Open

    options = options || {};
    var default_collapse_time = 0.3;

    if (state == "show") { state = 1; }
    else if (state == "hide") { state = 2; }
    else { state = 3; }

    function collapseEnd(collapsingNode, mode) {
      collapsingNode.style.maxHeight = "";
      collapsingNode.style.transitionDuration = "";
      collapsingNode.style.transitionProperty = "";
      collapsingNode.style.transitionTimingFunction = "";
      collapsingNode.classList.remove('collapsing');
      if (mode) { collapsingNode.classList.add('show'); }
      else { collapsingNode.classList.remove('show'); }
    };

    for (var node of this.result) {

      node.classList.add("collapse");
      if (node.classList.contains("collapsing")) { continue; }

      node.style.transitionDuration = (options.Duration || default_collapse_time)+"s";
      node.style.transitionProperty = "max-height";
      node.style.transitionTimingFunction = options.TimingFunction || "ease-out";
      // hide
      if (state == 2 || ( state == 3 && node.classList.contains("show"))) {
        node.style.maxHeight = getComputedStyle(node).height;
        node.classList.add('collapsing');
        node.style.maxHeight = "0px";
        setTimeout( function(){collapseEnd(node, 0)}, (options.Duration || default_collapse_time)*1000);
      }
      // show
      else {
        node.style.maxHeight = "0px";
        node.classList.add('collapsing');
        node.style.maxHeight = node.scrollHeight + "px";
        setTimeout( function(){collapseEnd(node, 1)}, (options.Duration || default_collapse_time)*1000);
      }

    }
    return this;
  }

  // object
  append(childs, cloneAppends=false) {
    if (typeof childs == "undefined") { throw TypeError("1 arguments 'childs' required") }
    for (let node of this.result) {
      for (let childNode of childs.result) {
        node.appendChild(cloneAppends ? childNode.cloneNode(true) : childNode );
      }
    }
    return childs;
  }

  remove() {
    for (let node of this.result) {
      node.parentNode.removeChild(node);
    }
    this.result = [];
    return this;
  }

  clone() {
    var new_node_list = [];
    for (let node of this.result) {
      new_node_list.push( node.cloneNode(true) );
    }
    var nPQ = new PhaazeQuery();
    nPQ.result = new_node_list;
    return nPQ;
  }

  // selector
  find(query) {
    if (typeof query == "undefined") { query = "*" }
    var new_node_list = [];
    for (let node of this.result) {
      let nl = node.querySelectorAll(query);
      for (let nn of nl) { new_node_list.push(nn) }
    }
    var finished_list = [];
    for (var k in new_node_list) {
      if ( this.result.indexOf(new_node_list[k]) < 0) { finished_list.push(new_node_list[k]) }
    }
    var nPQ = new PhaazeQuery();
    nPQ.result = finished_list;
    return nPQ;
  }

  siblings(query) {
    if (typeof query == "undefined") { query = "*" }
    var new_node_list = [];
    for (let node of this.result) {
      let nl = node.parentNode.querySelectorAll(":scope > "+query);
      for (let nn of nl) { new_node_list.push(nn) }
    }
    var finished_list = [];
    for (var k in new_node_list) {
      if ( this.result.indexOf(new_node_list[k]) < 0) { finished_list.push(new_node_list[k]) }
    }
    var nPQ = new PhaazeQuery();
    nPQ.result = finished_list;
    return nPQ;
  }

  closest() {}
}
