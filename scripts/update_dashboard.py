with open('petron_dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Update date if present
text = text.replace('02/09/2026', '03/09/2026')
text = text.replace('Wednesday 02/09/2026', 'Thursday 03/09/2026')

old_tbody_start = text.find('<tbody class="divide-y divide-slate-100 text-slate-700 font-mono">')
old_tbody_end = text.find('</tbody>', old_tbody_start) + len('</tbody>')

new_tbody = '''<tbody class="divide-y divide-slate-100 text-slate-700 font-mono">
            <!-- POS 1 S1 -->
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-bold text-slate-900 font-sans">POS 1 - Shift 1</td>
              <td class="p-3 font-semibold text-emerald-700 font-sans">GIASSUDDIN</td>
              <td class="p-3 text-right">2,546.20</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-right">2,546.20</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[11px] bg-emerald-100 text-emerald-800 font-bold">0.00</span></td>
              <td class="p-3 text-center"><span class="text-emerald-600 font-bold font-sans">BALANCED</span></td>
            </tr>
            <!-- POS 1 S2 -->
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-bold text-slate-900 font-sans">POS 1 - Shift 2</td>
              <td class="p-3 font-semibold text-emerald-700 font-sans">KAWSAR / IQHMAL</td>
              <td class="p-3 text-right">14,219.10</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-right">14,219.10</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[11px] bg-emerald-100 text-emerald-800 font-bold">0.00</span></td>
              <td class="p-3 text-center"><span class="text-emerald-600 font-bold font-sans">BALANCED</span></td>
            </tr>
            <!-- POS 2 S1 -->
            <tr class="hover:bg-slate-50 bg-emerald-50/20">
              <td class="p-3 font-bold text-slate-900 font-sans">POS 2 - Shift 1</td>
              <td class="p-3 font-semibold text-emerald-700 font-sans">WINA / KAWSAR / IQHMAL</td>
              <td class="p-3 text-right">8,198.35</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-right">8,198.35</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[11px] bg-emerald-100 text-emerald-800 font-bold">0.00</span></td>
              <td class="p-3 text-center"><span class="text-emerald-600 font-bold font-sans">BALANCED</span></td>
            </tr>
            <!-- POS 2 S2 -->
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-bold text-slate-900 font-sans">POS 2 - Shift 2</td>
              <td class="p-3 font-semibold text-emerald-700 font-sans">KAOSAR / IQHMAL</td>
              <td class="p-3 text-right">3,986.15</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-right">3,986.15</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[11px] bg-emerald-100 text-emerald-800 font-bold">0.00</span></td>
              <td class="p-3 text-center"><span class="text-emerald-600 font-bold font-sans">BALANCED</span></td>
            </tr>
            <!-- POS 3 S1 -->
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-bold text-slate-900 font-sans">POS 3 - Shift 1</td>
              <td class="p-3 font-semibold text-emerald-700 font-sans">GIASSUDDIN / KAOSAR / WINA</td>
              <td class="p-3 text-right">12,839.90</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-right">12,839.90</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[11px] bg-emerald-100 text-emerald-800 font-bold">0.00</span></td>
              <td class="p-3 text-center"><span class="text-emerald-600 font-bold font-sans">BALANCED</span></td>
            </tr>
            <!-- POS 3 S2 -->
            <tr class="hover:bg-slate-50">
              <td class="p-3 font-bold text-slate-900 font-sans">POS 3 - Shift 2</td>
              <td class="p-3 text-slate-400 font-sans">-</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[11px] bg-slate-100 text-slate-500 font-bold">0.00</span></td>
              <td class="p-3 text-center"><span class="text-slate-400 font-sans">[INACTIVE]</span></td>
            </tr>
            <!-- OPT -->
            <tr class="hover:bg-slate-50 bg-blue-50/30">
              <td class="p-3 font-bold text-blue-900 font-sans">OPT Terminal</td>
              <td class="p-3 font-semibold text-blue-700 font-sans">FAREEZ</td>
              <td class="p-3 text-right">25,888.85</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-right">25,888.85</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[11px] bg-emerald-100 text-emerald-800 font-bold">0.00</span></td>
              <td class="p-3 text-center"><span class="text-emerald-600 font-bold font-sans">BALANCED</span></td>
            </tr>
            <!-- TOTAL -->
            <tr class="bg-slate-100 font-bold text-slate-900 border-t-2 border-slate-300">
              <td class="p-3 font-sans">TOTAL CONSOLIDATED</td>
              <td class="p-3 font-sans">All Active Shifts</td>
              <td class="p-3 text-right">67,678.55</td>
              <td class="p-3 text-right">0.00</td>
              <td class="p-3 text-right">67,678.55</td>
              <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[11px] bg-emerald-200 text-emerald-900 font-bold">0.00</span></td>
              <td class="p-3 text-center"><span class="text-emerald-700 font-bold font-sans">ALL BALANCED</span></td>
            </tr>
          </tbody>'''

text = text[:old_tbody_start] + new_tbody + text[old_tbody_end:]
with open('petron_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)

try:
    artifact_path = r'C:\Users\User\.gemini\antigravity\brain\66a0b412-dc23-41d1-ac28-e453a79df7ba\petron_dashboard.html'
    with open(artifact_path, 'w', encoding='utf-8') as f:
        f.write(text)
except Exception:
    pass

print('Updated petron_dashboard.html for Day 03 successfully!')
