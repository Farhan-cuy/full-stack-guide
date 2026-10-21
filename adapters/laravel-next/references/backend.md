# Backend — Laravel 11, PHP ^8.2 (inti)

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


> Panduan generik, disarikan dari project nyata (Laravel `^11.9`, `sanctum ^4`,
> `spatie/permission`, Pest ^3). Nama domain di bawah (`Item`, `tenant`, `scope aktif`)
> adalah CONTOH — ganti dengan domain project-mu, polanya yang diikuti.
> Contoh pemetaan: `prodi` = tenant, `periode aktif` = scope aktif.
> Bentuk response & nama key: lihat `contract.md`. Multi-tenant, Excel, migration, seeder:
> lihat `backend-advanced.md`.

## Isi

- [Struktur folder](#struktur-folder)
- [1. Routes](#1-routes--versioning--role-di-route)
- [2. Base Controller & response](#2-base-controller--satu-satunya-cara-return-response)
- [3. Form Request](#3-form-request)
- [4. Resource](#4-resource--list--detail)
- [5. Service](#5-service--inti-logika)
- [6. Model](#6-model)
- [7. Test & docs](#7-test--docs)

## Struktur folder

```
routes/api.php                      → prefix v1/v2 + require per modul
routes/web/v1/{modul}.php           → contoh: items, cms, master, sync
routes/web/v1/{modul}/{peran}.php   → contoh: admin, staff
routes/web/v2/...                   → versi baru per modul bila ada breaking change
app/Exceptions/BusinessException.php
app/Http/Controllers/API/.../       (satu controller = satu peran dalam satu modul)
app/Http/Requests/ApiFormRequest.php            (base)
app/Http/Requests/{Modul}/{Peran}/  (satu file per aksi)
app/Http/Resources/API/{Modul}/     (satu file per list/detail)
app/Services/{Modul}/{Peran}/       (inti logika, cerminan controller)
app/Repositories/                   → hindari kecuali integrasi khusus (mis. notif/FCM)
app/Models/
```

## 1. Routes — versioning + role di route

```php
Route::prefix('v1')->middleware('api')->group(function () {
    Route::prefix('items')->group(function () {
        require __DIR__.'/web/v1/items.php';
    });
});
```

Per peran (`routes/web/v1/items/admin.php`):

```php
Route::middleware(['auth:sanctum', 'role:admin|staff'])->group(function () {
    Route::get('/', [ItemController::class, 'index']);
    Route::get('/{id}', [ItemController::class, 'detail']);
    Route::post('/', [ItemController::class, 'store']);
});
```

Aturan:
- Setiap endpoint non-publik (read maupun write) memakai `auth:sanctum` + `role:`. Jangan taruh cek role di controller/service.
- Pemisah multi-role Spatie adalah pipe `|`. `role:admin,staff` dibaca SATU role bernama
  "admin,staff" dan selalu 403.

## 2. Base Controller — helper response (SHOULD bila ada di repo)

**SHOULD** jika project punya base helper ini: controller extends base, return lewat
`successResponse` / `respond` / `exceptionError`. Jangan `response()->json()` manual di luar
helper itu. Jika base-nya tidak ada, tiru saudara terdekat — jangan mengarang helper baru
kecuali user minta.

### Exception bisnis

Aturan bisnis yang dilanggar (kuota penuh, status tidak valid) = bukan bug. Pesannya aman
ditampilkan ke user dan tidak perlu masuk `ErrorLog`.

```php
<?php

namespace App\Exceptions;

use Exception;

class BusinessException extends Exception
{
    public function __construct(string $message, public int $status = 400)
    {
        parent::__construct($message);
    }
}
```

### Base controller (siap-copy; sesuaikan model log + tenant helper)

```php
<?php

namespace App\Http\Controllers;

use App\Exceptions\BusinessException;
use App\Models\ErrorLog;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Throwable;

abstract class Controller
{
    // Kunci yang tidak boleh masuk ErrorLog.
    private const HIDDEN_PAYLOAD_KEYS = ['password', 'password_confirmation', 'current_password', 'token', 'file'];

    // Tenant milik user, atau header X-Tenant-Id bila role super.
    // PANGGIL DI DALAM method (di dalam try), BUKAN di constructor:
    // middleware belum jalan saat constructor, jadi auth()->user() masih null.
    protected function resolveTenantId(): ?int
    {
        $user = auth()->user();
        $id = $user->tenant_id
            ?? ($user->hasRole('super') ? request()->header('X-Tenant-Id') : null);

        return $id ? (int) $id : null;
    }

    // Dipanggil dari catch. Signature ($e, $detail) kompatibel dengan pemanggilan lama.
    public function exceptionError(Throwable $e, ?string $detail = null, int $status = 500)
    {
        if ($e instanceof BusinessException) {
            return response()->json(['success' => false, 'message' => $e->getMessage(), 'errors' => null], $e->status);
        }

        if ($e instanceof ModelNotFoundException) {
            return response()->json(['success' => false, 'message' => 'Data tidak ditemukan.', 'errors' => null], 404);
        }

        // Tak terduga: log dulu (payload disaring), jangan bocorkan trace/pesan internal ke client.
        try {
            $request = request();
            ErrorLog::create([
                'user_id' => optional($request->user())->id,
                'method' => $request->method(),
                'url' => $request->fullUrl(),
                'message' => $e->getMessage(),
                'trace' => $e->getTraceAsString(),
                'payload' => json_encode($request->except(self::HIDDEN_PAYLOAD_KEYS)),
            ]);
        } catch (Throwable $logError) {
            report($logError); // gagal menulis log tidak boleh menutupi error aslinya
        }

        return response()->json([
            'success' => false,
            'message' => config('app.debug') ? $e->getMessage() : 'Terjadi kesalahan pada server.',
            'errors' => config('app.debug') ? 'Exception Error : '.($detail ?? $e->getMessage()) : null,
        ], $status);
    }

    // Sukses single object / write-path / detail.
    public function successResponse($data, $message = 'Success', $status = 200)
    {
        return response()->json(['success' => true, 'message' => $message, 'data' => $data], $status);
    }

    // Sukses LIST (ResourceCollection sudah membawa data + meta sendiri).
    public function respond($data)
    {
        return response()->json($data);
    }
}
```

> Alternatif setara (pilih salah satu per project, jangan campur): pindahkan logika
> `exceptionError` ke `->withExceptions()` di `bootstrap/app.php` untuk `api/*`, lalu
> method controller tidak perlu try/catch. Kedua gaya menghasilkan envelope yang sama.

### Tabel keputusan: helper mana?

Lihat tabel di `contract.md` §1. Ringkas: list → `respond()`, detail/write → `successResponse()`,
validasi → otomatis, exception → `exceptionError()` di `catch`.

### Template method controller

```php
use Throwable;

class ItemController extends Controller
{
    public function __construct(private ItemService $itemService) {} // constructor: inject saja

    public function index(Request $request) // read-only: Request mentah OK
    {
        try {
            $items = $this->itemService->getList($request, $this->resolveTenantId());
            return $this->respond(new ItemListResource($items));
        } catch (Throwable $e) {
            return $this->exceptionError($e);
        }
    }

    public function detail(int $id)
    {
        try {
            return $this->successResponse(
                new ItemDetailResource($this->itemService->getDetail($id)),
                'Detail item berhasil diambil'
            );
        } catch (Throwable $e) {
            return $this->exceptionError($e);
        }
    }

    public function store(StoreItemRequest $request) // mutasi: Form Request WAJIB
    {
        try {
            $item = $this->itemService->create($request->validated());
            return $this->successResponse($item, 'Item berhasil ditambahkan', 201);
        } catch (Throwable $e) {
            return $this->exceptionError($e);
        }
    }
}
```

Default project asal (SHOULD — alternatif `withExceptions()` setara, lihat catatan di atas):
- Tiap method = `try { service → helper } catch (Throwable $e) { exceptionError }`. `Throwable`,
  bukan `Exception`, supaya `TypeError`/`Error` tidak lolos jadi halaman 500 HTML.
- Pilih satu gaya per project: try/catch per method ATAU handler global. Jangan dicampur,
  karena dua jalur envelope yang berbeda sulit diaudit dan gampang menghasilkan format beda.
- Constructor injection saja. Jangan `new Service()`, jangan facade di controller.
- Constructor TANPA logika: tidak ada query, `auth()`, atau scope di sana (middleware belum jalan;
  exception dari constructor lolos dari `try/catch` sehingga tidak berformat envelope).
  Butuh scope aktif → getter lazy di dalam method, atau oper dari controller ke service.
- Jangan `DB::beginTransaction/commit/rollback/transaction` di controller — milik service.
- Jangan query Eloquent/`DB::table` langsung di controller.
- Pesan sukses Bahasa Indonesia spesifik per aksi.

### Sekat file controller (urutan dari atas ke bawah)

1. `namespace` + `use` (jangan import yang tak dipakai)
2. Constructor (inject service) — tanpa logika lain
3. Method READ — `index`, `detail`: `Request` mentah → `respond(Resource)` / `successResponse(Resource)`
4. Method WRITE — `store`, `update`, `destroy`, aksi custom: Form Request → `successResponse($result, 'pesan')`
5. Method EXPORT/IMPORT — response file langsung dari service
6. Helper `private/protected` — paling bawah

Satu controller = satu peran dalam satu modul. Butuh peran lain → controller baru.

## 3. Form Request

Satu file per aksi, extends base `ApiFormRequest`. Base memuat dua hal yang gampang
terlupa; subclass hanya `rules()` + `messages()`.

```php
<?php

namespace App\Http\Requests;

use Illuminate\Contracts\Validation\Validator;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Http\Exceptions\HttpResponseException;

abstract class ApiFormRequest extends FormRequest
{
    // Selalu true — otorisasi ada di route (middleware role), bukan di sini.
    public function authorize(): bool
    {
        return true;
    }

    // Tanpa ini validasi gagal membalas redirect HTML, bukan JSON.
    protected function failedValidation(Validator $validator): void
    {
        throw new HttpResponseException(response()->json([
            'success' => false,
            'message' => 'Validasi gagal.',
            'errors' => $validator->errors(),
        ], 422));
    }
}
```

```php
<?php

namespace App\Http\Requests\Items\Admin;

use App\Http\Requests\ApiFormRequest;

class StoreItemRequest extends ApiFormRequest
{
    public function rules(): array
    {
        return [
            'nama' => ['required', 'string', 'max:100'],       // array notation, bukan 'required|string'
            'group_ids' => ['required', 'array', 'min:1'],
            'group_ids.*' => ['exists:groups,id'],
            'is_active' => ['required', 'boolean'],
        ];
    }

    // Pesan Bahasa Indonesia per-field. Jangan andalkan pesan Inggris bawaan.
    public function messages(): array
    {
        return [
            'nama.required' => 'Nama wajib diisi.',
            'group_ids.required' => 'Grup wajib dipilih.',
            'group_ids.*.exists' => 'Grup dengan ID tersebut tidak ditemukan.',
            'is_active.required' => 'Status wajib diisi.',
        ];
    }
}
```

Read-only (`index/detail/export`) boleh `Request` mentah. Semua mutasi WAJIB Form Request.
Controller memakai `$request->validated()`, bukan `$request->all()`.

## 4. Resource — list + detail

`public static $wrap = null;` WAJIB di tiap Resource/Collection (matikan envelope `data`
bawaan Laravel; envelope diatur manual sesuai `contract.md`).

### Collection (list paginate)

Service me-return paginator mentah; Resource memetakan item dan merakit `meta.pagination`.
`with()` dan `paginationInformation()` return `[]` supaya meta bawaan Laravel tidak dobel.

```php
<?php

namespace App\Http\Resources\API\Items;

use Illuminate\Http\Resources\Json\ResourceCollection;

class ItemListResource extends ResourceCollection
{
    public static $wrap = null;

    public function toArray($request): array
    {
        return [
            'data' => $this->collection->map(fn ($item) => [
                'id' => $item->id,
                'nama' => $item->nama ?? null,         // nullable → selalu `?? null`
                // relasi: null bila FK kosong, JANGAN objek setengah isi
                'group' => $item->group_id ? [
                    'id' => $item->group_id,
                    'nama' => $item->group_nama ?? null,
                ] : null,
                'foto' => $item->foto_path ? ImageService::url($item->foto_path) : null, // field turunan dihitung di sini
            ])->all(),
            'meta' => [
                'success' => true,
                'message' => 'Data berhasil diambil',
                'pagination' => [
                    'total' => $this->resource->total(),
                    'per_page' => $this->resource->perPage(),
                    'current_page' => $this->resource->currentPage(),
                    'last_page' => $this->resource->lastPage(),
                ],
            ],
        ];
    }

    public function with($request) { return []; }

    public function paginationInformation($request, $paginated, $default) { return []; }
}
```

### Detail — `JsonResource` + `$wrap = null`

Field sama dengan versi list (key konsisten) + field mahal tambahan (relasi dalam, riwayat).
Read-path wajib Resource. Write-path boleh `successResponse($model)`, tapi pastikan model tidak
membocorkan kolom sensitif (`$hidden`).

## 5. Service — inti logika

**Kapan:** transaksi lintas tabel, aturan bisnis, import/export, atau method yang gemuk.
**Kapan skip:** persist/update/hapus pendek yang di saudara terdekat juga tanpa service — controller
tetap tipis (Form Request → model/query → Resource/helper). Jangan bikin service kosong sebagai
cerminan controller.

Satu service = satu peran dalam satu modul. Return: paginator / model / array — JANGAN return
response atau Resource dari service.

```php
<?php

namespace App\Services\Items;

use App\Exceptions\BusinessException;
use App\Models\Item;
use Illuminate\Http\Request;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\DB;

class ItemService
{
    private ?ActiveScope $scope = null;

    // Constructor: inject saja. Tanpa query / getOrFail di sini.
    public function __construct(private ImageService $images) {}

    // Scope aktif di-memoize LAZY: exception-nya terjadi di dalam try/catch controller.
    private function scope(): ActiveScope
    {
        return $this->scope ??= ActiveScope::getOrFail();
    }

    // READ — return paginator MENTAH (mapping urusan Resource).
    public function getList(Request $request, ?int $tenantId): LengthAwarePaginator
    {
        return DB::table('items')
            ->when($tenantId, fn ($q) => $q->where('items.tenant_id', $tenantId)) // DB::table tak kena Global Scope
            ->when($request->filled('search'), fn ($q) => $q->where('nama', 'like', '%'.$request->string('search').'%'))
            ->orderByDesc('id')
            ->paginate(min($request->integer('limit', 10), 100));
    }

    public function getDetail(int $id): Item
    {
        return Item::with('group')->findOrFail($id); // ModelNotFoundException → 404 oleh exceptionError
    }

    // WRITE — transaction di sini; validasi bisnis SEBELUM menulis.
    public function create(array $data): Item
    {
        return DB::transaction(function () use ($data) {
            if ($this->isQuotaFull($data['group_ids'])) {
                throw new BusinessException('Kuota grup sudah penuh.');
            }

            return Item::create($data);
        });
    }

    // Helper private PALING bawah.
    private function isQuotaFull(array $groupIds): bool
    {
        // ...
        return false;
    }
}
```

Aturan:
- Transaction di service, bukan controller. Hindari `auth()` di service (inject dari controller).
- Pelanggaran aturan bisnis → `throw new BusinessException('pesan Indonesia')`; controller yang
  mengubahnya menjadi response.
- Query berat: query builder + `leftJoinSub` untuk agregat; hindari N+1 (`with()` / `withCount()`).
- Urutan file: use → property → constructor → READ → WRITE → EXPORT → helper private.

## 6. Model

- `$fillable` eksplisit untuk model baru (jangan `$guarded = ['id']`).
- `User`: `casts()` dengan `hashed`, `HasRoles + HasApiTokens + SoftDeletes`.
- Pola bagus: scope (`scopeActive()`), static helper scope aktif, trait isolasi tenant
  (`backend-advanced.md` §A).
- Migration: `foreignId()->constrained('tabel','id')`; tambah `->cascadeOnDelete()` untuk yang baru.
  Detail migration: `backend-advanced.md` §C.

## 7. Test & docs

Tiap service/endpoint baru butuh test (project asal hanya punya 2 unit test — jangan ditiru).
Minimal: satu feature test untuk happy path dan satu untuk 422.

```php
it('menolak store tanpa nama dengan 422 berformat envelope', function () {
    $user = User::factory()->create()->assignRole('admin');

    $this->actingAs($user, 'sanctum')
        ->postJson('/api/v1/items', [])
        ->assertStatus(422)
        ->assertJson(['success' => false, 'message' => 'Validasi gagal.'])
        ->assertJsonValidationErrors(['nama']);
});

it('mengembalikan list dengan meta.pagination', function () {
    $user = User::factory()->create()->assignRole('admin');
    Item::factory()->count(3)->create();

    $this->actingAs($user, 'sanctum')
        ->getJson('/api/v1/items?limit=2')
        ->assertOk()
        ->assertJsonStructure(['data', 'meta' => ['success', 'message', 'pagination' => ['total', 'per_page', 'current_page', 'last_page']]]);
});
```

Docs: `docs/technical-architecture.md` (aliran Route → Controller → Service → Request/Resource → Model).
