import * as fs from "node:fs";
import * as path from "node:path";

const MAX_BYTES = 1048576;

function fail(message: string): never {
  console.error("main.ts: " + message);
  process.exit(1);
}

function main(): void {
  const here = path.dirname(new URL(import.meta.url).pathname);
  const source = path.join(here, "entry.png");
  const outDir = process.env.MAKEFUN_OUTPUT_DIR || path.join(here, "output");
  const dest = path.join(outDir, "entry.png");

  if (!fs.existsSync(source)) {
    fail("entry.png not found next to main.ts; run tools/make_image.py first");
  }

  fs.mkdirSync(outDir, { recursive: true });
  fs.copyFileSync(source, dest);

  // Self-check the copied output.
  const stat = fs.statSync(dest);
  if (stat.size > MAX_BYTES) {
    fail("entry.png is " + stat.size + " bytes, over the 1 MiB limit");
  }
  const bytes = fs.readFileSync(dest);
  const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  if (!bytes.subarray(0, 8).equals(pngMagic)) {
    fail("output is not a PNG file");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width !== 1024 || height !== 1024) {
    fail("entry.png is " + width + "x" + height + ", expected 1024x1024");
  }
  console.log(
    "OK: copied entry.png to " + dest + " (" + width + "x" + height +
    ", " + stat.size + " bytes)"
  );
}

main();
