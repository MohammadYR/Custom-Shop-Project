/**
 * @type {import("@svgr/core").Config}
 */
export default {
  typescript: true,
  icon: true,
  prettier: false,
  index: false,
  jsxRuntime: "automatic",
  template: ({ componentName, imports, props, jsx }, { tpl }) => {
    return tpl`
        ${imports}
        \
        export const ${createComponentName(componentName)} = (${props}) => (
          ${jsx}
        );
      `;
  },
  replaceAttrValues: {
    "#EAEAEA": "currentColor",
  },
};

function createComponentName(oldName) {
  // Svgr add hardcode `Svg` prefix to component names
  return `${oldName.slice(3)}Icon`;
}
