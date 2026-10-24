import fs from "node:fs/promises";
import path from "node:path";
import {createHash} from "node:crypto";
import {pathToFileURL} from "node:url";

const [mode, plugin, encoder, directory, indexPath] = process.argv.slice(2);
if (!["export", "apply"].includes(mode)) throw new Error("Expected mode: export or apply");
if (mode === "apply" && !indexPath) throw new Error("Apply requires an image index");
const {Presentation} = await import(pathToFileURL(encoder).href);
await fs.mkdir(directory, {recursive: true});
const index = indexPath ? JSON.parse(await fs.readFile(indexPath, "utf8")) : null;
const report = [];
const withoutImagePayloads = (proto) => Buffer.from(Presentation.encode({...proto, images:proto.images.map(image => ({...image, data:new Uint8Array(), contentType:""}))}).finish());
for (const skill of await fs.readdir(path.join(plugin, "skills"))) {
  const file = path.join(plugin, "skills", skill, "assets/native-presentation.pb");
  let original;
  try {original=await fs.readFile(file);} catch(error) {if(error.code==="ENOENT")continue;throw error;}
  const proto=Presentation.decode(original);
  const before=withoutImagePayloads(proto);
  let saved=0;
  for (const image of proto.images) {
    if (!image.data.length)continue;
    const hash=createHash("sha256").update(image.data).digest("hex");
    if (mode==="export") await fs.writeFile(path.join(directory, hash), image.data);
    else {
      const replacement=index[hash];
      if (!replacement) throw new Error(`${skill}: missing image ${hash}`);
      const data=await fs.readFile(replacement.path);
      saved+=image.data.length-data.length;
      image.data=data;
      if (replacement.mime)image.contentType=replacement.mime;
    }
  }
  if(mode!=="export"){
    for (const image of proto.images) {
      if (!image.data.length) continue;
      const png = image.data[0] === 137 && image.data[1] === 80 && image.data[2] === 78;
      const jpeg = image.data[0] === 255 && image.data[1] === 216 && image.data[2] === 255;
      if ((png && image.contentType !== "image/png") || (jpeg && image.contentType !== "image/jpeg")) {
        throw new Error(`${skill}: image MIME type does not match encoded bytes: ${image.id}`);
      }
    }
    const result=Presentation.encode(proto).finish();
    const after=Presentation.decode(result);
    if(!before.equals(withoutImagePayloads(after))) throw new Error(`${skill}: nonimage protobuf fields changed`);
    await fs.writeFile(file,result);
  }
  report.push({skill,slides:proto.slides.length,bytes:original.length,savedImageBytes:saved,images:proto.images.length});
}
await fs.writeFile(path.join(directory,"native-image-report.json"),JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify(report));
