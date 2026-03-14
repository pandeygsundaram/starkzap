from __future__ import annotations

import hashlib
import random
from urllib.parse import quote

from app.models import AvatarFeatures

HORN_TYPES = ["twin ram", "blade crown", "crystal spike", "antenna arc"]
EYE_TYPES = ["ember slit", "neon orb", "holo visor", "storm lens"]
ARMOR_STYLES = ["titan plate", "carbon scales", "void shell", "brass lattice"]
COLORS = ["crimson", "teal", "gold", "obsidian", "jade", "azure"]
SIGILS = ["fang", "eclipse", "circuit", "rune"]


def _seeded_rng(agent_id: str) -> random.Random:
    digest = hashlib.sha256(agent_id.encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def generate_avatar(agent_id: str) -> AvatarFeatures:
    rng = _seeded_rng(agent_id)
    horn = rng.choice(HORN_TYPES)
    eyes = rng.choice(EYE_TYPES)
    armor = rng.choice(ARMOR_STYLES)
    color = rng.choice(COLORS)
    sigil = rng.choice(SIGILS)

    svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 320 320'>
      <rect width='320' height='320' rx='28' fill='#111827'/>
      <defs>
        <linearGradient id='bg' x1='0' x2='1' y1='0' y2='1'>
          <stop offset='0%' stop-color='{color}' />
          <stop offset='100%' stop-color='#0f172a' />
        </linearGradient>
      </defs>
      <rect x='12' y='12' width='296' height='296' rx='24' fill='url(#bg)' opacity='0.5'/>
      <path d='M75 96 L130 56 L115 116 Z' fill='white' opacity='0.8'/>
      <path d='M245 96 L190 56 L205 116 Z' fill='white' opacity='0.8'/>
      <ellipse cx='160' cy='172' rx='86' ry='94' fill='#1f2937' stroke='white' stroke-width='4'/>
      <ellipse cx='126' cy='160' rx='16' ry='12' fill='cyan'/>
      <ellipse cx='194' cy='160' rx='16' ry='12' fill='cyan'/>
      <path d='M130 214 Q160 238 190 214' stroke='white' stroke-width='5' fill='none'/>
      <text x='160' y='286' text-anchor='middle' fill='white' font-size='20' font-family='monospace'>
        {agent_id}
      </text>
    </svg>
    """.strip()

    return AvatarFeatures(
        horn_type=horn,
        eye_type=eyes,
        armor_style=armor,
        color=color,
        sigil=sigil,
        image=f"data:image/svg+xml;utf8,{quote(svg)}",
    )
