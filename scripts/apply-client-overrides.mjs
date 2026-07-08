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
  {
    source:
      "packages/client-overrides/py/api_client/api/sessions/stream_session_tokens.py",
    target:
      "packages/client-py/api_client/api/sessions/stream_session_tokens.py",
  },
];

const sourceEnumOverrides = [
  {
    name: "ParticipantType",
    source: "apps/api/src/api/modules/session_configs/models/participants.py",
  },
  {
    name: "HistoryMode",
    source: "apps/api/src/api/modules/strategies/history/configs.py",
  },
  {
    name: "ResolutionMode",
    source: "apps/api/src/api/modules/strategies/resolution/configs.py",
  },
  {
    name: "TurnSelectionMode",
    source: "apps/api/src/api/modules/strategies/turn_selection/configs.py",
  },
];

for (const override of overrides) {
  const target = resolve(override.target);
  await mkdir(dirname(target), { recursive: true });
  await copyFile(resolve(override.source), target);
}

await generatePythonUnionAliasModels();
await generateSourceEnumOverrides(sourceEnumOverrides);
await generateSchemaMetadata();

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

async function generateSourceEnumOverrides(enumOverrides) {
  const enumDefinitions = [];

  for (const enumOverride of enumOverrides) {
    enumDefinitions.push(await readPythonEnumDefinition(enumOverride));
  }

  await generatePythonEnumOverrides(enumDefinitions);
  await generateTypescriptEnumOverrides(enumDefinitions);
}

async function readPythonEnumDefinition(enumOverride) {
  const source = await readFile(resolve(enumOverride.source), "utf8");
  const lines = source.split("\n");
  const classStart = lines.findIndex((line) =>
    new RegExp(`^class\\s+${escapeRegExp(enumOverride.name)}\\(`).test(line),
  );

  if (classStart === -1) {
    throw new Error(
      `Unable to find enum ${enumOverride.name} in ${enumOverride.source}`,
    );
  }

  const members = [];
  for (const line of lines.slice(classStart + 1)) {
    if (line.trim() === "") {
      continue;
    }
    if (!line.startsWith("    ")) {
      break;
    }

    const member = line.match(
      /^\s{4}(?<name>[A-Z][A-Z0-9_]*)\s*=\s*["'](?<value>[^"']+)["']/,
    );
    if (member?.groups) {
      members.push({
        name: member.groups.name,
        value: member.groups.value,
      });
    }
  }

  if (members.length === 0) {
    throw new Error(
      `Unable to find enum members for ${enumOverride.name} in ${enumOverride.source}`,
    );
  }

  return {
    name: enumOverride.name,
    members,
  };
}

async function generatePythonEnumOverrides(enumDefinitions) {
  const modelsInitPath = resolve(
    "packages/client-py/api_client/models/__init__.py",
  );
  const modelsInit = await readFile(modelsInitPath, "utf8");

  for (const enumDefinition of enumDefinitions) {
    if (pythonModelsInitExports(modelsInit, enumDefinition.name)) {
      continue;
    }

    const enumPath = resolve(
      `packages/client-py/api_client/models/${pythonModuleName(enumDefinition.name)}.py`,
    );
    await mkdir(dirname(enumPath), { recursive: true });
    await writeFile(enumPath, renderPythonEnumOverride(enumDefinition));
  }

  await exportPythonModelSymbols(modelsInitPath, enumDefinitions);
}

function renderPythonEnumOverride(enumDefinition) {
  const members = enumDefinition.members
    .map((member) => `    ${member.name} = ${JSON.stringify(member.value)}`)
    .join("\n");

  return `from enum import Enum


class ${enumDefinition.name}(str, Enum):
${members}

    def __str__(self) -> str:
        return str(self.value)
`;
}

async function generateTypescriptEnumOverrides(enumDefinitions) {
  const generatedPath = resolve("packages/client-ts/src/client/generated.ts");
  const overridesPath = resolve("packages/client-ts/src/client/overrides.ts");
  const generatedContent = await readFile(generatedPath, "utf8");
  let content = await readFile(overridesPath, "utf8");
  const generated = enumDefinitions
    .filter(
      (enumDefinition) =>
        !typescriptClientExports(generatedContent, enumDefinition.name),
    )
    .map((enumDefinition) => renderTypescriptEnumOverride(enumDefinition))
    .join("\n");

  if (generated === "") {
    return;
  }

  content = `${content.trimEnd()}\n\n${generated}`;
  await writeFile(overridesPath, `${content}\n`);
}

