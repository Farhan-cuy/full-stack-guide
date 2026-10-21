# Workflow fullstack — cara berpikir sebelum, saat, dan sesudah menulis code

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


Baca file ini untuk tugas yang lebih dari perubahan satu-dua baris. Isinya bukan template,
melainkan cara kerja agar agent memahami sistem sebagai satu kesatuan BE + FE.

## Isi

1. [Peta alur request](#1-peta-alur-request-end-to-end)
2. [Baca dulu sebelum menulis](#2-baca-dulu-sebelum-menulis)
3. [Contract-first](#3-contract-first)
4. [Protokol verifikasi library](#4-protokol-verifikasi-library)
5. [Analisis dampak lintas sisi](#5-analisis-dampak-lintas-sisi)
6. [Checklist keamanan & performa](#6-checklist-keamanan--performa)
7. [Definition of done](#7-definition-of-done)

## 1. Peta alur request (end-to-end)

Setiap fitur melewati rantai yang sama. Saat menulis atau men-debug, tahu sedang di mata rantai mana.

Peta di bawah adalah dialect Laravel API + Next.js App Router (SHOULD jika helper-nya ada). Cocokkan tiap mata rantai ke repo.

```
[Table/Dialog] → Service FE (api/<domain>) → request<T>() → fetch + headers (Bearer, X-Tenant-Id)
   → routes/api (prefix v1, auth:sanctum, role:a|b) → ApiFormRequest (validasi, 422)
   → Controller tipis (try/catch per method ATAU withExceptions, jangan campur)
   → Service BE (DB::transaction, BusinessException)
   → Model (+Global Scope tenant) → Resource (bentuk JSON) → envelope (success/message/data | meta)
   → request<T>() (throw ApiError bila gagal) → SWR cache (key array) → render / toast / setError
```

Konsekuensi: mengubah satu mata rantai hampir selalu menuntut cek mata rantai tetangganya
(lihat §5).

## 2. Baca dulu sebelum menulis

Pola project ada di code project, bukan hanya di guide ini. Sebelum menulis file baru:

1. **Cari saudara terdekat** (definisi di `SKILL.md`). Tugas edit → fitur itu sendiri. Tugas baru →
   `grep`/folder modul yang sama, jenis yang sama, satu rantai lengkap. Contoh: page list kategori
   baru → list `items` di subapp yang sama, bukan dashboard KPI. Import Excel kategori → class
   Import lain di repo, bukan recipe CRUD. Tambah field `icon` di kategori → file kategori yang
   sudah ada, bukan scaffold resource baru.
2. **Cocokkan dengan guide.** Saudara terdekat adalah bukti tentang pola repo, bukan bukti bahwa pola itu aman atau benar. Untuk file baru, gunakan pola repo yang masih valid; jika ada risiko keamanan, integritas data, bug nyata, atau konflik kontrak, ikuti guardrail MUST dan jelaskan perubahan minimum yang diperlukan. Jangan menyalin bug hanya demi konsistensi.
3. **Cek yang sudah ada sebelum membuat.** Helper (`toQuery`, `applyServerErrors`), type di `types/`,
   komponen di `components/ui/`, role di `lib/constant`. Duplikat = utang.
4. **Baca git history singkat bila ragu** (`git log --oneline -5 -- <path>`) untuk memahami arah perubahan terakhir.

Jangan memulai dengan menulis lalu menyesuaikan di akhir; urutannya baca → rencanakan → tulis.

## 3. Contract-first

Untuk fitur yang menyentuh dua sisi, tulis kontrak dulu (satu blok, boleh di jawaban atau di PR),
baru implementasi:

```
POST /api/v1/items          role: admin
request : { nama: string (required, max 100), group_ids: number[] (min 1) }
200/201 : { success, message, data: Item }
422     : { success:false, message:'Validasi gagal.', errors:{ nama:[...] } }
400     : BusinessException 'Kuota grup sudah penuh.'
```

Urutan kerja: kontrak → BE (+test) → type FE dan factory → UI. Setelah BE jadi, panggil endpoint nyata
(test feature, `curl`, atau tinker) sebelum menulis FE, supaya type FE mencerminkan response asli,
bukan tebakan. Bentuk standar ada di `contract.md`.

## 4. Protokol verifikasi library

Memori model tentang library bisa usang atau milik versi lain. Perilaku yang salah di sini jarang
error saat dijalankan, tapi diam-diam salah (contoh nyata: `mutate` SWR terikat key, `toast.promise`
tidak mengembalikan promise yang bisa di-await, zod v3 vs v4).

**Kapan wajib verifikasi:** memakai API library yang belum ada contohnya di repo, memakai opsi yang
tidak yakin, menambah library baru, atau melihat peringatan deprecation.
**Kapan boleh lewati:** memakai pola yang templatenya sudah ada di references dan di repo.

Urutan sumber (dari paling bisa dipercaya):

1. **Pemakaian di repo** — `grep -rn "useSWR\|mutate(" app api | head`. Pola yang sudah berjalan menang.
2. **Source/type terpasang** — cocok dengan versi yang benar-benar dipakai, bekerja offline:
   - FE: `node_modules/<pkg>/package.json` (versi), `node_modules/<pkg>/dist/**/*.d.ts` (signature).
   - BE: `composer show <pkg>` (versi), `vendor/<pkg>/src/` (implementasi), `php artisan route:list`.
3. **Dokumentasi resmi untuk versi mayor itu** — buka lewat web fetch/search atau MCP dokumentasi bila
   tersedia. Pastikan halaman yang dibaca versinya sama dengan lockfile.
4. **Ingatan sendiri** — paling akhir, dan tandai sebagai asumsi di laporan.

Daftar yang **sensitif versi** (cek dulu, jangan andalkan ingatan):

| Library | Yang berubah antar versi |
|---|---|
| Next.js 14 → 15 | `params`/`searchParams`/`cookies()` menjadi async; perilaku cache fetch |
| React 18 → 19 | `ref` sebagai prop, `use()`, perubahan tipe |
| zod 3 → 4 | `required_error`/`invalid_type_error` → `error`; format error |
| SWR 1 → 2 | signature `mutate`, `useSWRMutation`, opsi `keepPreviousData` |
| sonner | bentuk return `toast.promise` |
| shadcn/ui | komponen disalin ke repo — baca file di `components/ui/`, bukan dokumentasi umum |
| Laravel 10 → 11 | `bootstrap/app.php` menggantikan `Kernel`/`Handler`; `config/cors.php` tidak ada by default (`php artisan config:publish cors`) |
| spatie/permission | sintaks middleware, `guard_name`, cache permission |
| maatwebsite/excel | concern per versi, config transaksi |

Catat di laporan: library apa yang diverifikasi, versinya, dan dari sumber mana.

## 5. Analisis dampak lintas sisi

Sebelum selesai, jawab: "siapa lagi yang membaca bentuk ini?" lalu `grep`.

| Yang diubah | Cari konsumennya |
|---|---|
| Key/field di Resource (BE) | `grep -rn "<nama_field>" types api app components` di FE; Resource lain yang memakai relasi sama |
| Rules/pesan Form Request | zod schema di dialog FE yang sama; pesan di test |
| Status/pesan `BusinessException` | handler FE yang mencocokkan teks pesan (hindari mencocokkan string; pakai status) |
| Nama/path route | factory `api/<domain>`, test, dokumentasi |
| Role/permission | `role:` di route, `withAuth(...)` di FE, `SUBAPP_ALLOWED_ROLES`, seeder |
| Tipe FE | semua factory + komponen yang mengimpor type itu (`tsc --noEmit` menunjukkan) |
| Env var | `.env.example` kedua sisi; ingat `NEXT_PUBLIC_*` ditanam saat build/dev-start |
| Migration (kolom/tabel) | Model `$fillable`, Resource, Excel import/export, seeder, factory test, deployment/backfill/rollback plan |

Perubahan breaking pada endpoint yang sudah dipakai → endpoint `v2` baru (`contract.md` §6), bukan mengubah yang lama.

## 6. Checklist keamanan & performa

Checklist ringkas di bawah bukan pengganti review risiko. Untuk fitur sensitif, gunakan `security.md`; untuk operasi konkurensi/import/saldo/stok/kuota, gunakan `data-integrity.md`; untuk bukti dan cakupan test, gunakan `testing.md`.

Keamanan (tiap fitur baru):
- Autentikasi dan otorisasi ditegakkan di server; middleware route adalah salah satu lapisan, bukan satu-satunya. Periksa policy/gate dan kepemilikan resource sesuai desain project. Tenant terfilter dan diuji lintas tenant.
- Mass assignment: `$fillable` eksplisit; controller memakai `$request->validated()`.
- Tidak ada rahasia di `NEXT_PUBLIC_*`; token/password tidak masuk log atau toast.
- HTML dari user ditampilkan lewat `sanitizeHtml`; tidak ada `dangerouslySetInnerHTML` mentah.
- Upload: validasi tipe/ukuran/konten sesuai risiko; nama file dibuat aman, storage privat untuk file sensitif, dan otorisasi download diperiksa.
- `limit` list dibatasi (maks 100).

Performa:
- Tidak ada N+1 (`with()`/`withCount()`/join); cek di list yang menampilkan relasi.
- List selalu paginate; search ber-debounce di FE.
- Kolom yang difilter/di-sort besar → pertimbangkan index di migration.
- SWR key menyertakan semua param, tapi tidak lebih (key terlalu banyak = cache tak terpakai).

## 7. Definition of done

Selesai berarti sudah dibuktikan, bukan sekadar ditulis:

- [ ] Kontrak ditulis dan BE/FE konsisten (type FE = response asli).
- [ ] Test BE hijau (happy path, validasi, authz/ownership, dan failure case relevan); route/middleware/policy diperiksa.
- [ ] Risiko keamanan dan integritas data ditinjau sesuai `security.md` dan `data-integrity.md`.
- [ ] Status verifikasi dilaporkan sebagai PASS / FAIL / NOT RUN; jangan mengklaim test berjalan jika hanya diperiksa secara statis.
- [ ] Lint dan type-check yang tersedia di project bersih; bila command tidak tersedia atau tidak relevan, laporkan NOT RUN/NOT APPLICABLE dengan alasan.
- [ ] Jalur manual end-to-end dicoba atau, bila tidak bisa dijalankan di sini, dinyatakan jujur belum dicoba:
      tambah (sukses) · tambah (422 → error per field, dialog tetap terbuka) · hapus (list ter-refresh) ·
      token dihapus (redirect `/login`).
- [ ] Analisis dampak §5 dijalankan; konsumen yang terdampak ikut diperbarui.
- [ ] Library yang tidak biasa sudah diverifikasi (§4) dan dicatat.
- [ ] Laporan mengikuti Output Contract di `SKILL.md`.

Versi netral (bukan khusus stack Laravel + Next.js) dari protokol verifikasi library, tabel dampak lintas sisi, dan tabel gejala ke layer ada di Core: `../../../references/library-verification.md`, `contracts.md`, dan `debugging.md`.
