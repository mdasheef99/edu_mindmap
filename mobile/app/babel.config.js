// Required by jest-expo so that Jest can apply the Expo Babel preset to all
// source files, including those outside the project root (mobile/ parent dir).
// Traceability: development-approach.md §7.6; SDD §12
module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
  };
};
