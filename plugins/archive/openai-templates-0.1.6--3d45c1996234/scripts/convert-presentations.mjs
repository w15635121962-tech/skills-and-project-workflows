import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import { createRequire } from "node:module";
import path from "node:path";
import { pathToFileURL } from "node:url";

const [
  inputPlugin,
  outputPlugin,
  artifactEntry,
  appRoot,
  fontManifest,
  reportDirectory,
] = process.argv.slice(2);
if (!reportDirectory)
  throw new Error(
    "Expected: <input-plugin> <output-plugin> <artifact-tool-entry> <codex-apps-root> <render-font-manifest> <report-directory>",
  );
const {
  Presentation: RenderPresentation,
  PresentationFile,
  FileBlob,
} = await import(pathToFileURL(artifactEntry).href);
const requireRuntime = createRequire(artifactEntry);
const { FontLibrary } = requireRuntime("skia-canvas");
const requireApp = createRequire(path.join(appRoot, "webview/package.json"));
const importApp = (id) => import(pathToFileURL(requireApp.resolve(id)).href);
const { Presentation: PresentationProto } = await importApp(
  "@oai/walnut/pptx/presentation",
);
const { Presentation } = await importApp(
  "@oai/granola/models/presentation/presentation",
);
const { Position } = await importApp(
  "@oai/granola/models/presentation/position",
);
const { resolveStyles } = await importApp("@oai/granola/draw-utils/utils");
const { buildParagraphLevelDefaults } = await importApp(
  "@oai/granola/models/presentation/paragraph-level-defaults",
);
const { resolveThemeTypeface } = await importApp(
  "@oai/granola/models/presentation/theme-typeface-resolution",
);
const fontFiles = JSON.parse(await fs.readFile(fontManifest, "utf8"));
const selectedTemplates = process.argv.slice(8);
const templates = [
  {
    name: "market-trends-report",
    slides: 6,
    image: "image1.png",
    typeface: "Roboto",
  },
  { name: "business-review", slides: 14 },
  { name: "project-kickoff", slides: 12, image: "image1.png" },
  {
    name: "annual-impact-report",
    slides: 10,
    masters: 7,
    layouts: 14,
    preservePlaceholders: true,
  },
  {
    name: "product-pitch",
    slides: 12,
    masters: 1,
    layouts: 18,
    preservePlaceholders: true,
  },
  {
    name: "creative-campaign-brief",
    slides: 10,
    masters: 1,
    layouts: 15,
    preservePlaceholders: true,
  },
].filter(
  (template) =>
    selectedTemplates.length === 0 || selectedTemplates.includes(template.name),
);
const furniture = new Set(["footer", "slideNumber", "dateTime", "header"]);
const report = [];
await fs.mkdir(reportDirectory, { recursive: true });

