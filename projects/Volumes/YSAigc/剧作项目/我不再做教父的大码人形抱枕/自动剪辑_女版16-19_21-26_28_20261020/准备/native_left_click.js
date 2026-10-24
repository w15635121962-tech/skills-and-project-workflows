// Executes only when explicitly invoked after user authorization for CGEvent.
ObjC.import('ApplicationServices');

function run(argv) {
  if (argv.length !== 2) throw new Error('Expected current global screen x and y.');
  var x = Number(argv[0]);
  var y = Number(argv[1]);
  if (!Number.isFinite(x) || !Number.isFinite(y)) throw new Error('Invalid point.');
  var point = $.CGPointMake(x, y);
  var down = $.CGEventCreateMouseEvent(null, $.kCGEventLeftMouseDown, point, $.kCGMouseButtonLeft);
  var up = $.CGEventCreateMouseEvent(null, $.kCGEventLeftMouseUp, point, $.kCGMouseButtonLeft);
  if (!down || !up) throw new Error('Could not create native mouse events.');
  $.CGEventPost($.kCGHIDEventTap, down);
  delay(0.08);
  $.CGEventPost($.kCGHIDEventTap, up);
  return 'Native left click delivered at ' + x + ', ' + y;
}
