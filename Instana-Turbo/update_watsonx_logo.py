# -*- coding: utf-8 -*-
import re

with open('projeto-sommelier/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

WATSONX_PATH_D = (
    "m29.312,22.9189c1.1042-2.1201,1.688-4.5127,1.688-6.9189C31,7.729,24.271,1,16,1"
    "c-3.3738,0-6.5815,1.1191-9.2046,3.1665-.2441-.106-.5125-.1665-.7954-.1665"
    "-1.1045,0-2,.8955-2,2s.8955,2,2,2,2-.8955,2-2c0-.0762-.0142-.1489-.0225-.2227"
    ",2.2812-1.7964,5.0793-2.7773,8.0225-2.7773.9727,0,1.9172.1157,2.8293.3193"
    "-3.3938.9258-5.8994,4.0273-5.8994,7.7109,0,.7891.1167,1.5503.332,2.27"
    "-.6985-.2021-1.4285-.3306-2.1919-.3306-3.7039,0-6.8191,2.5342-7.7256,5.957"
    "-.218-.9424-.3445-1.9189-.3445-2.9268,0-2.1162.4919-4.1328,1.4619-5.9951l-1.7739-.9238"
    "c-1.1042,2.1201-1.688,4.5127-1.688,6.9189,0,8.271,6.729,15,15,15,3.3738,0,6.5815-1.1191"
    ",9.2046-3.1665.2441.106.5125.1665.7954.1665,1.1045,0,2-.8955,2-2s-.8955-2-2-2"
    "-2,.8955-2,2c0,.0762.0142.1489.0225.2231-1.0796.8496-2.2776,1.5098-3.5493,1.9771"
    ".3315-.6641.5269-1.4072.5269-2.2002,0-1.6304-.7959-3.0669-2.0068-3.9805"
    ".0457-.3472.0769-.6978.0769-1.0498,0-.7856-.1257-1.54-.3381-2.2573"
    ".6995.2012,1.4346.3179,2.198.3179,3.7039,0,6.8191-2.5342,7.7256-5.957"
    ".218.9424.3445,1.9189.3445,2.9268,0,2.1162-.4919,4.1328-1.4619,5.9951l1.7739.9238Zm-17.7935,5.2646"
    "c-1.8389-.6807-3.49-1.7529-4.8325-3.1338-1.0366-1.1143-1.616-2.5527-1.616-4.0801"
    ",0-3.3081,2.6917-6,6-6s6,2.6919,6,6c0,.0498-.0125.0977-.0134.1475"
    "-.3413-.0737-.6936-.1172-1.0566-.1172-2.7571,0-5,2.2432-5,5,0,.7861.1924,1.5234.5186,2.1836Zm7.4814-2.1836"
    "c0,1.6543-1.3457,3-3,3s-3-1.3457-3-3,1.3457-3,3-3,3,1.3457,3,3Zm1.9299-8.9697"
    "c-3.3083,0-6-2.6919-6-6s2.6917-6,6-6c1.4294,0,2.7422.5039,3.7742,1.3418"
    ".3027.2739.5918.561.8677.8618.8479,1.0352,1.3582,2.3569,1.3582,3.7964,0,3.3081-2.6917,6-6,6Z"
)

# 1. Replace the Floating Trigger Button
old_trigger_pattern = re.compile(
    r'<button onclick="toggleSommelierChat\(\)" id="sommelier-trigger-btn".*?</button>',
    re.DOTALL
)

new_trigger_html = f'''<button onclick="toggleSommelierChat()" id="sommelier-trigger-btn" class="flex items-center space-x-2.5 sm:space-x-3 px-3.5 sm:px-5 py-2.5 sm:py-3.5 rounded-full bg-white text-[#1d1d1f] border border-[#d2d2d7] shadow-xl hover:shadow-2xl hover:border-[#0f62fe] hover:scale-105 transition-all group">
      <div class="relative flex-shrink-0">
        <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gradient-to-tr from-[#0f62fe] via-[#8a3ffc] to-[#ff7eb6] p-[2px] shadow-sm flex items-center justify-center">
          <div class="w-full h-full bg-[#12161f] rounded-full p-1.5 flex items-center justify-center">
            <svg class="w-full h-full" viewBox="0 0 32 32" fill="none">
              <defs>
                <linearGradient id="wx-trig-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#4589ff"/>
                  <stop offset="50%" stop-color="#a56eff"/>
                  <stop offset="100%" stop-color="#ff7eb6"/>
                </linearGradient>
              </defs>
              <path fill="url(#wx-trig-grad)" d="{WATSONX_PATH_D}"/>
            </svg>
          </div>
        </div>
        <span class="absolute -top-0.5 -right-0.5 w-3 h-3 rounded-full bg-[#34c759] border-2 border-white animate-pulse"></span>
      </div>
      <div class="text-left">
        <div class="flex items-center space-x-1.5">
          <span class="text-xs sm:text-sm font-bold block leading-tight text-[#1d1d1f]">Sommelier</span>
          <span class="text-[8px] sm:text-[9px] font-bold px-1.5 py-0.2 rounded bg-[#0f62fe]/10 text-[#0f62fe] uppercase tracking-wider">watsonx</span>
        </div>
        <span class="text-[10px] sm:text-[11px] text-[#6e6e73] block leading-tight">Consultoria de Vinhos</span>
      </div>
    </button>'''

content, count1 = old_trigger_pattern.subn(new_trigger_html, content)
print(f"Replaced trigger pill: {count1} times")

# 2. Replace Chat Header Avatar and Title
old_header_avatar_pattern = re.compile(
    r'<div class="relative flex-shrink-0">\s*<div class="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-\[#12161f\].*?</div>\s*<span class="absolute bottom-0 right-0 w-2\.5 h-2\.5 rounded-full bg-\[#34c759\] border-2 border-white"></span>\s*</div>',
    re.DOTALL
)

new_header_avatar_html = f'''<div class="relative flex-shrink-0">
            <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gradient-to-tr from-[#0f62fe] via-[#8a3ffc] to-[#ff7eb6] p-[2px] shadow-sm flex items-center justify-center">
              <div class="w-full h-full bg-[#12161f] rounded-full p-1.5 flex items-center justify-center">
                <svg class="w-full h-full" viewBox="0 0 32 32" fill="none">
                  <defs>
                    <linearGradient id="wx-chat-hdr-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stop-color="#4589ff"/>
                      <stop offset="50%" stop-color="#a56eff"/>
                      <stop offset="100%" stop-color="#ff7eb6"/>
                    </linearGradient>
                  </defs>
                  <path fill="url(#wx-chat-hdr-grad)" d="{WATSONX_PATH_D}"/>
                </svg>
              </div>
            </div>
            <span class="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-[#34c759] border-2 border-white"></span>
          </div>'''

content, count2 = old_header_avatar_pattern.subn(new_header_avatar_html, content)
print(f"Replaced header avatar: {count2} times")

# 3. Replace Welcome Bubble Avatar
old_welcome_avatar_pattern = re.compile(
    r'<div class="w-7 h-7 rounded-full bg-\[#12161f\].*?id="wx-welc-grad".*?</svg>\s*</div>',
    re.DOTALL
)

new_welcome_avatar_html = f'''<div class="w-7 h-7 rounded-full bg-gradient-to-tr from-[#0f62fe] via-[#8a3ffc] to-[#ff7eb6] p-[1.5px] flex-shrink-0 shadow-sm mt-0.5 flex items-center justify-center">
            <div class="w-full h-full bg-[#12161f] rounded-full p-1 flex items-center justify-center">
              <svg class="w-full h-full" viewBox="0 0 32 32" fill="none">
                <defs>
                  <linearGradient id="wx-welc-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#4589ff"/>
                    <stop offset="50%" stop-color="#a56eff"/>
                    <stop offset="100%" stop-color="#ff7eb6"/>
                  </linearGradient>
                </defs>
                <path fill="url(#wx-welc-grad)" d="{WATSONX_PATH_D}"/>
              </svg>
            </div>
          </div>'''

content, count3 = old_welcome_avatar_pattern.subn(new_welcome_avatar_html, content)
print(f"Replaced welcome avatar: {count3} times")

# 4. Replace WX_AVATAR_HTML in JavaScript
old_js_avatar_pattern = re.compile(
    r'const WX_AVATAR_HTML = `.*?`;',
    re.DOTALL
)

new_js_avatar_html = f'''const WX_AVATAR_HTML = `
      <div class="w-7 h-7 rounded-full bg-gradient-to-tr from-[#0f62fe] via-[#8a3ffc] to-[#ff7eb6] p-[1.5px] flex-shrink-0 shadow-sm mt-0.5 flex items-center justify-center">
        <div class="w-full h-full bg-[#12161f] rounded-full p-1 flex items-center justify-center">
          <svg class="w-full h-full" viewBox="0 0 32 32" fill="none">
            <defs>
              <linearGradient id="wx-msg-dyn-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#4589ff"/>
                <stop offset="50%" stop-color="#a56eff"/>
                <stop offset="100%" stop-color="#ff7eb6"/>
              </linearGradient>
            </defs>
            <path fill="url(#wx-msg-dyn-grad)" d="{WATSONX_PATH_D}"/>
          </svg>
        </div>
      </div>
    `;'''

content, count4 = old_js_avatar_pattern.subn(new_js_avatar_html, content)
print(f"Replaced JS avatar: {count4} times")

# Also ensure Chat Header Title has watsonx badge
header_title_old = '<span class="text-[9px] font-medium bg-[#f5f5f7] text-[#0071e3] px-2 py-0.5 rounded-full border border-[#e5e5e7]">IA Especialista</span>'
header_title_new = '<span class="text-[9px] font-bold px-1.5 py-0.2 rounded bg-[#0f62fe]/10 text-[#0f62fe] uppercase tracking-wider">watsonx</span><span class="text-[9px] font-medium bg-[#f5f5f7] text-[#525252] px-2 py-0.5 rounded-full border border-[#e5e5e7]">IA Especialista</span>'
if header_title_old in content:
    content = content.replace(header_title_old, header_title_new, 1)
    print("Added watsonx badge to chat header title")

with open('projeto-sommelier/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Update completed successfully!")
