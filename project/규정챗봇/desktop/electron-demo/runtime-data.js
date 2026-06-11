import fs from "node:fs";
import path from "node:path";

export function ensurePackagedRuntimeData(resourcesPath, userDataPath) {
  ensureSeedDatabase(resourcesPath, userDataPath);
}

function ensureSeedDatabase(resourcesPath, userDataPath) {
  const source = path.join(resourcesPath, "seed", "db.sqlite3");
  const target = path.join(userDataPath, "db.sqlite3");
  copyFileIfMissing(source, target);
}

function copyFileIfMissing(source, target) {
  if (!fs.existsSync(source) || fs.existsSync(target)) {
    return;
  }
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(source, target);
}
