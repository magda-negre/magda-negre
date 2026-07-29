// Contenido y publicación de la web de Magda Negre.
// El contenido publicado vive en content.json (en el repositorio de GitHub).
// Las ediciones sin publicar viven en localStorage como "borrador".

export const REPO_OWNER = 'magda-negre';
export const REPO_NAME = 'magda-negre';
export const BRANCH = 'main';

const EDIT_CODE = 'magda2026';
const DRAFT_KEY = 'mn_draft';
const TOKEN_KEY = 'mn_token';
const EDITMODE_KEY = 'mn_editmode';

export const DEFAULT_CONTENT = {
  author: {
    name: 'Magda Negre',
    tagline: 'Escritora y escultora',
    bio: 'Soy de Barcelona aunque con doble nacionalidad franco-española. Cursé mis estudios superiores en la UB, primero con una licenciatura de Psicología y, unos años más tarde, la de Prehistoria e Historia Antigua, arqueología como me gusta llamarla. También cursé los dos años de doctorado en el departamento de Evolución Humana, con unos directores de tesis tan increíbles como el Dr. Jordi Sabater Pi y el Dr. Camilo José Cela Conde.\n\nTodo esto no fue óbice para que, aparte de trabajos que realicé en lo que se ceñía a mi formación, siempre me gustara escribir y por supuesto el mundo del arte, del que viví rodeada en mi infancia por motivos familiares. La escritura y la escultura son mis grandes aficiones actualmente y este es el motivo de esta página, poder compartir con los demás lo que yo he disfrutado tanto creando.',
    email: 'magda.negre@gmail.com',
    photo: '',
  },
  amazonUrl: 'https://www.amazon.es/punta-iceberg-Magda-Negre-Chauveau/dp/8418854340',
  amazonLabel: 'Comprar «La punta del iceberg» en Amazon',
  novelas: [],
  cuentos: [],
  misterio: [],
  arte: [],
};

export const SECTION_WORDS = {
  novelas: { singular: 'novela', plural: 'novelas', title: 'Novelas', subtitle: 'Narración larga', back: '← Todas las novelas' },
  cuentos: { singular: 'cuento', plural: 'cuentos', title: 'Cuentos', subtitle: 'Narrativa breve', back: '← Todos los cuentos' },
  misterio: { singular: 'relato', plural: 'relatos', title: 'Relatos de misterio', subtitle: 'Historias de intriga y misterio', back: '← Todos los relatos' },
};

export const PALETTE = {
  bg: '#f6f1e7', elevated: '#efe6d6', card: '#e9ded0',
  text: '#2b2420', textSoft: '#4a4038', muted: '#8a7d6c',
  divider: 'rgba(43,36,32,0.14)', borderStrong: 'rgba(43,36,32,0.28)',
  navBg: 'rgba(246,241,231,0.9)', accent: '#a15a3a', accentText: '#f6f1e7',
};

export function uid() {
  return Math.random().toString(36).slice(2, 9);
}

function normalize(c) {
  const out = { ...DEFAULT_CONTENT, ...(c || {}) };
  out.author = { ...DEFAULT_CONTENT.author, ...(c && c.author ? c.author : {}) };
  for (const k of ['novelas', 'cuentos', 'misterio', 'arte']) {
    out[k] = Array.isArray(out[k]) ? out[k] : [];
  }
  return out;
}

export async function fetchPublished() {
  try {
    const res = await fetch('./content.json?t=' + Date.now(), { cache: 'no-store' });
    if (!res.ok) return null;
    return normalize(await res.json());
  } catch (e) {
    return null;
  }
}

export function loadDraft() {
  try {
    const raw = localStorage.getItem(DRAFT_KEY);
    return raw ? normalize(JSON.parse(raw)) : null;
  } catch (e) {
    return null;
  }
}
export function saveDraft(content) {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(content));
  } catch (e) {
    // localStorage lleno (fotos grandes): avisamos pero no rompemos la edición
    console.warn('No se pudo guardar el borrador local:', e);
  }
}
export function clearDraft() {
  localStorage.removeItem(DRAFT_KEY);
}

/** Devuelve { content, hasDraft, online } */
export async function loadContent() {
  const published = await fetchPublished();
  const base = published || normalize(DEFAULT_CONTENT);
  const draft = loadDraft();
  return { content: draft || base, hasDraft: !!draft, online: !!published };
}

