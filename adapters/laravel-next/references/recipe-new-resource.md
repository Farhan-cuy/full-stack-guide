# Recipe — tambah resource CRUD baru (BE + FE)

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


Checklist dialect Laravel API + Next.js App Router (SHOULD jika helper di Langkah 0 skill terdeteksi).
Kalau `ApiFormRequest` / `request<T>()` / `withAuth` tidak ada, tiru saudara terdekat —
jangan mengikuti tabel ini mentah-mentah.

Contoh nama: `Item`, modul `items`, peran `admin`. Muat bersama `contract.md`.
Ganti ke domain project. Kerjakan BE dulu.

## Sebelum mulai

- [ ] Cek `composer.json` / `package.json` (stack sesuai asumsi? versi zod?).
- [ ] Cari **satu** resource serupa, baca lengkap, tulis kontrak singkat (`workflow.md` §2-§3).
- [ ] Scope (SKILL Langkah 0.5): daftar aksi + field yang dipakai UI. Tabel di bawah = menu, bukan wajib semua.
- [ ] Tenant / Excel / v2 / tour: hanya jika diminta atau dibutuhkan. Authorization object-level tetap harus ditegakkan; gunakan Policy/Gate/query scope sesuai arsitektur, walaupun saudara terdekat tidak memilikinya.

Lewati baris yang tidak punya konsumen. Contoh: list-only → jangan Detail Resource + `getDetail` + halaman detail. CRUD sederhana tanpa aturan bisnis → Service tidak wajib bila saudara terdekat juga memakai pola langsung ke model; jangan menggunakan jumlah baris sebagai satu-satunya kriteria.

## Backend (`backend.md`, `backend-advanced.md`)

| # | File | Catatan |
|---|---|---|
| 1 | `database/migrations/<ts>_create_items_table.php` | migration standar eksplisit dan terlacak; jangan menambah `hasTable`/conditional schema guard secara default. Gunakan FK dan cascade hanya jika aturan lifecycle data memang mengizinkan penghapusan berantai — `backend-advanced.md` §C |
| 2 | `app/Models/Item.php` | `$fillable` eksplisit; `use BelongsToTenant` bila tenant-scoped — §A |
| 3 | `app/Http/Requests/Items/Admin/StoreItemRequest.php`, `UpdateItemRequest.php` | extends `ApiFormRequest`; `rules()` + pesan Indonesia per field |
| 4 | Resource yang **dipakai** (`ItemListResource` dan/atau `ItemDetailResource`) | `$wrap = null`; key list = key detail bila keduanya ada. Jangan buat yang tidak dipanggil |
| 5 | `app/Services/Items/Admin/ItemService.php` | **bila perlu** (txn lintas tabel, aturan bisnis, import, logika gemuk). Constructor inject; READ return mentah; WRITE dalam `DB::transaction`; `BusinessException` |
| 6 | `app/Http/Controllers/API/Items/Admin/ItemController.php` | tipis; SHOULD: `try/catch (Throwable)` → `exceptionError` *atau* `withExceptions()` — ikut gaya project; scope dibaca di dalam method |
| 7 | `routes/web/v1/items/admin.php` (+ require di `routes/web/v1/items.php`) | `auth:sanctum` + `role:admin\|...` (pipe) |
| 8 | `tests/Feature/Items/ItemTest.php` | minimal happy path + 422 + list ber-`meta.pagination` |

Verifikasi: `php artisan route:list --path=v1/items`, `php artisan test --filter=ItemTest`, `vendor/bin/pint --test`.

## Frontend (`frontend.md`, `frontend-ui.md`)

| # | File | Catatan |
|---|---|---|
| 9 | `types/item/item.ts` | `Item`, `CreateItemPayload`, `UpdateItemPayload`; key `snake_case` sama dengan BE; `types/api.ts` sudah ada |
| 10 | `api/item/item.ts` + wiring di `api/index.ts` | factory memakai `request<T>()`; `getAll({page, limit, search, type})` |
| 11 | `app/(subapps)/<domain>/items/page.tsx` | ikut saudara terdekat; subapp cookie/context: wrapper tipis + Suspense. Jangan cap `"use client"` otomatis |
| 12 | `.../items/table.tsx` | bila SWR dipakai: `useSWR([KEY, ...params], ...)`, guard `isLoading/error`, `refreshAll()` setelah CRUD |
| 13 | `.../items/columns.tsx` | factory `Columns(currentPage, perPage, onEdit)` |
| 14 | `.../items/dialog-pop-up.tsx` | zod schema di file; `onSubmit` mengembalikan `SubmitResult`; tutup hanya saat `ok` |
| 15 | `app/(subapps)/<domain>/layout.tsx` | item sidebar hanya jika halaman itu masuk navigasi; permission = nama subapp. Jangan tour/KPI/empty-state ilustrasi kecuali saudara punya |

Verifikasi: `npm run lint`, `npx tsc --noEmit`. Cek manual: tambah (sukses), tambah (kosong → error per field
dan dialog tetap terbuka), hapus (list ter-refresh), token dihapus lalu aksi (redirect `/login`).

## Sebelum melapor

- [ ] Tidak ada `any` baru, tidak ada `fetch` langsung, tidak ada `DB::transaction` di controller.
- [ ] Output Contract di `SKILL.md` terisi, termasuk adaptasi dari template dan pelanggaran lama yang tidak disentuh.
