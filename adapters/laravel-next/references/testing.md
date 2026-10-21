# Testing and verification strategy

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


Tujuan testing adalah memberi bukti terhadap perilaku yang diminta, bukan sekadar membuat command hijau. Pilih kedalaman berdasarkan risiko dan arsitektur project.

## 1. Jenis verifikasi

1. **Static** — formatter, linter, type-check, analisis konfigurasi. Berguna tetapi tidak membuktikan runtime behavior.
2. **Unit** — aturan bisnis terisolasi, transformasi, validasi helper.
3. **Feature/API** — route, middleware, request validation, authorization, response envelope, persistence.
4. **Integration** — database, queue, file, import, external boundary, cache, atau integrasi frontend/backend.
5. **Behavior/E2E** — alur pengguna dan state UI penting bila environment tersedia.

Tidak semua fitur butuh semua lapisan. Jelaskan pilihan berdasarkan risiko, bukan menambahkan test tanpa nilai.

## 2. Matriks test minimum untuk API

Pilih yang relevan: happy path; payload invalid; unauthenticated; role/permission salah; resource tidak ditemukan; resource milik user/tenant lain; duplicate/conflict; dependency gagal; side effect tidak terjadi ketika request gagal; response shape dan status code sesuai kontrak.

Untuk operasi data sensitif, gunakan `data-integrity.md` dan tes repeated request/concurrency. Untuk file/import, tes file kosong, format invalid, baris invalid, file besar yang realistis, duplicate, dan perilaku partial failure.

## 3. Frontend

Periksa loading, empty state, error state, retry, validasi field 422, kegagalan server, double submit, dialog tetap terbuka ketika gagal, list/cache refresh setelah mutasi, dan izin akses. Gunakan test otomatis atau langkah manual yang bisa diulang sesuai tool yang tersedia.

Type-check tidak menggantikan pengujian response API. Bila type FE dibuat dari asumsi, tandai dan verifikasi terhadap response aktual atau test contract.

## 4. Regression scope

Sebelum perubahan, identifikasi consumer dan perilaku yang bisa terdampak. Setelah perubahan, jalankan test terkait langsung terlebih dahulu, lalu test regresi yang proporsional. Jangan memperbaiki kegagalan lama yang tidak terkait secara diam-diam; catat sebagai pre-existing jika dapat dibuktikan.

## 5. Pelaporan status

Gunakan status berikut secara konsisten:

- **PASS** — command/test benar-benar dijalankan dan berhasil.
- **FAIL** — dijalankan dan gagal; sertakan ringkasan error yang relevan.
- **NOT RUN** — tidak dijalankan; jelaskan alasan (environment, dependency, waktu, akses, atau risiko).
- **NOT APPLICABLE** — memang tidak relevan, dengan alasan singkat.

Jangan menyatakan build/test lulus hanya karena kode tampak benar atau karena test tidak tersedia. Sebutkan command yang dijalankan, hasil ringkas, dan cakupan yang belum diverifikasi. Jangan mengklaim browser/E2E diuji jika tidak dijalankan.

## 6. Definition of done

- [ ] Kriteria penerimaan dapat diamati dan telah diperiksa.
- [ ] Kontrak request/response dan side effect sesuai ekspektasi.
- [ ] Failure path dan authorization diuji sesuai risiko.
- [ ] Test/lint/type-check relevan dijalankan atau diberi status NOT RUN.
- [ ] Tidak ada klaim yang melampaui bukti.