export function loadEditMode() {
  return localStorage.getItem(EDITMODE_KEY) === '1';
}
export function saveEditMode(v) {
  localStorage.setItem(EDITMODE_KEY, v ? '1' : '0');
}
export function verifyEditCode(code) {
  return code === EDIT_CODE;
}

export function loadToken() {
  return localStorage.getItem(TOKEN_KEY) || '';
}
export function saveToken(t) {
  localStorage.setItem(TOKEN_KEY, t);
}
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

/** Redimensiona y comprime una imagen a JPEG para que el repositorio no engorde. */
export function fileToDataUrl(file, maxSide = 1600) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error('No se pudo leer el archivo.'));
    reader.onload = () => {
      const img = new Image();
      img.onerror = () => reject(new Error('El archivo no es una imagen válida.'));
      img.onload = () => {
        const scale = Math.min(1, maxSide / Math.max(img.width, img.height));
        const w = Math.round(img.width * scale);
        const h = Math.round(img.height * scale);
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, w, h);
        ctx.drawImage(img, 0, 0, w, h);
        resolve(canvas.toDataURL('image/jpeg', 0.85));
      };
      img.src = reader.result;
    };
    reader.readAsDataURL(file);
  });
}

function bytesToBase64(bytes) {
  let bin = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    bin += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
  }
  return btoa(bin);
}
function utf8ToBase64(str) {
  return bytesToBase64(new TextEncoder().encode(str));
}

async function gh(path, token, opts) {
  const res = await fetch('https://api.github.com/repos/' + REPO_OWNER + '/' + REPO_NAME + '/' + path, {
    ...(opts || {}),
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      ...((opts && opts.headers) || {}),
    },
  });
  return res;
}

async function getSha(path, token) {
  const res = await gh('contents/' + path + '?ref=' + BRANCH, token);
  if (res.status === 200) {
    const j = await res.json();
    return j.sha;
  }
  return null;
}

async function putFile(path, base64, token, message) {
  const sha = await getSha(path, token);
  const body = { message, content: base64, branch: BRANCH };
  if (sha) body.sha = sha;
  const res = await gh('contents/' + path, token, { method: 'PUT', body: JSON.stringify(body) });
  if (!res.ok) {
    let detail = '';
    try {
      const j = await res.json();
      detail = j.message || '';
    } catch (e) {}
    if (res.status === 401) throw new Error('Código de publicación no válido o caducado.');
    if (res.status === 403 || res.status === 404) throw new Error('El código no tiene permiso de escritura en el repositorio.');
    throw new Error('Error de GitHub (' + res.status + '): ' + detail);
  }
}

/** Comprueba que el token funciona antes de guardar nada. */
export async function verifyToken(token) {
  try {
    const res = await gh('', token);
    return res.ok;
  } catch (e) {
    throw new Error('No se pudo conectar con GitHub. Comprueba tu conexión.');
  }
}

function setDeep(obj, keys, value) {
  let cur = obj;
  for (let i = 0; i < keys.length - 1; i++) cur = cur[keys[i]];
  cur[keys[keys.length - 1]] = value;
}

/**
 * Sube las imágenes nuevas y guarda content.json en el repositorio.
 * onProgress(texto) para informar del avance.
 */
export async function publish(content, token, onProgress) {
  const out = normalize(JSON.parse(JSON.stringify(content)));
  const uploads = [];
  if (out.author.photo && out.author.photo.startsWith('data:')) {
    uploads.push({ keys: ['author', 'photo'], data: out.author.photo, base: 'autor' });
  }
  out.arte.forEach((a, i) => {
    if (a.image && a.image.startsWith('data:')) {
      uploads.push({ keys: ['arte', i, 'image'], data: a.image, base: 'obra-' + (a.id || i) });
    }
  });

  let n = 0;
  for (const up of uploads) {
    n += 1;
    onProgress && onProgress('Subiendo fotografía ' + n + ' de ' + uploads.length + '…');
    const m = up.data.match(/^data:image\/[a-z+.-]+;base64,(.*)$/);
    if (!m) continue;
    const path = 'assets/' + up.base + '-' + Date.now().toString(36) + '.jpg';
    await putFile(path, m[1], token, 'Subir fotografía ' + path);
    setDeep(out, up.keys, path);
  }

  onProgress && onProgress('Guardando el contenido…');
  await putFile('content.json', utf8ToBase64(JSON.stringify(out, null, 2)), token, 'Actualizar contenido de la web');
  clearDraft();
  return out;
}
