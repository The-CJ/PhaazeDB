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
    if (string == null) {
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



}
