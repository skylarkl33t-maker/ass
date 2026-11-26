# 01 – Dişli Kalp (pilot)
138 BPM · Fa♯ minör · 192 bar · 5:40 · sert peak-time tekno · konsept: Makine ve İnsan

## Yapı (bar)
| Bar | Bölüm | Ne oluyor |
|---|---|---|
| 0–16 | Uyanış | İnsan kalp atışı, mekanik tıkırtılar, kick 8'de girer |
| 16–32 | Yükseliş | Rumble bas, hat, clap, riser ve snare roll |
| 32–48 | Makine | Tam sert ritim, 40'ta acid lead |
| 48–64 | İnsan sızıyor | Formant koro (u→o), vokal parçacıklar |
| 64–80 | Kırılma | Kick yok. Koro ve insan melodisi, makine sadece tıkırdar |
| 80–112 | Zirve 1 | Her şey, phrygian acid, vokal chop |
| 112–128 | Soyunma | Kick ve rumble, koro, tekrar yükseliş |
| 128–160 | Zirve 2 | Koro, melodi, acid ve chop birlikte |
| 160–186 | Sönüş | Makine adım adım çekilir |
| 186–192 | İnsan kalır | Kalp atışı, koro, son nefes |

## MIDI (FL Studio'ya sürükle)
`midi/00_FULL_ARRANGEMENT.mid` tüm kanalları ayrı track olarak getirir. Tek tek: `01_drums_GM` … `08_heartbeat`.
Tempo 138. Ses: `01_disli_kalp.wav` (24-bit, git'e girmez) ve `.mp3` demo mix.
Yeniden üretmek: `python3 ../gear_heart.py --out OUT [--stems]` (--stems ayrı kanal WAV'ları çıkarır).
