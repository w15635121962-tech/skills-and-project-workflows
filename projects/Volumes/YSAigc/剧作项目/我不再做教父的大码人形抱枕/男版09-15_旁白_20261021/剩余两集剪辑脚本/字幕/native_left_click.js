// Task-local real click helper. User explicitly authorized JXA/CGEvent in this chat.
ObjC.import('ApplicationServices');
function run(argv) {
  if (argv.length !== 2) throw new Error('Expected current verified global screen x/y.');
  var x = Number(argv[0]), y = Number(argv[1]);
  if (!Number.isFinite(x) || !Number.isFinite(y)) throw new Error('Invalid point.');
  var point = $.CGPointMake(x, y);
  var down = $.CGEventCreateMouseEvent(null, $.kCGEventLeftMouseDown, point, $.kCGMouseButtonLeft);
  var up = $.CGEventCreateMouseEvent(null, $.kCGEventLeftMouseUp, point, $.kCGMouseButtonLeft);
  if (!down || !up) throw new Error('Cannot create mouse events.');
  $.CGEventPost($.kCGHIDEventTap, down);
  delay(0.08);
  $.CGEventPost($.kCGHIDEventTap, up);
  return 'Real click at ' + x + ', ' + y;
}
