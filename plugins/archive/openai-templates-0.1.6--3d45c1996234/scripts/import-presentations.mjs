import fs from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";

const [pluginDirectory, artifactEntry, encoderEntry, templatesPath, reportDirectory, fontManifest] = process.argv.slice(2);
if (!reportDirectory) throw new Error("Expected: <plugin-directory> <artifact-tool-entry> <walnut-presentation-entry> <templates-json> <report-directory> [font-manifest]");
const { Presentation, PresentationFile, FileBlob } = await import(pathToFileURL(artifactEntry).href);
const { Presentation: PresentationProto } = await import(pathToFileURL(encoderEntry).href);
const { FontLibrary } = createRequire(artifactEntry)("skia-canvas");
if (fontManifest) FontLibrary.use(JSON.parse(await fs.readFile(fontManifest, "utf8")));
const templates = JSON.parse(await fs.readFile(templatesPath, "utf8"));
await fs.mkdir(reportDirectory, { recursive: true });
const report = [];
for (const template of templates) {
  const directory = path.join(pluginDirectory, "skills", `artifact-template-${template.name}`);
  const input = path.join(directory, "assets/reference.pptx");
  const imported = await PresentationFile.importPptx(await FileBlob.load(input));
  const source = imported.toProto();
  if (source.slides.length !== template.slides) throw new Error(`${template.name}: unexpected slide count`);
  const bytes = PresentationProto.encode(source).finish();
  const decoded = PresentationProto.decode(bytes);
  const native = Presentation.load(decoded);
  // Compare the complete presentation after normalized encode/decode. No slide,
  // layout, text, geometry, theme, or image transformations belong in this step.
  const normalized = PresentationProto.encode(native.toProto()).finish();
  if (!Buffer.from(bytes).equals(Buffer.from(normalized))) throw new Error(`${template.name}: native model roundtrip changed the presentation`);
  await fs.writeFile(path.join(directory, "assets/native-presentation.pb"), bytes);
  const missingFonts = native.fontFamilies.filter((family) => !FontLibrary.has(family));
  if (missingFonts.length) throw new Error(`${template.name}: renderer missing fonts: ${missingFonts.join(", ")}`);
  for (const [index, slide] of native.slides.items.entries()) {
    const png = await native.export({slide, format: "png", scale: 800 / Math.max(slide.frame.width, slide.frame.height)});
    const target = index === 0 ? path.join(directory, "assets/preview.png") : path.join(reportDirectory, `${template.name}-slide-${index+1}.png`);
    await fs.writeFile(target, new Uint8Array(await png.arrayBuffer()));
  }
  const montage = await native.export({ format: "png", montage: { columns: 3, slideWidth: 400 }});
  await fs.writeFile(path.join(reportDirectory, `${template.name}-montage.png`), new Uint8Array(await montage.arrayBuffer()));
  const entry = {
    name: template.name,
    sourceSha256: createHash("sha256").update(await fs.readFile(input)).digest("hex"),
    nativeSha256: createHash("sha256").update(bytes).digest("hex"),
    slides: native.slides.items.length,
    masters: native.layouts.items.filter(layout => layout.type === "master").length,
    layouts: native.layouts.items.filter(layout => layout.type !== "master").length,
    fonts: native.fontFamilies,
    nativeBytes: bytes.length,
    imageBytes: source.images.reduce((sum, image) => sum + image.data.length, 0),
  };
  report.push(entry);
  await fs.writeFile(path.join(reportDirectory, "conversion-report.json"), JSON.stringify(report, null, 2)+"\n");
  console.log(JSON.stringify(entry));
  imported.getCrdtDoc().destroy();
  native.getCrdtDoc().destroy();
}
