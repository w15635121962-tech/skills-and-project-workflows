# Default templates

Create documents, presentations, and spreadsheets from 27 OpenAI-provided templates. Each template skill includes a preview image and a retained Office reference file that controls the output's layout and formatting.

## Templates

| Documents | Presentations | Spreadsheets |
| --- | --- | --- |
| Design Report | Business Review | Analytics Dashboard |
| Experiment Analysis | Market Trends Report | Financial Budget |
| Investment Committee Memo |  | Operating Calendar |
| Legal Memorandum | Project Kickoff | Project Tracker |
| Minimal Letterhead |  | Sales Pipeline |
| Strategy Memorandum |  | Three-Statement Forecast |
| System Design |  |  |

The presentation catalog also includes Annual Impact Report, Product Pitch, and Creative Campaign Brief. These three decks retain their nine masters and 47 layouts, including inherited backgrounds and editable placeholders.

The catalog also includes Photography Portfolio, Product Strategy, Next Generation OS, Calder Architecture, Brand Guidelines, State of Art, Growth Strategy, and Weekly Business Review. These eight decks add 50 slides, retaining their eight masters, 50 layouts, and original typography.

## How it works

Select or name a template and describe the content you want. The selected skill keeps its retained reference unchanged, delegates rendering to ChatGPT's preinstalled document, presentation, or spreadsheet capability, and verifies the finished artifact.

The plugin binds the first-party Documents, Presentations, and Spreadsheets apps so template skills can use their artifact capabilities without replacing the apps' router skills.

Office references retain their slide content; author and edit-history fields are removed from package metadata. Opaque raster images larger than 50 KB use JPEG quality 85 with 4:4:4 chroma and a maximum long edge of 1,440 pixels when this reduces file size. Transparent PNGs retain their dimensions and transparency, with palette optimization at quality 70–95 where it reduces size. Original or losslessly optimized PNGs are retained when palette conversion misses the quality threshold or would remove transparency. Palette conversion may change individual color and alpha values.

## Native presentation assets

The fourteen presentation skills also include `assets/native-presentation.pb`, referenced by `nativePresentation` in `artifact-template.json`. These are editable presentation protobufs for insertion into Spaces. The three original decks use regular text boxes and native image placeholders in place of checkerboard images. The remaining eleven decks preserve their inherited text placeholders, masters, and layouts. Both formats use the same compressed photos. Images remain embedded for the destination's existing image upload flow. The native Market Trends Report uses Roboto throughout; its PPTX retains its original typography.

Each skill retains one cover PNG, rendered ahead of time with the template fonts. The app renders individual slide previews from the selected native presentation and caches them locally. Runtime previews and editable slides use the app's available fonts.

## Maintaining presentation assets

The scripts/optimize-images.py tool creates optimized Office references and an image index using Pillow and pngquant. The scripts/optimize-native-images.mjs tool updates embedded native images and verifies that every other protobuf field is unchanged. The scripts/import-presentations.mjs tool uses Artifact Tool to import the eight decks listed in scripts/imported-presentations.json, encodes them with Walnut, checks a complete native roundtrip, and renders every slide with the source fonts. Keep the original input files outside the plugin for comparison. Run the package tests after refreshing the assets and their hash manifest.
