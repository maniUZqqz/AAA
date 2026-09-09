/**
 * Markdown posts from `content/blog/`.
 *
 * Files, not a database: posts are versioned with the code, reviewable in a
 * pull request, and need no admin to be online. Front matter carries the SEO
 * fields so a post is publishable by anyone who can write Markdown.
 */
import fs from "node:fs";
import path from "node:path";

import matter from "gray-matter";
import { remark } from "remark";
import html from "remark-html";

const DIR = path.join(process.cwd(), "content", "blog");

export type Post = {
  slug: string;
  title: string;
  description: string;
  date: string;
  author: string;
  tags: string[];
  readingMinutes: number;
  cover?: string;
};

export type FullPost = Post & { html: string };

function readAll(): { slug: string; raw: string }[] {
  if (!fs.existsSync(DIR)) return [];
  return fs
    .readdirSync(DIR)
    .filter((f) => f.endsWith(".md"))
    .map((f) => ({
      slug: f.replace(/\.md$/, ""),
      raw: fs.readFileSync(path.join(DIR, f), "utf8"),
    }));
}

function meta(slug: string, raw: string): { post: Post; body: string } {
  const { data, content } = matter(raw);
  const words = content.trim().split(/\s+/).length;
  return {
    post: {
      slug,
      title: data.title ?? slug,
      description: data.description ?? "",
      date: data.date ?? "",
      author: data.author ?? "تیم آپ‌مارکت",
      tags: data.tags ?? [],
      cover: data.cover,
      // Persian reads slower than English in most measurements; 200 wpm is a
      // reasonable middle and only ever shown as a rough hint
      readingMinutes: Math.max(1, Math.round(words / 200)),
    },
    body: content,
  };
}

export function getPosts(): Post[] {
  return readAll()
    .map(({ slug, raw }) => meta(slug, raw).post)
    .sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getTags(): string[] {
  const all = getPosts().flatMap((p) => p.tags);
  return Array.from(new Set(all));
}

export async function getPost(slug: string): Promise<FullPost | null> {
  const file = path.join(DIR, `${slug}.md`);
  if (!fs.existsSync(file)) return null;
  const { post, body } = meta(slug, fs.readFileSync(file, "utf8"));
  const processed = await remark().use(html).process(body);
  return { ...post, html: processed.toString() };
}
