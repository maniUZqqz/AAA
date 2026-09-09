/**
 * Copies the real sample output into the site.
 *
 * The showcase is the strongest thing this site has, and it must not depend
 * on a sibling folder existing at deploy time. So the media and captions are
 * copied in once, here, and the pages read only from inside the project.
 *
 *     node scripts/sync-showcase.mjs
 */
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const root = join(here, "..");
const data = join(root, "..", "..", "..", "دیتا");

const SAMPLES = join(data, "3-نمونه‌کار");
const MEDIA = join(data, "2-ارائه", "static", "portfolio");

const WORKS = [
  { id: "apparel", category: "پوشاک", product: "کت اورسایز کرم",
    dir: "01-پوشاک", image: "apparel.png" },
  { id: "accessory", category: "اکسسوری", product: "گردنبند مینیمال",
    dir: "02-اکسسوری", image: "accessory.png" },
  { id: "decor", category: "دکوراسیون", product: "آباژور مینیمال",
    dir: "03-دکوراسیون", image: "decor.png",
    videos: [1, 2, 3, 4, 5].map((n) => `decor-seg${n}.mp4`) },
];

if (!existsSync(SAMPLES)) {
  console.log("  samples folder not found - keeping existing copy");
  process.exit(0);
}

const out = [];
for (const w of WORKS) {
  const captionFile = join(SAMPLES, w.dir, "caption.txt");
  if (!existsSync(captionFile)) {
    console.log(`  ! caption missing for ${w.id}`);
    continue;
  }
  out.push({
    id: w.id,
    category: w.category,
    product: w.product,
    image: `/showcase/${w.image}`,
    videos: (w.videos ?? []).map((v) => `/showcase/${v}`),
    caption: readFileSync(captionFile, "utf8").trim(),
  });
}

mkdirSync(join(root, "content", "showcase"), { recursive: true });
writeFileSync(
  join(root, "content", "showcase", "works.json"),
  JSON.stringify(out, null, 2),
  "utf8",
);

// copied one file at a time: cpSync crashes the process on Windows when the
// source path contains non-ASCII segments, and it does so *after* the copy,
// which turns a working prebuild step into a failed build
if (existsSync(MEDIA)) {
  const dest = join(root, "public", "showcase");
  mkdirSync(dest, { recursive: true });
  for (const name of readdirSync(MEDIA)) {
    const from = join(MEDIA, name);
    if (!statSync(from).isFile()) continue;
    const to = join(dest, name);
    if (existsSync(to) && statSync(to).size === statSync(from).size) continue;
    copyFileSync(from, to);
  }
}

console.log(`  showcase synced: ${out.length} works`);
