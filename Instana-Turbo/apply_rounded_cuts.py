# -*- coding: utf-8 -*-
import re

with open("projeto-sommelier/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update Spotlight image container
old_spotlight_img = """        <!-- Left: Bottle Stage with Radial Glow -->
        <div class="md:col-span-5 flex items-center justify-center relative py-4 sm:py-8 bottle-glow">
          <img src="/images/romanee.jpg" alt="Domaine de la Romanée-Conti 2017" class="h-64 sm:h-80 object-contain drop-shadow-[0_20px_35px_rgba(0,0,0,0.22)] transform hover:scale-105 transition-transform duration-700">
        </div>"""

new_spotlight_img = """        <!-- Left: Bottle Stage with Luxury Rounded Frame -->
        <div class="md:col-span-5 flex items-center justify-center relative p-1 sm:p-3">
          <div class="w-full h-72 sm:h-96 rounded-[32px] sm:rounded-[40px] bg-gradient-to-b from-white via-[#fcfaf5] to-[#f4ede0] border border-[#e5decb] p-3 sm:p-5 flex items-center justify-center relative overflow-hidden shadow-md group">
            <div class="absolute inset-0 bg-radial from-amber-100/40 via-transparent to-transparent pointer-events-none"></div>
            <div class="absolute top-3.5 left-3.5 px-3 py-1 rounded-full bg-white/95 backdrop-blur-md border border-[#e5decb] text-[10px] sm:text-[11px] font-bold text-[#b8860b] shadow-xs flex items-center space-x-1.5 z-10">
              <i data-lucide="crown" class="w-3.5 h-3.5"></i>
              <span>Obra-Prima Nº 1</span>
            </div>
            <img src="/images/romanee.jpg" alt="Domaine de la Romanée-Conti 2017" class="h-full w-full object-contain rounded-[26px] sm:rounded-[32px] drop-shadow-[0_20px_36px_rgba(0,0,0,0.22)] transform group-hover:scale-105 transition-transform duration-700">
          </div>
        </div>"""

html = html.replace(old_spotlight_img, new_spotlight_img)

# 2. Update each of the 6 wine cards with rounded showcase frames
cards_data = [
    {
        "old_marker": '<img src="/images/romanee.jpg" alt="Romanée-Conti"',
        "vintage": "Safra 2017",
        "alt": "Domaine de la Romanée-Conti",
        "src": "/images/romanee.jpg"
    },
    {
        "old_marker": '<img src="/images/petrus.jpg" alt="Château Pétrus"',
        "vintage": "Safra 2010",
        "alt": "Château Pétrus Pomerol",
        "src": "/images/petrus.jpg"
    },
    {
        "old_marker": '<img src="/images/margaux.jpg" alt="Château Margaux"',
        "vintage": "Safra 2015",
        "alt": "Château Margaux 1er Cru",
        "src": "/images/margaux.jpg"
    },
    {
        "old_marker": '<img src="/images/sassicaia.jpg" alt="Sassicaia"',
        "vintage": "Safra 2016",
        "alt": "Tenuta San Guido Sassicaia",
        "src": "/images/sassicaia.jpg"
    },
    {
        "old_marker": '<img src="/images/vegasicilia.jpg" alt="Vega Sicilia"',
        "vintage": "Safra 2000",
        "alt": "Vega Sicilia Único Reserva",
        "src": "/images/vegasicilia.jpg"
    },
    {
        "old_marker": '<img src="/images/perignon.jpg" alt="Dom Pérignon P2"',
        "vintage": "Safra 2004",
        "alt": "Dom Pérignon P2 Brut",
        "src": "/images/perignon.jpg"
    }
]

for c in cards_data:
    # Pattern matching the bottle-glow container
    pat = r'<div class="my-4 h-56 flex items-center justify-center relative bottle-glow">\s*' + re.escape(c["old_marker"]) + r'[^>]*>\s*</div>'
    replacement = f"""<div class="my-3.5 h-60 sm:h-64 rounded-[26px] sm:rounded-[30px] bg-gradient-to-b from-[#fafafc] via-[#f4f4f7] to-[#ebebf0] border border-[#e5e5e7] p-3 sm:p-4 flex items-center justify-center relative overflow-hidden shadow-[inset_0_2px_6px_rgba(0,0,0,0.03)] group-hover:border-[#c5a059]/40 group-hover:shadow-md transition-all duration-500">
            <div class="absolute inset-0 bg-radial from-white/90 via-transparent to-black/[0.02] pointer-events-none"></div>
            <span class="absolute top-3 left-3 px-2.5 py-0.5 rounded-full bg-white/95 backdrop-blur-md border border-white/70 text-[9px] font-mono font-semibold text-[#1d1d1f] shadow-2xs z-10">
              {c["vintage"]}
            </span>
            <img src="{c["src"]}" alt="{c["alt"]}" class="h-full w-full object-contain rounded-[20px] sm:rounded-[24px] drop-shadow-[0_14px_24px_rgba(0,0,0,0.16)] group-hover:scale-105 transition-transform duration-500 ease-out">
          </div>"""
    html = re.sub(pat, replacement, html)

# 3. Update Modal Dossier to display the bottle in an elegant rounded frame
old_dossier_header = """      <!-- Dossier Header -->
      <div class="flex items-start justify-between border-b border-[#e5e5e7] pb-4">
        <div>
          <span id="dossier-appellation" class="text-[11px] font-bold text-[#b8860b] uppercase tracking-wider block"></span>
          <h3 id="dossier-title" class="font-serif font-bold text-xl sm:text-2xl text-[#1d1d1f] tracking-tight mt-0.5"></h3>
          <span id="dossier-vintage" class="text-xs text-[#6e6e73]"></span>
        </div>
        <button onclick="closeWineDossier()" class="w-8 h-8 rounded-full bg-[#f5f5f7] hover:bg-[#e8e8ed] flex items-center justify-center text-[#6e6e73] hover:text-[#1d1d1f]">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>"""

new_dossier_header = """      <!-- Dossier Header with Rounded Bottle Capsule -->
      <div class="flex items-start justify-between border-b border-[#e5e5e7] pb-4">
        <div class="flex items-center space-x-3.5 min-w-0">
          <div class="w-16 h-22 sm:w-20 sm:h-28 rounded-[20px] sm:rounded-[24px] bg-gradient-to-b from-[#fafafc] to-[#ebebf0] border border-[#e5e5e7] p-1.5 flex items-center justify-center overflow-hidden flex-shrink-0 shadow-xs">
            <img id="dossier-img" src="/images/romanee.jpg" alt="Vinho" class="h-full w-full object-contain rounded-[16px] drop-shadow-sm">
          </div>
          <div class="truncate">
            <span id="dossier-appellation" class="text-[10px] sm:text-[11px] font-bold text-[#b8860b] uppercase tracking-wider block truncate"></span>
            <h3 id="dossier-title" class="font-serif font-bold text-lg sm:text-2xl text-[#1d1d1f] tracking-tight mt-0.5 truncate"></h3>
            <span id="dossier-vintage" class="text-xs text-[#6e6e73] block truncate"></span>
          </div>
        </div>
        <button onclick="closeWineDossier()" class="w-8 h-8 rounded-full bg-[#f5f5f7] hover:bg-[#e8e8ed] flex items-center justify-center text-[#6e6e73] hover:text-[#1d1d1f] flex-shrink-0 ml-2">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>"""

html = html.replace(old_dossier_header, new_dossier_header)

# 4. In openWineDetails JS, also set dossier-img src
old_dossier_js = """    function openWineDetails(key) {
      const wine = wineCatalog[key];
      selectedWineKey = key;

      document.getElementById('dossier-appellation').textContent = wine.appellation;"""

new_dossier_js = """    function openWineDetails(key) {
      const wine = wineCatalog[key];
      selectedWineKey = key;

      const dImg = document.getElementById('dossier-img');
      if (dImg) dImg.src = wine.image;
      document.getElementById('dossier-appellation').textContent = wine.appellation;"""

html = html.replace(old_dossier_js, new_dossier_js)

# 5. In CSS, add custom class for ultra-smooth squircle clipping
squircle_css = """
    /* Apple Squircle Product Frame */
    .apple-photo-squircle {
      border-radius: 28px;
      overflow: hidden;
      mask-image: -webkit-radial-gradient(white, black);
      -webkit-mask-image: -webkit-radial-gradient(white, black);
    }
"""
if "apple-photo-squircle" not in html:
    html = html.replace("</style>", squircle_css + "\n  </style>")

with open("projeto-sommelier/index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Updated index.html with rounded image cuts and luxury frames!")
