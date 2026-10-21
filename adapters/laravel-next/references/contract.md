# Kontrak API BE ↔ FE

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


Baca file ini setiap kali menyentuh dua sisi. Ini acuan **bentuk yang disepakati** antar
reference skill. Kalau implementasi repo menyimpang, laporkan konflik — jangan diam-diam
menganggap file ini atau kode salah. Hirarki lengkap ada di `SKILL.md`.

## Isi

1. [Bentuk response](#1-bentuk-response)
2. [Query param list](#2-query-param-list)
3. [Penamaan & format data](#3-penamaan--format-data)
4. [Type FE (`types/api.ts`)](#4-type-fe-typesapits)
5. [Aksi FE per status](#5-aksi-fe-per-status)
6. [Versioning & validasi](#6-versioning--validasi)

## 1. Bentuk response

| Kasus | Status | Body | Helper BE |
|---|---|---|---|
| List paginate | 200 | `{data:[...], meta:{success, message, pagination:{total, per_page, current_page, last_page}}}` | `respond(new XListResource($paginator))` |
| Detail | 200 | `{success:true, message, data:{...}}` | `successResponse(new XDetailResource($m), '...')` |
| Create/update/delete | 200/201 | `{success:true, message, data}` | `successResponse($result, '... berhasil ...')` |
| Validasi gagal | 422 | `{success:false, message:'Validasi gagal.', errors:{field:[msg]}}` | otomatis (`ApiFormRequest`) |
| Aturan bisnis dilanggar | 400 (atau status di exception) | `{success:false, message, errors:null}` | `throw new BusinessException('...')` |
| Tidak ditemukan | 404 | `{success:false, message:'Data tidak ditemukan.', errors:null}` | `ModelNotFoundException` |
| Tak terduga | 500 | `{success:false, message:'Terjadi kesalahan pada server.', errors:null}` (detail hanya saat `APP_DEBUG`) | `exceptionError()` |
| Tanpa token / token mati | 401 | `{message:'Unauthenticated.'}` | middleware `auth:sanctum` |
| Role tak cukup | 403 | `{message:...}` | middleware `role:` |

Catatan: pada list, `success` ada di `meta`, bukan di root. Jangan membaca `res.success` dari response list.

## 2. Query param list

| Param | Tipe | Default | Catatan |
|---|---|---|---|
| `page` | int ≥ 1 | 1 | dibaca otomatis oleh `paginate()` |
| `limit` | int | 10 | BE batasi maksimal 100: `min($request->integer('limit', 10), 100)` |
| `search` | string | kosong | BE: `when($request->filled('search'), ...)` |
| `type` / filter lain | string | `all` | nama filter = nama kolom/atribut, konsisten FE & BE |

FE menyusun query dengan `URLSearchParams` (`toQuery()` di `lib/utils`), tidak dengan template string.

## 3. Penamaan & format data

- Key JSON = `snake_case`; type FE mengikuti persis (`per_page`, bukan `perPage`). Satu aturan,
  tanpa mapper. Kalau project memakai camelCase, tulis keputusan itu di sini dan konsisten.
- Key list dan detail HARUS sama (`id`, `nama`) — bukan `mahasiswa_id` di satu tempat dan `id` di tempat lain.
- Nullable: BE `?? null` per field; relasi bersarang `null` bila FK kosong, jangan objek setengah isi.
- Tanggal: string ISO 8601 dari BE; format tampilan di FE (`formatDate` di `lib/utils`, fallback `"-"`).
- Field turunan (URL file, label) dihitung di Resource, bukan di FE.
- Pesan untuk user: Bahasa Indonesia, spesifik per aksi (`'... berhasil diperbaharui'`, bukan `'Success'`).

## 4. Type FE (`types/api.ts`)

Factory dan hook memakai type ini; tidak ada `any` dari `r.json()`.

```ts
export interface ApiResponse<T> {
  success: true;
  message: string;
  data: T;
}

export interface Pagination {
  total: number;
  per_page: number;
  current_page: number;
  last_page: number;
}

export interface Paginated<T> {
  data: T[];
  meta: { success: boolean; message: string; pagination: Pagination };
}

export type FieldErrors = Record<string, string[]>;
```

`ApiError` (lihat `frontend.md` §2) membawa `status`, `message`, `errors` agar UI bisa membedakan 422 dari lainnya.

## 5. Aksi FE per status

`request()` melempar `ApiError` untuk semua status gagal; pemanggil memutuskan:

| Status | Aksi FE |
|---|---|
| 2xx | render; `mutate` (halaman ini / semua halaman resource) setelah CRUD |
| 422 | `form.setError` per field dari `errors`; dialog tetap terbuka; jangan toast generik saja |
| 400 / 404 | `toast.error(message)` |
| 401 | `request()` hapus cookie + redirect `/login` (juga di tengah sesi, bukan hanya saat mount) |
| 403 | redirect `/unauthorized` (HOC untuk page; `request()` melempar `ApiError` 403 untuk aksi) |
| 500 / jaringan | `toast.error(message)`; tabel menampilkan `ErrorState` dengan `retry` |

## 6. Versioning & validasi

- Breaking change → endpoint `v2` baru; FE membuat `*-v2.ts` terpisah. Jangan ubah signature
  factory/endpoint lama (klien lama masih memakainya).
- Validasi FE (RHF + zod) mencerminkan `rules()` BE, tetapi BE tetap sumber kebenaran terakhir.
