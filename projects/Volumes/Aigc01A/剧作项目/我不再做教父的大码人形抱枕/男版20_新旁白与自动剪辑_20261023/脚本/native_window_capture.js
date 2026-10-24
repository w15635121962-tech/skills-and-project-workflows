ObjC.import('ApplicationServices');
ObjC.import('AppKit');
function run(argv) {
 if(argv.length!==5) throw Error('Need output and verified x/y/w/h');
 var rect=$.CGRectMake(Number(argv[1]),Number(argv[2]),Number(argv[3]),Number(argv[4]));
 var cg=$.CGWindowListCreateImage(rect,$.kCGWindowListOptionOnScreenOnly,$.kCGNullWindowID,$.kCGWindowImageDefault);
 if(!cg) throw Error('Native screenshot unavailable');
 var rep=$.NSBitmapImageRep.alloc.initWithCGImage(cg);
 var data=rep.representationUsingTypeProperties($.NSBitmapImageFileTypePNG,$({}));
 if(!data.writeToFileAtomically($(argv[0]),true)) throw Error('Screenshot not saved');
 return 'Current native app view saved';
}
