// Metro configuration for M2 smoke build.
// Adds the parent mobile/ directory to watchFolders so that
// ../PhraseSelectionReaderSheet can be resolved from inside mobile/app/.
//
// Traceability: docs/planning/sdd/phase-3-phrase-selection-sdd.md §12

const { getDefaultConfig } = require('expo/metro-config');
const path = require('path');

const projectRoot = __dirname;
const mobileRoot = path.resolve(projectRoot, '..');

const config = getDefaultConfig(projectRoot);

// Allow Metro to watch files outside the project root (../PhraseSelectionReaderSheet).
config.watchFolders = [mobileRoot];

// Files in mobileRoot have no node_modules of their own, so pin module
// resolution to the app's node_modules; otherwise `react`/`react-native`
// imports from ../PhraseSelectionReaderSheet fail to resolve.
config.resolver.nodeModulesPaths = [path.resolve(projectRoot, 'node_modules')];

module.exports = config;
