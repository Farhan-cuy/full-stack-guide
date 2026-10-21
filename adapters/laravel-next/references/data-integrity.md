# Data integrity and concurrency

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


Gunakan panduan ini untuk saldo, transfer, stok, kuota, reservasi, import/export, upsert, counter, atau operasi multi-tabel. `DB::transaction` adalah alat penting, tetapi tidak otomatis mencegah race condition atau membuat operasi idempotent.

## 1. Mulai dari invariant

Sebelum coding, tulis kondisi yang harus selalu benar. Contoh: saldo tidak boleh negatif; satu external reference hanya boleh diproses sekali; stok tidak boleh turun di bawah nol; data tenant tidak boleh saling terhubung; satu import tidak boleh membuat duplikasi untuk kunci bisnis yang sama.

## 2. Transaction boundary

- Bungkus perubahan database yang harus berhasil/gagal bersama dalam satu transaksi. Letakkan di layer yang sesuai dengan arsitektur project (biasanya service/use case), bukan secara acak di controller dan model sekaligus.
- Hindari network/API call atau operasi lama di dalam transaksi jika bisa; transaksi panjang meningkatkan contention. Untuk efek eksternal, pertimbangkan after-commit, outbox, retry yang aman, atau kompensasi sesuai kebutuhan.
- Jangan menganggap transaksi meliputi email, queue eksternal, file storage, atau HTTP API. Tentukan perilaku jika efek eksternal gagal setelah commit.

## 3. Race condition dan constraint

- Jika keputusan bergantung pada nilai yang bisa berubah bersamaan (saldo/stok/kuota), jangan hanya membaca lalu menulis. Evaluasi row lock (`lockForUpdate`), atomic conditional update, optimistic locking, atau strategi lain sesuai database dan beban.
- Gunakan database constraints untuk invariant yang bisa dinyatakan di database: unique, foreign key, check constraint (bila didukung), not-null. Validasi aplikasi memberi pesan yang baik; constraint melindungi dari race condition dan jalur tulis lain.
- Tentukan urutan lock yang konsisten untuk mengurangi deadlock; tangani retry deadlock hanya bila operasi aman untuk diulang.
- Uji konkurensi dengan database/engine yang mendekati production. SQLite test tidak selalu merepresentasikan locking MySQL/PostgreSQL.

## 4. Idempotensi dan import

- `firstOrCreate`/`updateOrCreate` bukan jaminan idempotensi absolut di bawah konkurensi. Tentukan kunci bisnis, tambahkan unique constraint bila tepat, dan tangani duplicate-key/upsert secara eksplisit.
- Untuk endpoint yang dapat di-retry (webhook, payment, import), pertimbangkan idempotency key atau external event ID, status pemrosesan, unique constraint, dan response untuk retry.
- Import chunked perlu mendefinisikan perilaku parsial: semua file atomic atau tiap chunk/row commit; bagaimana error dilaporkan; bagaimana resume/retry bekerja; dan apakah file yang sama aman diulang. Jangan mengklaim atomicity seluruh file jika transaksi sebenarnya per chunk.
- `WithChunkReading` mengurangi penggunaan memori, tetapi tidak otomatis menjamin performa atau idempotensi. Ukur query per baris, batch/upsert bila cocok, dan validasi foreign key dalam scope yang benar.

## 5. Migration dan deployment

- Migration standar harus eksplisit dan dapat dilacak. Tambahkan conditional schema checks hanya bila ada kebutuhan kompatibilitas yang jelas; jangan menyembunyikan schema drift.
- Pertimbangkan tabel besar, lock, index creation, default/backfill, kompatibilitas kode lama, serta urutan deploy. Untuk perubahan breaking, gunakan pola expand-and-contract bila perlu.
- `down()` harus aman dan dipahami; jangan menghapus data secara tak terduga. Jelaskan bila rollback tidak dapat memulihkan data. Jangan menjalankan migration destruktif di environment bersama tanpa izin.

## 6. Checklist sebelum selesai

- [ ] Invariant bisnis ditulis dan ditegakkan.
- [ ] Batas transaksi jelas; efek eksternal setelah commit ditangani.
- [ ] Unique/FK/check constraint dievaluasi.
- [ ] Retry dan idempotensi didefinisikan.
- [ ] Negative test dan kasus concurrent/repeated request relevan disiapkan.
- [ ] Keterbatasan engine test vs production dicatat.
