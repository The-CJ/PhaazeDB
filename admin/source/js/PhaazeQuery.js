// because JQuery is to huge, i want a light wight framework, AND i have a lot of freetime, so i made my own

function _(query) {
  return new PhaazeQuery(query);
}

_.get = function (url, parameter) {
  if (typeof url == "undefined") {throw "1 arguments 'url' required"}
  return new PhaazeRequest("GET", url, parameter);
}

class PhaazeRequest {
  constructor(method, url, parameter) {
    this.method = method;
    this.url = url;
    this.parameter = parameter;
    this.status = null;
    this.formData = null;
    this.response = null;

    this.call();
  }
  done(func) {
    if (typeof func == "undefined") { throw "1 argument 'func' required" }
  }
  fail(func) {
    if (typeof func == "undefined") { throw "1 argument 'func' required" }
  }
  call() {
    this.formData = new FormData();
    if (typeof this.parameter == "undefined") {  }
    else if (typeof this.parameter == "object") {
      for (var key in this.parameter) { this.formData.append(key, this.parameter[key]); }
    } else { throw "2 argument 'parameter' must be object or null" }
    var this2 = this;
    var r = new XMLHttpRequest();
    r.onload = function () {
      this2.status = r.status;
      this2.response = r;
    }
    r.open(this.method, this.url);
    r.send(this.formData);
  }
}

class PhaazeQuery {
  // yeah i actully name it PhaazeQuery, fight me REEEEEEEEEE
  constructor(query) {
    this.result = document.querySelectorAll(query);
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
  }

  // class managment
  addClass(cssclass) {
    for (let node of this.result) {
      node.classList.add(cssclass);
    }
  }

  removeClass(cssclass) {
    for (let node of this.result) {
      node.classList.remove(cssclass);
    }
  }

  // collapse
  collapse(state) {
    if (state == "show") { state = 1; }
    else if (state == "hide") { state = 2; }
    else { state = 3; }

    for (var node of this.result) {
      node.eventlist = node.eventlist ? node.eventlist : [];
      // hide
      if (state == 2 || ( state == 3 && node.style.maxHeight)) {
        node.style.maxHeight = null;
        function transitionend() {
          for (let e of node.eventlist) {
            node.removeEventListener("transitionend", e);
          }
          node.classList.remove('show');
        };
        node.addEventListener("transitionend", transitionend);
        node.eventlist.push(transitionend);
      }
      // show
      else {
        node.classList.add('show');
        node.style.maxHeight = node.scrollHeight + "px";
      }
    }
  }


}