for (const template of templates) {
  const skill = `artifact-template-${template.name}`;
  const input = path.join(inputPlugin, "skills", skill);
  const output = path.join(outputPlugin, "skills", skill);
  const pptxPath = path.join(input, "assets/reference.pptx");
  const sourceSha256 = createHash("sha256")
    .update(await fs.readFile(pptxPath))
    .digest("hex");
  const imported = await PresentationFile.importPptx(
    await FileBlob.load(pptxPath),
  );
  const source = imported.toProto();
  if (source.slides.length !== template.slides)
    throw new Error(`${skill}: unexpected slide count`);

  // Registration belongs to this offline renderer. No app-worker changes are required.
  FontLibrary.use(fontFiles);
  if (template.typeface) {
    replaceTypeface(source, template.typeface);
    source.fonts = source.fonts.filter(
      (font) => font.name === template.typeface,
    );
  }
  const model = Presentation.load(source);
  const beforeLayouts = JSON.stringify(model.layouts.toProto());
  const beforeSlideLayouts = model.slides.items.map(
    (slide) => slide.toProto().layoutId,
  );
  const beforeText = model.slides.items.map(slideText);
  const beforeFrames = model.slides.items.map(textFrames);
  const slides = model.slides.items.map((slide) => {
    // These decks intentionally inherit their editable placeholders from masters/layouts.
    if (template.preservePlaceholders) return slide.toProto();
    const textBoxes = new Map(
      slide.shapes.items
        .filter(
          (shape) =>
            shape.text.toString().trim() &&
            !furniture.has(shape.placeholderType),
        )
        .map((shape) => {
          const frame = shape.resolveFrame({ includePreview: false });
          const shapeProto = structuredClone(shape.toProto());
          const textStyle = structuredClone(resolveStyles(shape, model, slide));
          textStyle.typeface = resolveThemeTypeface(
            textStyle.typeface,
            source.theme.fontScheme,
          );
          return [
            shape.id,
            {
              ...shapeProto,
              bbox: new Position(
                { ...shape.position.toJSON(), ...frame },
                true,
              ).toProto(),
              placeholderType: undefined,
              placeholderIndex: undefined,
              textStyle,
              levelsStyles: buildParagraphLevelDefaults(shape, slide).map(
                (defaults, level) => ({
                  ...structuredClone(defaults),
                  level: level + 1,
                  paragraphStyle: {
                    ...structuredClone(defaults?.paragraphStyle),
                    bulletCharacter:
                      defaults?.paragraphStyle?.bulletCharacter ?? "",
                  },
                }),
              ),
            },
          ];
        }),
    );
    return {
      ...slide.toProto(),
      elements: slide.elements
        .toProto()
        .map((element) => textBoxes.get(element.id) ?? element),
    };
  });
  model.slides.replace(slides);

  // These are the source decks' checkerboard sample images. Keep decorative images.
  let imagePlaceholders = 0;
  if (template.image) {
    const assetId = `/ppt/media/${template.image}`;
    const asset = model.images.getById(assetId);
    if (!asset) throw new Error(`${skill}: missing checkerboard image`);
    asset.data = new Uint8Array();
    asset.uri = undefined;
    for (const slide of model.slides.items) {
      for (const image of slide.images.items) {
        if (image.image?.id !== assetId) continue;
        image.isPlaceholder = true;
        image.prompt = undefined;
        imagePlaceholders++;
      }
    }
    if (imagePlaceholders === 0)
      throw new Error(`${skill}: checkerboard image has no placements`);
  }
  if (
    JSON.stringify(beforeText) !==
    JSON.stringify(model.slides.items.map(slideText))
  ) {
    throw new Error(`${skill}: sample text changed during conversion`);
  }
  const proto = {
    ...model.toProto(),
    slides: model.slides.toProto(),
    images: model.getImageAssetItems().map((image) => image.toProto()),
  };
  const bytes = PresentationProto.encode(proto).finish();
  const roundTrip = Presentation.load(PresentationProto.decode(bytes));
  if (
    JSON.stringify(beforeText) !==
    JSON.stringify(roundTrip.slides.items.map(slideText))
  ) {
    throw new Error(`${skill}: native roundtrip changed sample text`);
  }
  assertFramesMatch(
    beforeFrames,
    roundTrip.slides.items.map(textFrames),
    skill,
  );
  if (
    JSON.stringify(roundTrip.layouts.toProto()) !== beforeLayouts ||
    JSON.stringify(
      roundTrip.slides.items.map((slide) => slide.toProto().layoutId),
    ) !== JSON.stringify(beforeSlideLayouts)
  ) {
    throw new Error(
      `${skill}: native roundtrip changed masters, layouts, or slide layout links`,
    );
  }
  const masterCount = roundTrip.layouts.items.filter(
    (layout) => layout.type === "master",
  ).length;
  const layoutCount = roundTrip.layouts.items.length - masterCount;
  if (
    (template.masters != null && masterCount !== template.masters) ||
    (template.layouts != null && layoutCount !== template.layouts)
  ) {
    throw new Error(`${skill}: unexpected master/layout counts`);
  }
  const missingFonts = roundTrip.fontFamilies.filter(
    (family) => !FontLibrary.has(family),
  );
  if (missingFonts.length)
    throw new Error(
      `${skill}: renderer missing fonts: ${missingFonts.join(", ")}`,
    );
  if (
    template.typeface &&
    roundTrip.fontFamilies.some((family) => family !== template.typeface)
  ) {
    throw new Error(`${skill}: unexpected font after Roboto conversion`);
  }
  await fs.mkdir(path.join(output, "assets"), {
    recursive: true,
  });
  await fs.rm(path.join(output, "assets/native-previews"), {
    recursive: true,
    force: true,
  });
  await fs.writeFile(path.join(output, "assets/native-presentation.pb"), bytes);
  const renderModel = RenderPresentation.load(proto);
  renderModel.view.showPlaceholders();
  for (const [index, slide] of renderModel.slides.items.entries()) {
    const previewPath =
      index === 0
        ? path.join(output, "assets/preview.png")
        : path.join(reportDirectory, `${template.name}-slide-${index + 1}.png`);
    const scale = 800 / Math.max(slide.frame.width, slide.frame.height);
    const png = await renderModel.export({ slide, format: "png", scale });
    const pngBytes = Buffer.from(await png.arrayBuffer());
    if (Math.max(pngBytes.readUInt32BE(16), pngBytes.readUInt32BE(20)) > 800) {
      throw new Error(`${skill}: preview exceeds 800 pixels`);
    }
    await fs.writeFile(previewPath, pngBytes);
    const layout = await slide.export({ format: "layout", detail: "full" });
    await fs.writeFile(
      path.join(reportDirectory, `${template.name}-slide-${index + 1}.json`),
      await layout.text(),
    );
  }
  const montage = await renderModel.export({
    format: "png",
    montage: { columns: 3, slideWidth: 400 },
  });
  await fs.writeFile(
    path.join(reportDirectory, `${template.name}-montage.png`),
    new Uint8Array(await montage.arrayBuffer()),
  );
  const manifest = JSON.parse(
    await fs.readFile(path.join(input, "artifact-template.json"), "utf8"),
  );
  delete manifest.nativeLayout;
  manifest.nativePresentation = {
    schemaVersion: 1,
    reference: "assets/native-presentation.pb",
  };
  await fs.writeFile(
    path.join(output, "artifact-template.json"),
    JSON.stringify(manifest, null, 2) + "\n",
  );
  const entry = {
    template: template.name,
    slides: template.slides,
    sourceSha256,
    nativeBytes: bytes.byteLength,
    masters: masterCount,
    layouts: layoutCount,
    fonts: roundTrip.fontFamilies,
    imagePlaceholders,
    retainedImageBytes: proto.images.reduce(
      (sum, image) => sum + image.data.byteLength,
      0,
    ),
    previews: renderModel.slides.items.length,
  };
  report.push(entry);
  await fs.writeFile(
    path.join(reportDirectory, "conversion-report.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  console.log(JSON.stringify(entry));
  imported.getCrdtDoc().destroy();
  model.getCrdtDoc().destroy();
  roundTrip.getCrdtDoc().destroy();
  renderModel.getCrdtDoc().destroy();
}

function slideText(slide) {
  return slide.shapes.items.map((shape) => ({
    id: shape.id,
    text: shape.text.toString(),
  }));
}

function textFrames(slide) {
  return slide.shapes.items
    .filter((shape) => shape.text.toString().trim())
    .map((shape) => ({
      id: shape.id,
      ...shape.resolveFrame({ includePreview: false }),
    }));
}

function assertFramesMatch(before, after, skill) {
  for (const [index, frames] of before.entries()) {
    for (const frame of frames) {
      const actual = after[index].find((value) => value.id === frame.id);
      for (const key of ["left", "top", "width", "height"]) {
        if (!actual || Math.abs(actual[key] - frame[key]) > 0.001) {
          throw new Error(
            `${skill}: slide ${index + 1} text frame ${frame.id} changed ${key}: ${frame[key]} -> ${actual?.[key]}`,
          );
        }
      }
    }
  }
}

function replaceTypeface(value, typeface) {
  if (!value || typeof value !== "object" || ArrayBuffer.isView(value)) return;
  for (const [key, child] of Object.entries(value)) {
    if (
      [
        "typeface",
        "latinTypeface",
        "eastAsianTypeface",
        "complexScriptTypeface",
      ].includes(key) &&
      typeof child === "string" &&
      child
    ) {
      value[key] = typeface;
    } else if (key !== "fonts") {
      replaceTypeface(child, typeface);
    }
  }
}
