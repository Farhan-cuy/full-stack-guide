# Laravel API + Next.js App Router adapter

Adapter untuk repository berpola Laravel API + Next.js App Router dengan helper bersama (mis. Form Request base, response helper, typed fetch client, tenant global scope). Adapter ini bukan default universal. Aktifkan hanya setelah repository memperlihatkan pola yang relevan dan versi dependency diverifikasi.

## Aktivasi
- Deteksi `composer.json`, `package.json`, lockfile, serta struktur aktual.
- Pastikan project memang memakai Laravel + Next.js dan helper bersama yang disebutkan.
- Terapkan instruksi adapter sebagai SHOULD kecuali keamanan, integritas data, kontrak eksplisit, atau instruksi user menuntut hal lain.
- Jika pola helper tidak ada, jangan menciptakannya; ikuti Core dan saudara terdekat.

## Referensi
`references/` berisi materi Laravel/Next.js dari Fullstack Code Guide v3.3.0 yang dipertahankan sebagai adapter khusus. Periksa versi framework dan dependency sebelum menggunakan contoh.

## Catatan prioritas
Kata WAJIB / SELALU di `references/` menunjukkan default dialect adapter ini. Bila bertentangan dengan keamanan, integritas data, kontrak publik yang ada, atau instruksi user, Core yang menang. Sinyal aktivasi dan tautan ke adapter lain: `../INDEX.md`.
