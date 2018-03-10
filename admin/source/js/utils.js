function get_origen(obj, pre) {
  if (pre == null) {pre = "";}
  // test for normal container
  var t = $(obj).children('.name_space');
  if (t.length != 0) {
    pre = pre + t.text();
  }

  var upper = $(obj).parents('.sc_button_top');
  if (upper.length == 0) {return pre;}

  upper = upper[0];
  pre = $(upper).children('.supercontainer_button').children('.name_space').text() + "/" + pre;

  return get_origen(upper, pre);

}