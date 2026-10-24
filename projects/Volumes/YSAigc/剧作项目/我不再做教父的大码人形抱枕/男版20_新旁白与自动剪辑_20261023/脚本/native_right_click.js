ObjC.import('ApplicationServices');
function run(argv){var p=$.CGPointMake(Number(argv[0]),Number(argv[1]));$.CGEventPost($.kCGHIDEventTap,$.CGEventCreateMouseEvent(null,$.kCGEventRightMouseDown,p,$.kCGMouseButtonRight));delay(.08);$.CGEventPost($.kCGHIDEventTap,$.CGEventCreateMouseEvent(null,$.kCGEventRightMouseUp,p,$.kCGMouseButtonRight));return 'Right click at verified point';}
