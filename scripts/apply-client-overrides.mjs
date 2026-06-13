import { copyFile, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const overrides = [
  {
    source: "packages/client-overrides/ts/src/client/index.ts",
    target: "packages/client-ts/src/client/index.ts",
  },
  {
    source: "packages/client-overrides/ts/src/client/overrides.ts",
    target: "packages/client-ts/src/client/overrides.ts",
  },
  {
    source:
      "packages/client-overrides/py/api_client/api/sessions/stream_session_events.py",
    target:
      "packages/client-py/api_client/api/sessions/stream_session_events.py",
  },
];

for (const override of overrides) {
  const target = resolve(override.target);
  await mkdir(dirname(target), { recursive: true });
  await copyFile(resolve(override.source), target);
}

const packageJsonPath = resolve("packages/client-ts/package.json");
const packagePatchPath = resolve(
  "packages/client-overrides/ts/package.patch.json",
);
const packageJson = JSON.parse(await readFile(packageJsonPath, "utf8"));
const packagePatch = JSON.parse(await readFile(packagePatchPath, "utf8"));

await writeFile(
  packageJsonPath,
  `${JSON.stringify(mergeObjects(packageJson, packagePatch), null, 2)}\n`,
);

const pythonPyprojectPath = resolve("packages/client-py/pyproject.toml");
const pythonPatchPath = resolve(
  "packages/client-overrides/py/pyproject.patch.json",
);
const pythonPatch = JSON.parse(await readFile(pythonPatchPath, "utf8"));
let pythonPyproject = await readFile(pythonPyprojectPath, "utf8");

for (const [section, dependencies] of Object.entries(pythonPatch)) {
  pythonPyproject = addTomlSectionEntries(
    pythonPyproject,
    section,
    dependencies,
  );
}

await writeFile(pythonPyprojectPath, pythonPyproject);

function mergeObjects(target, patch) {
  const merged = { ...target };

  for (const [key, value] of Object.entries(patch)) {
    if (isPlainObject(value) && isPlainObject(merged[key])) {
      merged[key] = mergeObjects(merged[key], value);
      continue;
    }

    merged[key] = value;
  }

  return merged;
}

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function addTomlSectionEntries(content, section, entries) {
  let patched = content;
  const sectionHeader = `[${section}]`;
  const sectionStart = patched.indexOf(sectionHeader);

  if (sectionStart === -1) {
    throw new Error(`Unable to find TOML section ${sectionHeader}`);
  }

  for (const [key, value] of Object.entries(entries)) {
    const entry = `${key} = ${JSON.stringify(value)}`;
    if (new RegExp(`^${escapeRegExp(key)}\\s*=`, "m").test(patched)) {
      continue;
    }

    const nextSectionStart = patched.indexOf(
      "\n[",
      sectionStart + sectionHeader.length,
    );
    const insertAt =
      nextSectionStart === -1 ? patched.length : nextSectionStart;
    const before = patched.slice(0, insertAt).trimEnd();
    const after = patched.slice(insertAt);
    patched = `${before}\n${entry}\n${after.startsWith("\n") ? after : `\n${after}`}`;
  }

  return patched;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
