import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { canonicalJSON, buildManifest, validateManifest, runContractTests } from "./manifest_contract.mjs";

const baseline = new URL("../../docs/asset_inventory_baseline.json", import.meta.url);
const output = new URL("../../assets/catalog/manifest.json", import.meta.url);
const inv = JSON.parse(readFileSync(baseline, "utf8"));
const manifest = buildManifest(inv);
const counts = validateManifest(manifest, inv);
const tests = runContractTests(inv);
const expected = canonicalJSON(manifest);
if (process.argv.includes("--write")) {
    writeFileSync(fileURLToPath(output), expected);
} else if (readFileSync(output, "utf8") !== expected) {
    throw new Error("Manifest differs from baseline; regenerate with --write");
}
console.log("ASSET_MANIFEST_CONTRACT_PASS", JSON.stringify(counts), tests.length + " tests");
