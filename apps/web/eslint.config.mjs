import coreWebVitals from 'eslint-config-next/core-web-vitals'
import nextTypescript from 'eslint-config-next/typescript'

export default [
  {
    ignores: ['public/sw.js', 'public/workbox-*.js', 'next.config.js'],
  },
  ...coreWebVitals,
  ...nextTypescript,
]