function renderTypescriptEnumOverride(enumDefinition) {
  const members = enumDefinition.members
    .map((member) => `  ${member.value}: ${JSON.stringify(member.value)},`)
    .join("\n");

  return `export type ${enumDefinition.name} = typeof ${enumDefinition.name}[keyof typeof ${enumDefinition.name}];

export const ${enumDefinition.name} = {
${members}
} as const;
`;
}

function pythonModelsInitExports(modelsInit, name) {
  return new RegExp(
    `^from \\.${pythonModuleName(name)} import ${name}$`,
    "m",
  ).test(modelsInit);
}

function typescriptClientExports(content, name) {
  return new RegExp(
    `^export (?:type|const) ${escapeRegExp(name)}\\b`,
    "m",
  ).test(content);
}

async function generateSchemaMetadata() {
  const openapiPath = resolve("packages/contracts/openapi.json");
  const openapi = JSON.parse(await readFile(openapiPath, "utf8"));
  const metadata = extractSchemaMetadata(openapi);

  await writeFile(
    resolve("packages/client-ts/src/client/schema_metadata.ts"),
    renderTypescriptSchemaMetadata(metadata),
  );
  await writeFile(
    resolve("packages/client-py/api_client/schema_metadata.py"),
    renderPythonSchemaMetadata(metadata),
  );
}

function extractSchemaMetadata(openapi) {
  const schemas = openapi.components?.schemas ?? {};
  const schemaFields = {};

  for (const [schemaName, schema] of Object.entries(schemas)) {
    const fields = Object.fromEntries(
      Object.entries(schema.properties ?? {})
        .map(([propertyName, property]) => [
          propertyName,
          schemaFieldMetadata(property, schemas),
        ])
        .filter(([, metadata]) => Object.keys(metadata).length > 0),
    );

    if (Object.keys(fields).length > 0) {
      schemaFields[schemaName] = fields;
    }
  }

  return {
    schemaFields: sortNestedObject(schemaFields),
  };
}

function schemaFieldMetadata(property, schemas) {
  return Object.fromEntries(
    [
      [
        "title",
        // Pydantic can omit a property-level title when a $ref field's title
        // matches the referenced schema title, so fall back to the component.
        typeof property.description === "string"
          ? (property.title ?? referencedSchemaTitle(property, schemas))
          : undefined,
      ],
      [
        "description",
        typeof property.description === "string"
          ? property.description
          : undefined,
      ],
    ].filter(([, value]) => typeof value === "string"),
  );
}

function referencedSchemaTitle(property, schemas) {
  const ref = property.$ref;
  if (typeof ref !== "string") {
    return undefined;
  }

  const schemaName = componentNameFromRef(ref);
  const title = schemas[schemaName]?.title;
  return typeof title === "string" ? title : undefined;
}

function sortNestedObject(value) {
  if (!isPlainObject(value)) {
    return value;
  }

  return Object.fromEntries(
    Object.entries(value)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, entry]) => [key, sortNestedObject(entry)]),
  );
}

function renderTypescriptSchemaMetadata(metadata) {
  return `export interface SchemaFieldMetadata {
  title?: string;
  description?: string;
}

export type SchemaFields = Record<string, Record<string, SchemaFieldMetadata>>;

export const schemaFields = ${JSON.stringify(metadata.schemaFields, null, 2)} as const satisfies SchemaFields;
`;
}

function renderPythonSchemaMetadata(metadata) {
  return `SCHEMA_FIELDS: dict[str, dict[str, dict[str, str]]] = ${JSON.stringify(metadata.schemaFields, null, 4)}
`;
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

  await exportPythonModelSymbols(modelsInitPath, aliases);
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

async function exportPythonModelSymbols(modelsInitPath, symbols) {
  let content = await readFile(modelsInitPath, "utf8");
  content = addPythonModelImports(content, symbols);
  content = addPythonModelAllEntries(content, symbols);
  await writeFile(modelsInitPath, content);
}

function addPythonModelImports(content, symbols) {
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

  for (const symbol of symbols) {
    imports.add(`from .${pythonModuleName(symbol.name)} import ${symbol.name}`);
  }

  const sortedImports = [...imports].sort((left, right) =>
    left.localeCompare(right),
  );
  return content.replace(
    importBlock[0],
    `${importBlock.groups.header}${sortedImports.join("\n")}\n${importBlock.groups.footer}`,
  );
}

function addPythonModelAllEntries(content, symbols) {
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

  for (const symbol of symbols) {
    entries.add(`"${symbol.name}",`);
  }

  const sortedEntries = [...entries].sort((left, right) =>
    left.localeCompare(right),
  );
  return content.replace(
    allBlock[0],
    `${allBlock.groups.header}${sortedEntries.map((entry) => `    ${entry}`).join("\n")}\n${allBlock.groups.footer}`,
  );
}
