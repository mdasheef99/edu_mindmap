// Metro configuration for M2 smoke build.
// Adds the parent mobile/ directory to watchFolders so that
// ../PhraseSelectionReaderSheet can be resolved from inside mobile/app/.
//
// Traceability: docs/planning/sdd/phase-3-phrase-selection-sdd.md §12

const { getDefaultConfig } = require('expo/metro-config');
const fs = require('fs');
const path = require('path');

const projectRoot = __dirname;
const mobileRoot = path.resolve(projectRoot, '..');

const config = getDefaultConfig(projectRoot);

// Allow Metro to watch the complete mobile source tree.
config.watchFolders = [mobileRoot];

// Expo remains rooted at app/ for entry and asset URLs. On Windows, Metro's
// default resolver does not reliably discover relative source files above that
// root even when they are watched, so resolve only those known sibling sources.
config.resolver.resolveRequest = (context, moduleName, platform) => {
  if (moduleName.startsWith('.')) {
    const base = path.resolve(path.dirname(context.originModulePath), moduleName);
    const withinMobile = !path.relative(mobileRoot, base).startsWith('..');
    const outsideApp = path.relative(projectRoot, base).startsWith('..');
    if (withinMobile && outsideApp) {
      const variants = platform
        ? [`.${platform}.ts`, `.${platform}.tsx`, '.native.ts', '.native.tsx', '.ts', '.tsx', '.js']
        : ['.ts', '.tsx', '.js'];
      const candidates = [base, ...variants.map((suffix) => `${base}${suffix}`)];
      for (const candidate of candidates) {
        if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
          return { filePath: candidate, type: 'sourceFile' };
        }
      }
    }
  }
  return context.resolveRequest(context, moduleName, platform);
};

// Files in mobileRoot have no node_modules of their own, so pin module
// resolution to the app's node_modules; otherwise `react`/`react-native`
// imports from ../PhraseSelectionReaderSheet fail to resolve.
config.resolver.nodeModulesPaths = [path.resolve(projectRoot, 'node_modules')];

module.exports = config;
