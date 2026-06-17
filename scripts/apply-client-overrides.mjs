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

await generatePythonUnionAliasModels();

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

async function generatePythonUnionAliasModels() {
  const openapiPath = resolve("packages/contracts/openapi.json");
  const modelsInitPath = resolve(
    "packages/client-py/api_client/models/__init__.py",
  );
  const openapi = JSON.parse(await readFile(openapiPath, "utf8"));
  const aliases = findUnionAliasSchemas(openapi);

  for (const alias of aliases) {
    const aliasPath = resolve(
      `packages/client-py/api_client/models/${pythonModuleName(alias.name)}.py`,
    );
    await mkdir(dirname(aliasPath), { recursive: true });
    await writeFile(aliasPath, renderPythonUnionAliasModel(alias));
  }

  await exportPythonUnionAliasModels(modelsInitPath, aliases);
}

function findUnionAliasSchemas(openapi) {
  return Object.entries(openapi.components?.schemas ?? {})
    .filter(([, schema]) => isUnionAliasSchema(schema))
    .map(([name, schema]) => ({
      name,
      modelNames: (schema.oneOf ?? schema.anyOf).map((item) =>
        componentNameFromRef(item.$ref),
      ),
    }));
}

function isUnionAliasSchema(schema) {
  const refs = schema?.oneOf ?? schema?.anyOf;
  return (
    Array.isArray(refs) &&
    refs.length > 0 &&
    refs.every((item) => isComponentSchemaRef(item?.$ref))
  );
}

function renderPythonUnionAliasModel(alias) {
  const imports = alias.modelNames
    .map((name) => `from .${pythonModuleName(name)} import ${name}`)
    .sort((left, right) => left.localeCompare(right));
  const union = alias.modelNames
    .map((name, index) => `${index === 0 ? "    " : "    | "}${name}`)
    .join("\n");
  return `from typing import TypeAlias

${imports.join("\n")}

${alias.name}: TypeAlias = (
${union}
)
`;
}

function componentNameFromRef(ref) {
  if (!isComponentSchemaRef(ref)) {
    throw new Error(`Unsupported union alias schema ref: ${ref}`);
  }

  return ref.slice("#/components/schemas/".length);
}

function isComponentSchemaRef(ref) {
  return typeof ref === "string" && ref.startsWith("#/components/schemas/");
}

function pythonModuleName(name) {
  return name
    .replace(/([a-z0-9])([A-Z])/g, "$1_$2")
    .replace(/([A-Z]+)([A-Z][a-z])/g, "$1_$2")
    .toLowerCase();
}

async function exportPythonUnionAliasModels(modelsInitPath, aliases) {
  let content = await readFile(modelsInitPath, "utf8");
  content = addPythonModelImports(content, aliases);
  content = addPythonModelAllEntries(content, aliases);
  await writeFile(modelsInitPath, content);
}

function addPythonModelImports(content, aliases) {
  const importBlock = content.match(
    /(?<header>"""Contains all the data models used in inputs\/outputs"""\n\n)(?<imports>[\s\S]*?)(?<footer>\n__all__ = \()/,
  );

  if (!importBlock?.groups) {
    throw new Error("Unable to find generated Python models import block");
  }

  const imports = new Set(
    importBlock.groups.imports
      .trim()
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean),
  );

  for (const alias of aliases) {
    imports.add(`from .${pythonModuleName(alias.name)} import ${alias.name}`);
  }

  const sortedImports = [...imports].sort((left, right) =>
    left.localeCompare(right),
  );
  return content.replace(
    importBlock[0],
    `${importBlock.groups.header}${sortedImports.join("\n")}\n${importBlock.groups.footer}`,
  );
}

function addPythonModelAllEntries(content, aliases) {
  const allBlock = content.match(
    /(?<header>__all__ = \(\n)(?<entries>[\s\S]*?)(?<footer>\)\n)/,
  );

  if (!allBlock?.groups) {
    throw new Error("Unable to find generated Python models __all__ block");
  }

  const entries = new Set(
    allBlock.groups.entries
      .trim()
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean),
  );

  for (const alias of aliases) {
    entries.add(`"${alias.name}",`);
  }

  const sortedEntries = [...entries].sort((left, right) =>
    left.localeCompare(right),
  );
  return content.replace(
    allBlock[0],
    `${allBlock.groups.header}${sortedEntries.map((entry) => `    ${entry}`).join("\n")}\n${allBlock.groups.footer}`,
  );
}
