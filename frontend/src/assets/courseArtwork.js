export function courseArtwork(thumbnail) {
  if (!thumbnail) return thumbnail
  const normalized = String(thumbnail).replace(/\\/g, '/').replace(/\.(?:jpe?g)$/i, '.svg')
  if (typeof __VITE_SERVE__ !== 'undefined' && __VITE_SERVE__) {
    return normalized.replace(/^\/?static\//, '/')
  }
  return /^https?:\/\//i.test(normalized) || normalized.startsWith('/') ? normalized : `/${normalized}`
}
