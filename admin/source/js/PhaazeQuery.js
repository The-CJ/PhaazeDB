// because JQuery is to huge, i want a light wight framework, AND i have a lot of freetime, i made my own

function _(query) {
  return new PhaazeQuery(query);
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
    if (typeof state == "undefined") { state = "toggle"; }

    for (let node of this.result) {
      if (state == "show") {
        node.classList.add('show');
        node.style.maxHeight = node.scrollHeight + "px";
      }
      else if (state == "hide") {
        node.classList.remove('show');
        node.style.maxHeight = null;
      }
      else {
        node.classList.toggle('show');
        if (node.style.maxHeight){ node.style.maxHeight = null; }
        else { node.style.maxHeight = node.scrollHeight + "px"; }
      }
    }
  }


}
