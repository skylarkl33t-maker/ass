# SES HARİTASI: hangi MIDI'ye hangi ses, hangi tonda (FL Studio)

**Nota adı uyarısı:** FL'de MIDI 60 "C5" görünür (standart adın bir oktav üstü). Aşağıda hem MIDI no hem FL adı var.
**Tüm parçalarda:** MIDI'yi `File → Import → MIDI file` ile al, tempoyu uygula. Her track ayrı kanal olur. Her kanalı ayrı Mixer insert'ine yolla.
**Sidechain:** Kick'in kendi insert'i. Diğer insert'lerin birine `Fruity Limiter` (sidechain: kick) ya da `Fruity Peak Controller → Volume` bağla. Her satırdaki "SC" değeri düşme miktarı.

---
## 01 · DİŞLİ KALP · 138 BPM · Fa♯ minör (F#m) · sert tekno
Gam: F# G# A B C# D E. Akor döngüsü (2'şer bar): **F#m → D → A → E**.

| MIDI dosyası | Nota (MIDI / FL adı) | Ses | Ayar | SC |
|---|---|---|---|---|
| `01_drums_GM` kick (36 / C3) | F#1 (46 Hz) tonlu | Kick: sinüs, 220 Hz'den 47 Hz'e 25 ms'de düşen, kuyruk ~200 ms, **distortion** (tanh). `Fruity Kick` ya da Sytrus. Kick'i F#1'e tune et | Bas'a göre en yüksek ses | – |
| drums clap (39 / D#3) | – | Gürültü clap, 900–4200 Hz bandı, 3 hızlı vuruş + kuyruk | Plate reverb 0.9 sn | – |
| drums hat (42 / F#3) | – | Kapalı hat, 7 kHz+ high-pass, 25 ms | 16'lıkların "e" ve "a"sında | hafif |
| drums open hat (46 / A#3) | – | Açık hat, 6 kHz+, 100 ms, "&" vuruşlarında | | hafif |
| drums rim (37 / C#3) | – | Kısa filtreli gürültü tık (2–6 kHz), her 16'lıkta | Zamanla sesi açılır | hafif |
| drums snare roll (38 / D3) | – | Gürültü + 185 Hz gövde, build'lerde 16'lık → 32'lik | Yükselen velocity | – |
| `02_sub_bass_F#1` | 30 / F#2, bazen 28 / E2 (8. barın sonu) | Sinüs + 2. harmonik, `3x Osc` ya da Sytrus. Off-beat 8'lik | Low-pass yok, hafif sat. | **güçlü** |
| (MIDI'de yok) rumble | F#1 | Kick'i kopyala, reverb (0.5 sn, 110 Hz low-pass), tanh dist. Her vuruşta kick'le duck | Bas gibi çalışır, 32–140 Hz | tam |
| `03_acid_lead` | 42–57 / F#3 → A4. Kök F#2 (42 / F#3) | **Acid saw**: tek testere, **resonant low-pass (Q ~7)**. Sytrus/Harmor/Flex "acid" | Cutoff 380 Hz → ~1.7 kHz (16 barlık LFO), her notada +2100 Hz, 75 ms'de iner. Vurgulu notada +3400. Çıkışa drive | orta |
| `04_perc_clank` | 76–90 / E6 → F#7 | Metal çan: FM (oran 1.414, index 5, 50 ms'de azalır), 400 Hz altı kes | Sağ/sol sırayla pan ±0.6 | hafif |
| `05_choir_chords` | F#m [42,54,57,61], D [38,54,57,62], A [45,52,57,61], E [40,52,56,59] | **İnsan koro**: "u → o" (96–112, 136–160 barlarında "o → a"). Formant sample veya `Vocodex`. Her nota ±9 cent çift ses | Giriş 0.9 sn, çıkış 2 sn, hall reverb 3.6 sn | orta |
| `06_human_melody` | 68–77 / G#5 → F6 | Solo "aah" sesi, vibrato 5.3 Hz, ±6 cent 3 ses | Hall reverb | hafif |
| `07_vocal_chops` | akor 3. ve 5. sesi (57–74) | Kısa "ha / ah / oh / eh" (160 ms), önünde nefes | 16'lık, sync'li | hafif |
| `08_heartbeat` | 24 / C2 | Kalp: sinüs 58 → 40 Hz, 90 ms, 180 Hz low-pass, "lub-dub" 0.7 vuruş arayla | Sadece açılış ve final | – |

**Master:** 22 Hz high-pass, hafif tanh limiter. Zirve −1 dBFS. Orijinal demo RMS ≈ −11 dB.

---
## 02 · NEFES DÖNGÜSÜ · 122 BPM · Re minör (Dm) · minimal melodik
Gam: D E F G A Bb C. Akor döngüsü (2'şer bar): **Dm → Bb → F → C**.

| MIDI dosyası | Nota (MIDI / FL adı) | Ses | Ayar | SC |
|---|---|---|---|---|
| `01_drums_GM` kick 36 | – | **Yumuşak kick**: 155 → 50 Hz, kuyruk 170 ms, hafif sat. | Sert değil, yuvarlak | – |
| clap 39 | – | Clap, 5.5 kHz'te low-pass (yumuşak) | Vuruş 2 ve 4, düşük ses | – |
| hat 42 / open hat 46 / shaker 70 / rim 37 | – | Hat 16'lığın "a"sında, open hat "&"de, shaker 16'lık (5.5–13 kHz) | Hepsi kısık | hafif |
| `02_sub_bass` | Dm 38 (D3), Bb 34 (A#2), F 29 (F2), C 36 (C3) | Sinüs + hafif 2. harmonik, kısa, off-beat | | güçlü |
| `03_arp_pluck` | Dm [62,65,69,74], Bb [58,62,65,70], F [60,65,69,72], C [60,64,67,72] | **Pluck**: testere benzeri, yüksek harmonikler hızlı söner (decay ~0.5 sn). Sytrus/Harmor/FLEX "pluck" | Çiftli ±5 cent (stereo). **Ping-pong delay: 3/16 (noktalı 8'lik), 4 tekrar, 4.2 kHz low-pass** | hafif |
| `04_lead_pluck` | 65–77 / F5 → F6 | Aynı pluck, **daha uzun decay (1.5 sn)**. Melodi: Dm'de D5-C5-A4, Bb'de Bb4-A4-F4... | Delay + hall | hafif |
| `05_pad_chords` | Dm [50,53,57,62], Bb [46,50,53,58], F [48,53,57,60], C [48,52,55,60] | Sıcak pad: 7 harmonikli testere, üç ses ±12 cent, **yavaş filtre salınımı (0.09 Hz)** | Giriş 1.3 sn, çıkış 2 sn | orta |
| `06_choir_chords` | pad notaları, 50 altı oktav yukarı | İnsan koro "u → o" (112'den sonra "o → a") | Hall reverb 3 sn | orta |
| `07_vocal_chops` | arp akor 2. ve 3. sesi | "ha/ah" kısa | | hafif |

---
## 03 · ÇELİK NABIZ · 130 BPM · Mi minör (Em) · endüstriyel Paganini tarzı
Piyano, pad, pluck **yok**. Gam: E F# G A B C D. Tek akor yok, bas ve riff E'de döner, G ve B ile gerilim.

| MIDI dosyası | Nota (MIDI / FL adı) | Ses | Ayar | SC |
|---|---|---|---|---|
| `01_drums_GM` kick 36 | ~52 Hz tonlu (A1'e yakın) | **Sıkı kick**: 260 → 52 Hz çok hızlı, kuyruk 115 ms, güçlü dist. + 3 kHz click | Kısa, dar, vurucu | – |
| clap 39, hat 42, open hat 46, rim 37, roll 38 | – | Clap (Plate 0.7 sn), 16'lık hat, off-beat open hat, rim 3-6-11-14. step | | hafif |
| toms 45 / 47 / 50 (FL: A3 / B3 / D4) | sesler MIDI'den bir oktav yukarı çalar (A3, B3, D4 tınısı) | **Tom**: sinüs, başlangıçta yüksek perdeden %62'ye düşer, 110 ms, hafif gürültü | 8 barda bir fill | – |
| grind 56 | – | Dar gürültü (700–3200 Hz), 40 ms, distorted. Endüstriyel ritim dokusu | 16'lık gate deseni | hafif |
| `02_rolling_bass` | **28 / E2** (4. vuruşta bazen 31 / G2) | **Yuvarlanan 16'lık bas**: sinüs + 2. + 3. harmonik, tanh distortion. "x-xx" deseni (her vuruşun 2, 3, 4. 16'lığı), 80 ms | **Kick'e sıkı sidechain (%90, 90 ms)** | **güçlü** |
| `03_riff_stab` | 40–50 / E3 → D4 (E, G, B, A, D) | **Karanlık testere riff**: tek nota, resonant LP (Q 5), kısa. Distorted. Cutoff 320 → 1000 Hz (12 barlık LFO) | Sade, tekrarlayan; üç desen (a, b, c) | orta |
| `04_metal_clank` | MIDI 52–64, **ses 2 oktav yukarı** (FL'de +24 yarı ton çal) | Metal çan FM | Sağ/sol pan | hafif |
| `05_anvil` | 55 (G3 / FL G4 → ~196 Hz), 52 (E3 → 165 Hz) | Örs: FM (oran 2.76), uzun ring 1.6 sn, kırılmalarda 2 barda bir | **Büyük hall (3.2 sn, 4.5 kHz low-pass)** | hafif |
| `06_whisper_chops` | 52 (FL: E4), 55 (FL: G4) | Kısık, fısıltı gibi "o/u/a" kısa chop. Çok seyrek | Hall, kırılma ve zirvede | hafif |

**Karakter:** Mi minör. Bas E'de kal, riff E-G-B-A etrafında dolansın. Kırılmada (bar 64–80) kick ve bas yok, sadece anvil, tıkırtı ve fısıltı.

---
## Stem yolu (kolay yol)
Her parçanın `stems/` klasöründeki .flac dosyaları hazır sesli. FL'de Playlist'e sürükle, hepsi 1. bar'a hizalı.
