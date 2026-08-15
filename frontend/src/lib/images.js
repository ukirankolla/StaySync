const U = (id, w = 900) =>
  `https://images.unsplash.com/${id}?auto=format&fit=crop&w=${w}&q=80`

export const IMG = {
  hero: U('photo-1493809842364-78817add7ffb', 1800),
  heroAlt: U('photo-1522708323590-d24dbb6b0267', 1800),
  city: U('photo-1477959858617-67f85cf4f1df', 1800),
  group: U('photo-1543269865-cbf427effbad', 900),
  friends: U('photo-1511632765486-a01980e01a18', 900),
  team: U('photo-1522071820081-009f0129c71c', 900),
  crowd: U('photo-1529156069898-49953e39b3ac', 900),
  chat: U('photo-1521791136064-7986c2920216', 900),
  plan: U('photo-1531482615713-2afd69097998', 900),
  office: U('photo-1529333166437-7750a6dd5a70', 900),
  home: U('photo-1560518883-ce09059eeffa', 900),
}

export const PORTRAITS = [
  'photo-1507003211169-0a1dd7228f2d',
  'photo-1494790108377-be9c29b29330',
  'photo-1500648767791-00dcc994a43e',
  'photo-1438761681033-6461ffad8d80',
  'photo-1573496359142-b8d87734a5a2',
  'photo-1534528741775-53994a69daeb',
  'photo-1506794778202-cad84cf45f1d',
  'photo-1544005313-94ddf0286df2',
  'photo-1517841905240-472988babdf9',
  'photo-1527980965255-d3b416303d12',
]

const ROOMS = {
  chennai: 'photo-1522708323590-d24dbb6b0267',
  bengaluru: 'photo-1493809842364-78817add7ffb',
  hyderabad: 'photo-1513694203232-719a280e022f',
  pune: 'photo-1567016432779-094069958ea5',
  delhi: 'photo-1502672260266-1c1ef2d93688',
  mumbai: 'photo-1560448204-e02f11c3d0e2',
  kolkata: 'photo-1524758631624-e2822e304c36',
  default: 'photo-1524758631624-e2822e304c36',
}

export function roomImage(city = '') {
  const key = (city || '').toLowerCase().replace(/[^a-z]/g, '')
  const id = ROOMS[key] || ROOMS.default
  return U(id, 900)
}

const GRADIENTS = [
  ['#4f46e5', '#0ea5e9'],
  ['#9333ea', '#db2777'],
  ['#0ea5e9', '#10b981'],
  ['#f59e0b', '#ef4444'],
  ['#6366f1', '#8b5cf6'],
  ['#0d9488', '#2563eb'],
  ['#e11d48', '#7c3aed'],
]

export function avatarGradient(name = '') {
  let h = 0
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0
  const [a, b] = GRADIENTS[h % GRADIENTS.length]
  return `linear-gradient(135deg, ${a}, ${b})`
}

export function initials(name = 'U') {
  return name
    .split(' ')
    .filter(Boolean)
    .map((s) => s[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
