# Security review — Laravel API + Next.js

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


Gunakan checklist ini untuk fitur baru atau perubahan yang menyentuh autentikasi, data pribadi, multi-tenant, upload, export, pembayaran, saldo, atau izin. Ini panduan review; sesuaikan kontrol dengan threat model dan implementasi project.

## 1. Identitas dan otorisasi

- Bedakan authentication (siapa user) dari authorization (apa yang boleh dilakukan).
- Jangan mengandalkan tombol tersembunyi, route guard frontend, HOC, atau validasi UI sebagai kontrol keamanan. Backend harus memeriksa izin pada setiap request.
- Periksa akses terhadap objek: user A tidak boleh membaca/mengubah/menghapus resource user B hanya dengan mengganti ID (IDOR/BOLA). Gunakan policy/gate, query yang dibatasi kepemilikan, atau pola otorisasi project.
- Untuk multi-tenant, tenant berasal dari identitas/sesi yang dipercaya server, bukan nilai header/body yang bebas dipercaya. Validasi akses tenant dan semua relasi terkait. Jangan menganggap Global Scope cukup tanpa menguji query raw, `DB::table`, job, export, cache, dan relasi.
- `X-Tenant-Id` hanya boleh dipercaya setelah role diverifikasi server. Untuk role `super`, misalnya, akses lintas tenant adalah fitur by design — catat itu eksplisit dan uji bahwa role lain tidak bisa memakainya.
- Terapkan prinsip least privilege; periksa role, permission, guard, dan jalur bypass/admin.

## 2. Input dan output

- Gunakan data tervalidasi (`validated()`/DTO) untuk menulis data; jangan mass-assign payload mentah. `$fillable` membantu mass assignment tetapi bukan pengganti authorization.
- Validasi enum, rentang numerik, tanggal, relasi, ukuran, dan kombinasi field di server. Validasi referensi relasi harus juga memastikan objek berada dalam scope yang boleh diakses.
- Jangan mengembalikan model mentah tanpa meninjau field tersembunyi, relasi, atribut tambahan, dan kestabilan kontrak. Gunakan Resource/DTO/serializer eksplisit.
- Escape output sesuai konteks. Hindari `dangerouslySetInnerHTML` untuk konten tak tepercaya; bila HTML memang dibutuhkan, gunakan sanitizer terawat dan kebijakan yang sesuai.
- Jangan membocorkan stack trace, SQL, token, credential, atau detail internal dalam response, toast, URL, telemetry, maupun log. Redaksi data sensitif.

## 3. Session, token, CORS, dan secret

- Identifikasi mekanisme autentikasi aktual (cookie/session, Sanctum SPA, bearer token, atau lainnya) sebelum mengubah storage atau middleware. Jangan memindahkan token ke `localStorage` sebagai solusi cepat tanpa analisis risiko.
- Untuk cookie autentikasi, evaluasi `HttpOnly`, `Secure`, `SameSite`, domain/path, CSRF protection, dan kebutuhan lintas origin sesuai model deployment. CORS bukan pengganti autentikasi/CSRF.
- Jangan menaruh secret dalam variabel `NEXT_PUBLIC_*`, source frontend, log, atau file yang di-commit. Jangan mencetak `.env` atau credential saat debugging.
- Batasi origin CORS secara eksplisit pada deployment; jangan menggunakan wildcard bersama credential. Izinkan header/method yang benar-benar dibutuhkan.

## 4. Upload, export, dan file

- Validasi ukuran, ekstensi/MIME, dan bila perlu signature/konten; jangan percaya nama file dari pengguna. Buat nama penyimpanan sendiri.
- Simpan file sensitif pada disk privat dan otorisasi setiap download. Hindari path traversal, file overwrite, dan file executable di web root.
- Export harus menerapkan scope tenant/ownership dan pembatasan volume; lindungi dari formula injection pada CSV/Excel bila data dapat dibuka di spreadsheet.

## 5. Minimum negative tests

Sesuaikan kasus dengan fitur; untuk data yang memiliki ownership/tenant, tes minimal: unauthenticated ditolak; role/permission salah ditolak; user lain tidak dapat mengakses objek; tenant lain tidak dapat mengakses data; payload berisi field terlarang diabaikan/ditolak; input invalid ditolak; file atau export tidak melewati scope. Pastikan tes membuktikan response dan tidak adanya side effect yang tidak diizinkan.

## 6. Pelaporan

Catat risiko yang diperiksa, test yang dijalankan, hasil PASS/FAIL/NOT RUN, dan keterbatasan. Jangan menyatakan fitur aman hanya karena linter/type-check lolos.
