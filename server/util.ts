/** Return an object with keys (deeply) sorted. This work in practice but not in theory. */
export function sortKeys<T extends object>(o: T): T {
  const keys = Object.keys(o) as (keyof T)[];
  keys.sort();

  const res: Partial<T> = {};
  let k: keyof T;
  for (k of keys) {
    let v = o[k];
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      v = sortKeys(v);
    }
    res[k] = v;
  }

  return res as T;
}
