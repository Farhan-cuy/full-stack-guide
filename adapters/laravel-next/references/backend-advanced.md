# Backend — topik lanjutan

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


Muat file ini hanya bila tugasnya menyentuh multi-tenant, import/export Excel, migration, atau seeder.
Dasar (controller, request, resource, service) ada di `backend.md`.

## Isi

- [A. Multi-tenancy — Global Scope + Trait](#a-multi-tenancy--global-scope--trait)
- [B. Import/Export Excel](#b-importexport-excel)
- [C. Migration & Seeder](#c-migration--seeder)

## A. Multi-tenancy — Global Scope + Trait

**Default untuk project multi-tenant: Global Scope.** Model ber-trait ini otomatis terfilter
berdasarkan tenant user dan otomatis terisi saat create, menggantikan `where('tenant_id', ...)` manual.

`resolveTenantId()` (base controller) hanya untuk kasus eksplisit: `DB::table` (tidak terkena
scope), export, atau override oleh role `super`. Jangan memakai dua mekanisme untuk query yang sama.

Pemakaian `auth()` di dalam Scope/trait ini diperbolehkan: scope adalah infrastruktur yang
berjalan saat query dibangun, bukan logika service.

```php
<?php

namespace App\Models\Scopes;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Scope;
use Illuminate\Support\Facades\Schema;

class TenantScope implements Scope
{
    private static array $columnCache = [];

    // Tabel yang filternya lewat relasi, bukan kolom langsung. Isi sesuai project.
    private const VIA_RELATION = [
        // 'students' => 'user',
    ];

    // Cache Schema::hasColumn — jangan query schema berkali-kali per request.
    private static function hasColumn(string $table, string $col): bool
    {
        return self::$columnCache["$table.$col"] ??= Schema::hasColumn($table, $col);
    }

    public function apply(Builder $builder, Model $model): void
    {
        if (! auth()->check()) {
            return;
        }

        $user = auth()->user();
        $table = $model->getTable();

        if ($user->tenant_id !== null) {
            if (isset(self::VIA_RELATION[$table])) {
                $builder->whereHas(self::VIA_RELATION[$table], fn ($q) => $q->where('tenant_id', $user->tenant_id));
            } elseif (self::hasColumn($table, 'tenant_id')) {
                $builder->where($table.'.tenant_id', $user->tenant_id);
            }
            return;
        }

        // User tanpa tenant_id (super) → baca dari header/query param
        if ($user->hasRole('super')) {
            $tenantId = request()->header('X-Tenant-Id') ?? request()->query('tenant_id');
            if ($tenantId && self::hasColumn($table, 'tenant_id')) {
                $builder->where($table.'.tenant_id', $tenantId);
            }
        }
    }
}
```

```php
<?php

namespace App\Traits;

use App\Models\Scopes\TenantScope;
use App\Models\Tenant;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

trait BelongsToTenant
{
    protected static function bootBelongsToTenant(): void
    {
        static::addGlobalScope(new TenantScope);

        // Auto-fill tenant_id saat create (bila user punya tenant)
        static::creating(function ($model) {
            if (empty($model->tenant_id) && auth()->check() && auth()->user()->tenant_id !== null) {
                $model->tenant_id = auth()->user()->tenant_id;
            }
        });
    }

    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class, 'tenant_id');
    }
}
```

Aturan:
- Model tenant baru → `use BelongsToTenant;`.
- **Model `User` JANGAN memakai trait ini.** `auth()->user()` di dalam scope mengambil User; kalau
  User terkena scope yang sama terjadi rekursi tak berujung.
- `DB::table(...)` TIDAK terkena Global Scope → filter manual lewat `$tenantId` dari controller.
- `Model::withoutGlobalScope(TenantScope::class)` hanya untuk seeder/migrasi, dengan alasan jelas.

## B. Import/Export Excel

Pakai `maatwebsite/excel`. Satu class per operasi di `app/Imports/` atau `app/Exports/`.

### Import

```php
<?php

namespace App\Imports;

use App\Models\Item;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\WithChunkReading;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithValidation;

class ItemImport implements ToModel, WithHeadingRow, WithValidation, WithChunkReading
{
    public int $imported = 0;
    public int $existing = 0;
    public int $skipped = 0;

    // Alias header yang sering berbeda antar file user.
    private const ALIAS = ['nama_lengkap' => 'nama', 'npm' => 'nim'];

    // Normalisasi dipanggil SEBELUM validasi dan sebelum model().
    public function prepareForValidation($data, $index)
    {
        return $this->normalize($data);
    }

    private function normalize(array $row): array
    {
        $out = [];
        foreach ($row as $key => $value) {
            $clean = strtolower(str_replace([' ', '-'], '_', trim((string) $key)));
            $out[self::ALIAS[$clean] ?? $clean] = $value;
        }
        return $out;
    }

    public function model(array $row)
    {
        $row = $this->normalize($row);

        if (empty($row['nim'])) {
            $this->skipped++;
            return null;
        }

        // firstOrCreate membantu menghindari duplikasi pada alur normal, tetapi bukan jaminan idempotensi di bawah konkurensi tanpa unique constraint dan strategi konflik yang tepat
        $item = Item::firstOrCreate(
            ['nim' => $row['nim']],
            ['nama' => $row['nama'] ?? null]
        );

        // firstOrCreate mengembalikan model LAMA bila sudah ada — jangan dihitung sebagai created.
        $item->wasRecentlyCreated ? $this->imported++ : $this->existing++;

        return $item;
    }

    public function rules(): array
    {
        return ['*.nim' => ['required', 'string', 'max:20'], '*.nama' => ['nullable', 'string']];
    }

    // Hanya berefek karena class ini implements WithChunkReading.
    public function chunkSize(): int
    {
        return 500;
    }
}
```

Controller tipis; logika di service. **Jangan** membungkus dengan `DB::transaction` di controller:
`maatwebsite/excel` sudah membungkus import dalam transaksi lewat `config/excel.php`
(`transactions.handler = 'db'`).

```php
// Service
public function import(UploadedFile $file): array
{
    set_time_limit(300); // file besar
    $import = new ItemImport;
    Excel::import($import, $file);

    return ['imported' => $import->imported, 'existing' => $import->existing, 'skipped' => $import->skipped];
}

// Controller
public function import(ImportItemRequest $request)
{
    try {
        return $this->successResponse($this->itemService->import($request->file('file')), 'Import selesai');
    } catch (Throwable $e) {
        return $this->exceptionError($e);
    }
}
```

### Export

```php
use PhpOffice\PhpSpreadsheet\Worksheet\Worksheet;

class ItemExport implements FromCollection, WithHeadings, WithStyles
{
    public function collection()
    {
        return Item::query()->get()->map(fn ($x) => [
            $x->nim ?? '', $x->nama ?? '', $x->email ?? '', // null di sel Excel bisa memicu error → `?? ''`
        ]);
    }

    public function headings(): array { return ['NIM', 'Nama', 'Email']; }

    public function styles(Worksheet $sheet): array
    {
        return [1 => ['font' => ['bold' => true, 'size' => 12]]];
    }
}
```

Aturan: normalisasi nilai kosong per sel sesuai skema; gunakan `WithChunkReading` untuk file besar (ambang ditentukan dari ukuran/memori aktual); `firstOrCreate/updateOrCreate` hanya bila cocok dengan kunci bisnis. Untuk jaminan anti-duplikasi di bawah konkurensi, evaluasi unique constraint dan conflict/upsert handling; metode ORM saja tidak menjamin idempotensi. Counter (`$imported`, `$skipped`) di class boleh dipakai untuk ringkasan response.

## C. Migration & Seeder

### Migration standar dan kompatibilitas schema

Migration normal dijalankan dan dilacak oleh migration repository Laravel. Buat perubahan schema eksplisit; jangan menyamarkan schema drift dengan guard kondisional tanpa alasan kompatibilitas yang nyata. Contoh migration standar:

```php
public function up(): void
{
    Schema::create('items', function (Blueprint $table) {
        $table->id();
        $table->foreignId('tenant_id')->constrained();
        $table->string('nama');
        $table->timestamps();
    });
}
```

- Gunakan `Schema::hasTable`/`hasColumn` hanya jika migration memang harus mendukung kondisi schema yang sudah ada dan kebutuhan itu terdokumentasi. Jangan gunakan guard untuk membuat migration tampak sukses ketika schema drift atau urutan deploy salah.
- Gunakan `cascadeOnDelete()` hanya bila lifecycle data mengizinkan penghapusan anak secara otomatis; jika tidak, pilih restrict/nullify atau strategi domain yang tepat.
- Untuk tabel besar atau perubahan produksi, evaluasi lock, backfill, indeks, kompatibilitas versi kode, urutan deploy, dan kemampuan rollback sebelum menjalankan migration.
- Naming: `YYYY_MM_DD_HHMMSS_create_x_table.php`; satu timestamp per migration (kecuali urutan eksplisit `000001`, `000002`).
- Hapus blok `Schema::create` yang dikomentari.

### Seeder self-healing

```php
public function run(): void
{
    Role::firstOrCreate(['name' => 'admin']);
    Role::firstOrCreate(['name' => 'staff']);

    // Rename role lama → baru (bila ada migrasi nama)
    Role::where('name', 'old-staff')->first()?->update(['name' => 'staff']);

    // Hapus role obsolete
    Role::where('name', 'old-role')->delete();

    app()[PermissionRegistrar::class]->forgetCachedPermissions(); // wajib setelah ubah role/permission
}
```

Aturan: semua seeder `firstOrCreate` / `updateOrCreate`, jangan `create` mentah.
