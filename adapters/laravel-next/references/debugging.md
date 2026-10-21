# Debugging lintas BE ↔ FE + setup integrasi

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


Muat file ini saat ada bug ("kok 403", "tabel kosong", "CORS", "list tidak refresh"), atau saat
menyiapkan koneksi FE ke BE (env, CORS, token). Bagian pertama: cara menemukan layer yang salah.

## Isi

1. [Temukan layer dulu](#1-temukan-layer-dulu)
2. [Gejala → penyebab → perbaikan](#2-gejala--penyebab--perbaikan)
3. [Setup integrasi](#3-setup-integrasi)

## 1. Temukan layer dulu

Jangan menebak. Persempit dengan urutan murah → mahal:

1. **Network tab / `curl`** — status HTTP dan body mentah. Ini langsung memisahkan "request tak sampai"
   (CORS, URL, token) dari "BE membalas error" dari "BE sukses tapi FE salah baca".
2. **`php artisan route:list --path=v1/<modul>`** — route ada? middleware benar?
3. **Log BE** — `storage/logs/laravel.log` dan tabel `ErrorLog` (exception tak terduga tercatat di sana;
   `BusinessException` sengaja tidak).
4. **`php artisan tinker`** — jalankan query/service langsung, lewati HTTP.
5. **React DevTools / SWR** — key apa yang aktif, `data`/`error` apa yang dipegang hook.

Aturan: satu hipotesis, satu pengujian. Ubah satu hal lalu uji ulang, jangan menambal tiga tempat sekaligus.

## 2. Gejala → penyebab → perbaikan

| Gejala | Penyebab paling mungkin | Perbaikan |
|---|---|---|
| 403 padahal role benar | `role:a,b` (koma) dibaca satu role; `guard_name` tak cocok; cache permission basi | pakai `role:a\|b`; samakan guard; `forgetCachedPermissions()` di seeder |
| Validasi gagal tapi respon HTML/redirect, bukan JSON | Request tak extends `ApiFormRequest` (tanpa `failedValidation`), atau header `Accept: application/json` hilang | extend base; pastikan header lewat `configureHeaders` |
| 401 setelah login berhasil | nama cookie token beda (`TOKEN_COOKIE_KEY`), header `Authorization` tak terkirim, guard bukan `sanctum` | cek cookie di devtools, cek header di network tab, cek `auth:sanctum` di route |
| Error CORS di console | origin FE tak diizinkan, `allowed_headers` tak memuat `Authorization`/`X-Tenant-Id`, atau path tak tercakup | lihat §3 CORS |
| 200 tapi tabel kosong | FE membaca path envelope yang salah (`data.data`), atau Resource lupa `$wrap = null` sehingga jadi `data.data.data` | cocokkan dengan `contract.md` §1; cek `$wrap` |
| List tidak refresh / sempat kosong setelah tambah-hapus | `mutate(key)` dari hook `useSWR` (argumen pertama adalah data) | `mutate()` atau `mutate` global dengan matcher (`frontend.md` §3) |
| Toast "berhasil" padahal gagal | factory memakai `.then(r => r.json())` tanpa cek `!ok` | semua lewat `request<T>()` yang melempar `ApiError` |
| Dialog menutup, input hilang saat 422 | dialog `setOpen(false)` tanpa melihat hasil | `SubmitResult` + `applyServerErrors` (`frontend-ui.md` §A) |
| 500 berbentuk HTML bukan envelope JSON | exception terjadi di luar `try/catch` (constructor controller/service, middleware) | pindahkan logika dari constructor ke dalam method |
| Data tenant lain muncul | `DB::table` tak terkena Global Scope; header `X-Tenant-Id` salah; model lupa trait | filter `$tenantId` manual; cek trait |
| Upload gagal 415/422 padahal file ada | `Content-Type` diset manual pada `FormData` | `isFileUpload: true`, jangan set Content-Type |
| Build error "useSearchParams should be wrapped in Suspense" | `useSearchParams` di komponen tanpa `<Suspense>` | bungkus di `page.tsx` |
| `localStorage is not defined` / hydration mismatch | akses browser API saat render di server | guard `typeof window !== "undefined"` atau pindah ke `useEffect` |
| Env baru tidak terbaca di FE | `NEXT_PUBLIC_*` ditanam saat dev server/build mulai | restart dev server / rebuild |
| Import Excel lambat / timeout | tanpa `WithChunkReading`, `set_time_limit` kecil, query di dalam loop | chunk 500; firstOrCreate; hindari N+1 |
| Tipe FE lolos build tapi salah saat jalan | `ignoreBuildErrors` aktif; response tak sesuai type | `npx tsc --noEmit`; bandingkan dengan response asli |

Kalau gejala tidak ada di tabel: kembali ke §1, jangan memilih baris yang "mirip".

## 3. Setup integrasi

### Env

| Sisi | Variabel | Catatan |
|---|---|---|
| FE | `NEXT_PUBLIC_API_URL` (mis. `http://localhost:8000/api/v1`), `NEXT_PUBLIC_COOKIE_NAME`, `NEXT_PUBLIC_APP_NAME` | terbuka di browser — tidak ada rahasia |
| BE | `APP_URL`, `FRONTEND_URL` (untuk CORS), `SANCTUM_STATEFUL_DOMAINS` bila memakai cookie SPA | `APP_DEBUG=false` di produksi (menentukan detail error di `exceptionError`) |

Selalu perbarui `.env.example` kedua sisi saat menambah env var.

### CORS (Laravel 11)

Laravel 11 tidak menyertakan `config/cors.php` default; terbitkan dulu: `php artisan config:publish cors`.

```php
// config/cors.php
return [
    'paths' => ['api/*'],
    'allowed_methods' => ['*'],
    'allowed_origins' => [env('FRONTEND_URL', 'http://localhost:3000')],
    'allowed_headers' => ['Content-Type', 'Accept', 'Authorization', 'X-Tenant-Id'], // header custom WAJIB terdaftar
    'supports_credentials' => false, // Bearer token, bukan cookie sesi
];
```

Header custom (`X-Tenant-Id`) yang tidak ada di `allowed_headers` membuat preflight gagal — gejalanya
"CORS error" padahal masalahnya daftar header.

### Alur token (Bearer)

Login → BE membalas token → FE menyimpan ke cookie `TOKEN_COOKIE_KEY` → `configureHeaders()` membaca dan mengirim
`Authorization: Bearer` → `auth:sanctum` memvalidasi. Token mati → 401 → `request()` hapus cookie + `/login`.

### Port lokal umum

BE `php artisan serve` (8000) · FE `npm run dev` (3000). Ubah satu sisi → perbarui `NEXT_PUBLIC_API_URL` dan
`FRONTEND_URL`, lalu restart keduanya.
