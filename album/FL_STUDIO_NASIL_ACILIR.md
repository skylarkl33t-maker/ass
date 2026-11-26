# FL Studio'da açma (2 parça)
FL proje dosyası (.flp) kapalı bir format, o yüzden kodla üretilemiyor. Paket iki yolla aynı sonucu verir:

## Yol A – Hızlı: ses stem'leri (birebir demo sesi)
1. FL'de yeni proje aç, **Tempo = 138** (Dişli Kalp) ya da **122** (Nefes Döngüsü).
2. `stems/` klasöründeki tüm .flac dosyalarını seç, Playlist'e sürükle, 1. bar'dan başlat.
   Hepsi 1. bar'a hizalı, tek tek yüksekliği ayarlayabilirsin (stem'ler ayrı ayrı normalize).
3. Mixer'da her stem'e ayrı kanal ver. Rumble ve sub'a ses eşitliği için biraz low-cut ekle.

## Yol B – Asıl yol: MIDI + kendi sesin
1. **File → Import → MIDI file** → `midi/00_FULL_ARRANGEMENT.mid`.
   "Create new channels" seçili kalsın. Her track ayrı kanal olur. Tempoyu FL'e uygulat.
2. Kanalları şu sesle doldur:
   - Davul (ch10): Kick/Clap/Hat için FPC ya da Drumpad, kick'i kendi sample'ınla değiştir.
   - Sub: Sytrus/Harmor sinüs, ya da 3x Osc.
   - Acid/Arp/Lead: Harmor, Sytrus, ya da FLEX pluck/saw preset'i.
   - Pad, Choir: Harmor/Flex pad, vokal için ücretsiz koro sample'ı.
3. Sidechain: Mixer'da kick'e Fruity Peak Controller ya da Fruity Limiter sidechain bağla (bas, pad, arp).

Parçalar: 01 Dişli Kalp (sert tekno, Fa♯ minör) · 02 Nefes Dönüşü/Döngüsü (minimal melodik, Re minör).
