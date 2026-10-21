# Frontend — Next.js App Router + TS (inti)

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


> Panduan generik, disarikan dari project nyata (`next`, `react ^18`, `TS ^5`, `tailwind`,
> shadcn + Radix, `swr`, `cookies-next`, `sonner`, `RHF + zod`). Nama domain di bawah
> (`Resource`, `Item`) adalah CONTOH — ganti dengan domain project-mu.
> Bentuk response, query param, dan type API: `contract.md`.
> Dialog form, kolom tabel, sidebar, tour, styling: `frontend-ui.md`.

Config project asal: `next.config.ts` memakai `ignoreBuildErrors` + `images.unoptimized: true`.
Kalau flag itu ada, build TIDAK menangkap error tipe — `npx tsc --noEmit` wajib. Cocokkan
`tsconfig` dan eslint dengan repo, jangan asumsikan identik.

## Isi

- [Struktur folder](#struktur-folder)
- [1. Page](#1-page--rendering-sesuai-kebutuhan-wrapper-tipis)
- [2. API layer](#2-api-layer--request-sentral--factory)
- [3. Data fetching — SWR](#3-data-fetching--swr)
- [4. Auth — HOC](#4-auth--hoc-bukan-middleware)
- [5. Types](#5-types)
- [6. Toast & konstanta](#6-toast--konstanta)

## Struktur folder

```
app/layout.tsx + provider.tsx   (Server: font + providers global + Toaster)
app/(auth)/login,callback,unauthorized
app/(subapps)/<domain>/         (satu folder per fitur)
api/index.ts                    (header helper, request(), wiring service)
api/<domain>/*.ts               (factory client, bukan axios instance)
lib/ (utils: cn, toQuery, formatDate · constant · toast-response · form-errors)
hooks/  context/ (minimal: hanya state benar-benar global, mis. profile)
components/ui/ (shadcn) + komponen shared per fitur
types/api.ts + types/<domain>/*.ts
```

## 1. Page — rendering sesuai kebutuhan, wrapper tipis

```tsx
"use client";
import { Suspense } from "react";

export default function DataItemPage() {
  return (
    <>
      <DashboardHeader />
      {/* useSearchParams di child butuh Suspense (Next 14.1+/15) agar build tidak error */}
      <Suspense fallback={<TableSkeleton />}>
        <ItemTable />
      </Suspense>
    </>
  );
}
// logika di table.tsx / client-page.tsx, bukan page.tsx
```

Untuk subapp asal yang bergantung pada kredensial browser/context, ikuti client + SWR. Namun, jangan menerapkan `"use client"` ke semua halaman secara otomatis. Evaluasi Server Components/server-side fetching jika sesuai model autentikasi, boundary keamanan, dan arsitektur project; jangan pernah mengekspos secret ke client.

## 2. API layer — `request()` sentral + factory

**SHOULD** jika `api/index.ts` `request<T>()` ada: semua request lewat dua lapis ini.
Jangan axios instance baru, jangan `fetch` URL hardcode di component. Jika helper itu
tidak ada, tiru client yang sudah dipakai repo.

### Lapis 1: `api/index.ts` (template)

```ts
import { deleteCookie, getCookie } from "cookies-next";
import { API_URL, TOKEN_COOKIE_KEY } from "@/lib/constant";

const stripQuotes = (v: string) => v.replace(/^"|"$/g, "").trim();

// Token: document.cookie dulu, fallback cookies-next. Tidak menebak cookie lain.
const getTokenFromCookie = (name: string): string | undefined => {
  if (typeof window !== "undefined") {
    const prefix = `${name}=`;
    for (const part of document.cookie.split(";")) {
      const c = part.trim();
      if (c.startsWith(prefix)) return stripQuotes(decodeURIComponent(c.slice(prefix.length))) || undefined;
    }
  }
  const fallback = getCookie(name);
  return typeof fallback === "string" ? stripQuotes(fallback) || undefined : undefined;
};

export const configurePublicHeaders = ({ contentType = "application/json" } = {}) => {
  const headers = new Headers();
  headers.append("Content-Type", contentType);
  headers.append("Accept", "application/json");
  return headers;
};

// - Upload FormData: isFileUpload: true (JANGAN set Content-Type manual; browser mengisi boundary)
// - Endpoint lintas-tenant: skipTenant: true
// - Tenant aktif: satu sumber (context menulis ke localStorage "active_tenant_id"), dibaca di sini
export const configureHeaders = ({
  contentType = "application/json",
  token = "",
  isFileUpload = false,
  skipTenant = false,
  tenantId,
}: {
  contentType?: string; token?: string; isFileUpload?: boolean;
  skipTenant?: boolean; tenantId?: number | string | null;
} = {}) => {
  const headers = new Headers();
  if (!isFileUpload) headers.append("Content-Type", contentType);
  headers.append("Accept", "application/json");

  const final = token.trim() || getTokenFromCookie(TOKEN_COOKIE_KEY);
  if (final) headers.append("Authorization", `Bearer ${final}`);

  if (!skipTenant) {
    const id = tenantId ?? (typeof window !== "undefined" ? localStorage.getItem("active_tenant_id") : null);
    if (id) headers.append("X-Tenant-Id", String(id));
  }
  return headers;
};

// ---- request(): satu-satunya tempat fetch ke BE ----
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public errors?: Record<string, string[]> | string | null,
  ) {
    super(message);
  }
}

const handleUnauthorized = () => {
  if (typeof window === "undefined") return;
  deleteCookie(TOKEN_COOKIE_KEY);
  if (!window.location.pathname.startsWith("/login")) window.location.replace("/login");
};

// Melempar ApiError untuk jaringan putus, !ok, atau success === false.
// Konsekuensi: SWR `error` terpicu, handleToastPromise menampilkan pesan gagal yang benar.
export async function request<T>(url: string, init: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(url, init);
  } catch {
    throw new ApiError("Tidak dapat terhubung ke server.", 0);
  }

  if (res.status === 401) {
    handleUnauthorized();
    throw new ApiError("Sesi berakhir, silakan login kembali.", 401);
  }

  const body = await res.json().catch(() => null); // 500 HTML bukan JSON → null
  if (!res.ok || body?.success === false) {
    throw new ApiError(body?.message ?? res.statusText ?? "Terjadi kesalahan.", res.status, body?.errors);
  }
  return body as T;
}

// Download file: SATU-SATUNYA pengecualian bentuk response (blob).
export async function requestBlob(url: string, init: RequestInit): Promise<Blob> {
  const res = await fetch(url, init);
  if (res.status === 401) handleUnauthorized();
  if (!res.ok) throw new ApiError("Gagal mengunduh file.", res.status);
  return res.blob();
}
```

Wiring service — satu factory satu service:

```ts
export const ResourceService = ResourceFactory({
  baseUrl: API_URL || "",
  config: () => configureHeaders(),                    // default: auth + tenant
});
export const PublicResourceService = PublicFactory({
  baseUrl: API_URL || "",
  config: () => configurePublicHeaders(),              // publik: tanpa token
});
export const CrossTenantService = OtherFactory({
  baseUrl: API_URL || "",
  config: () => configureHeaders({ skipTenant: true }), // lintas tenant
});
```

`lib/utils.ts`:

```ts
export const toQuery = (params: Record<string, string | number | null | undefined>) => {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") q.set(k, String(v));
  }
  return q.toString(); // sudah ter-encode
};
```

### Lapis 2: factory per domain `api/<domain>/*.ts`

Satu file per resource. Operasi standar: `getAll` → `getById` → `create` → `update` → `delete`
(+ `import`/`downloadTemplate` bila ada Excel). Semua bertipe — tidak ada `any`.

```ts
import { request, requestBlob } from "@/api";
import { toQuery } from "@/lib/utils";
import type { ApiResponse, Paginated } from "@/types/api";
import type { Item, CreateItemPayload, UpdateItemPayload } from "@/types/item/item";

const ItemFactory = ({ baseUrl, config }: { baseUrl: string; config: () => Headers }) => {
  const resource = "/items";

  return {
    getAll: (p: { page: number; limit: number; search?: string; type?: string }) =>
      request<Paginated<Item>>(`${baseUrl}${resource}?${toQuery(p)}`, { method: "GET", headers: config() }),

    getById: (id: number) =>
      request<ApiResponse<Item>>(`${baseUrl}${resource}/${id}`, { method: "GET", headers: config() }),

    create: (data: CreateItemPayload) =>
      request<ApiResponse<Item>>(`${baseUrl}${resource}`, { method: "POST", body: JSON.stringify(data), headers: config() }),

    update: (id: number, data: UpdateItemPayload) =>
      request<ApiResponse<Item>>(`${baseUrl}${resource}/${id}`, { method: "PATCH", body: JSON.stringify(data), headers: config() }),

    delete: (id: number) =>
      request<ApiResponse<null>>(`${baseUrl}${resource}/${id}`, { method: "DELETE", headers: config() }),

    // FormData: headers dari config() TANPA Content-Type (browser mengisi boundary)
    import: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return request<ApiResponse<{ imported: number; skipped: number }>>(
        `${baseUrl}${resource}/import`,
        { method: "POST", body: form, headers: config() },
      );
    },

    downloadTemplate: () => requestBlob(`${baseUrl}${resource}/template`, { method: "GET", headers: config() }),
  };
};
export default ItemFactory;
```

Untuk import dengan factory yang `config()`-nya memuat `Content-Type`, buat wiring terpisah
`configureHeaders({ isFileUpload: true })`.

### Sekat file factory (urutan)

1. Konstanta `resource` (path dasar)
2. `getAll` (list paginate + filter) · varian versi baru (`getAllV2`) bila ada — jangan ubah signature lama
3. `getById` · 4. `create` · 5. `update` · 6. `delete`
7. `import(file)` / `downloadTemplate()` bila ada

Satu factory = satu resource. Resource baru → file factory baru + wiring di `api/index.ts`.
Endpoint versi baru (breaking change) → file `*-v2.ts` terpisah.

## 3. Data fetching — SWR

Tidak ada fetcher kedua: fungsi factory itu sendiri adalah fetcher SWR.

```tsx
"use client";
import useSWR, { mutate as globalMutate } from "swr";
import { useSearchParams } from "next/navigation";
import { ApiError, ResourceService } from "@/api";
import { handleToastPromise } from "@/lib/toast-response";
import { toast } from "sonner";

const KEY = "resource";

export function ItemTable() {
  const params = useSearchParams();
  const page = Number(params.get("page") ?? 1);
  const limit = Number(params.get("limit") ?? 10);
  const search = params.get("search") ?? "";
  const type = params.get("type") ?? "all";

  // Key = [nama-resource, ...param]. Semua param yang mengubah hasil HARUS ada di key.
  const { data, isLoading, error, mutate } = useSWR(
    [KEY, page, limit, search, type],
    () => ResourceService.getAll({ page, limit, search, type }),
  );

  const rows = data?.data ?? [];
  const pagination = data?.meta.pagination;

  // Segarkan SEMUA halaman/filter resource ini (create/delete menggeser pagination).
  const refreshAll = () => globalMutate((k) => Array.isArray(k) && k[0] === KEY);

  const onDelete = async (id: number) => {
    try {
      await handleToastPromise(ResourceService.delete(id), {
        loading: "Menghapus...", success: "Berhasil dihapus", error: "Gagal menghapus",
      });
      refreshAll();
    } catch {
      /* toast gagal sudah tampil dari handleToastPromise */
    }
  };

  // Dipakai dialog: kembalikan hasil supaya dialog tahu harus menutup atau menampilkan error field.
  const onCreate = async (payload: CreatePayload) => {
    try {
      const res = await ResourceService.create(payload);
      toast.success(res.message);
      refreshAll();
      return { ok: true as const };
    } catch (e) {
      if (e instanceof ApiError && e.status === 422) {
        return { ok: false as const, errors: e.errors as Record<string, string[]> };
      }
      toast.error(e instanceof ApiError ? e.message : "Terjadi kesalahan.");
      return { ok: false as const };
    }
  };

  if (isLoading) return <TableSkeleton />;
  if (error) return <ErrorState message={error.message} retry={() => mutate()} />;

  return <DataTable rows={rows} pagination={pagination} onDelete={onDelete} onCreate={onCreate} />;
}
```

### Sekat file table.tsx (urutan)

1. `"use client"` + import
2. Params — `useSearchParams`: `page`, `limit`, `search`, `type` (+ debounce search, reset page ke 1)
3. `useSWR([KEY, ...params], () => Service.getAll(...))`
4. Data turunan — `data?.data ?? []`, `data?.meta.pagination`. Jangan membentuk ulang response (urusan BE/Resource)
5. Handler CRUD — panggil service → toast → refresh
6. Guard — `isLoading` → skeleton, `error` → `ErrorState` (retry = `mutate()`), SEBELUM render utama
7. Render — tabel + pagination, tanpa fetch dan tanpa hitungan berat

`page.tsx` = wrapper saja, tanpa hook data. Dialog form/import → file terpisah.

### Aturan

- **`mutate` dari `useSWR` terikat ke key-nya**: argumen pertama adalah *data*. `mutate()` = revalidate
  halaman ini. Mengoper key ke sana menimpa cache dengan key itu. Untuk key lain / semua halaman
  pakai `mutate` global dengan matcher seperti di atas.
- Pagination + search lewat `useSearchParams` (state di URL, link bisa dibagikan).
- Search input WAJIB debounce ~300ms (`use-debounce`) + reset page ke 1 saat keyword berubah.
- Baca envelope: `data.data` (rows), `data.meta.pagination`.
- `error` SWR benar-benar terpicu untuk 4xx/5xx karena `request()` melempar `ApiError`.
- Download blob: `requestBlob` di handler, lalu `URL.createObjectURL(blob)` → klik `<a download>`.

## 4. Auth — HOC (bukan middleware)

**SHOULD** jika project memakai `withAuth`. Jangan mengganti ke middleware Next hanya karena
template ini; jangan juga memaksa HOC ke project yang sudah punya pola auth lain.

Alur: cek cookie token → pakai profile dari context bila ada → bila belum `getProfile()` → simpan ke
context → cek permission/role → redirect. Loading = spinner fullscreen; tak punya akses = `null`
(redirect jalan di effect).

```tsx
"use client";
import { ComponentType, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getCookie } from "cookies-next";
import { useProfile } from "@/context/profileContext";
import { AuthService } from "@/api";
import { TOKEN_COOKIE_KEY } from "@/lib/constant";

const withAuth = <P extends object>(
  WrappedComponent: ComponentType<P>,
  requiredPermission?: string,
  requiredRole?: string | string[],
) => {
  return function AuthenticatedComponent(props: P) {
    const router = useRouter();
    const { profile, setProfile } = useProfile();
    const [isLoading, setIsLoading] = useState(true);
    const [hasPermission, setHasPermission] = useState(false);

    useEffect(() => {
      const token = getCookie(TOKEN_COOKIE_KEY);
      if (!token) { router.replace("/login"); return; }

      const validate = (user: { permissions?: string[]; role?: string }) => {
        if (requiredPermission && !user.permissions?.includes(requiredPermission)) return false;
        if (requiredRole) {
          return Array.isArray(requiredRole)
            ? requiredRole.includes(user.role ?? "")
            : user.role === requiredRole;
        }
        return true;
      };

      if (profile) {
        const ok = validate(profile);
        setHasPermission(ok); setIsLoading(false);
        if (!ok) router.replace("/unauthorized");
        return;
      }

      (async () => {
        try {
          const response = await AuthService.getProfile();
          const user = response?.data?.user ?? null;
          if (!user) { router.replace("/login"); return; }
          setProfile(user);
          const ok = validate(user);
          setHasPermission(ok);
          if (!ok) { router.replace("/unauthorized"); return; }
          // Contoh aturan bisnis asal: data belum lengkap → /onboarding. Adaptasi ke project.
          if (user.needsOnboarding) { router.replace("/onboarding"); return; }
        } catch {
          router.replace("/login"); // 401 sudah ditangani request(); ini untuk error lain
        } finally {
          setIsLoading(false);
        }
      })();
    }, [router, requiredPermission, requiredRole, setProfile, profile]);

    if (isLoading) return <FullScreenSpinner />;
    if (!hasPermission) return null;
    return <WrappedComponent {...props} />;
  };
};
export default withAuth;
```

Pakai: `export default withAuth(DashboardPage, "permission-key", ["role-a", "admin"])`.
Bungkus layout/page subapps. Jangan bikin `middleware.ts` baru. Tanpa permission/role = cukup login.

Catatan:
- HOC hanya mengecek saat mount. Token yang kedaluwarsa di tengah sesi ditangani `request()` (401 → hapus cookie + `/login`).
- Token disimpan di cookie yang bisa dibaca JS (dibutuhkan `getTokenFromCookie`) — trade-off yang
  disengaja project asal (rentan XSS dibanding cookie httpOnly). Jangan "memperbaikinya" diam-diam; kalau mau
  diubah, diskusikan dulu karena menyentuh BE (Sanctum SPA) dan seluruh `api/index.ts`.

## 5. Types

`types/api.ts` (lihat `contract.md` §4) + `types/<domain>/*.ts` granular per fitur.

```ts
export interface Item {
  id: number;
  nama: string | null;
  group: { id: number; nama: string | null } | null;
}
export interface CreateItemPayload { nama: string; group_ids: number[]; is_active: boolean }
```

- Key mengikuti kontrak BE persis (`snake_case`). Project asal pernah duplikat `nama`/`name` — untuk kode baru ikuti BE.
- Ketik payload eksplisit; jangan `any`, jangan `eslint-disable no-explicit-any`.
- Props: `interface` + `ColumnDef<T>`. shadcn di `components/ui/`, komponen custom per fitur di satu lokasi (jangan sebar 2-3 folder).

## 6. Toast & konstanta

`lib/toast-response.ts`:

```ts
import { toast } from "sonner";
import { ApiError } from "@/api";

type ApiResponse = { success?: boolean; message: string };

// Untuk response yang SUKSES secara HTTP: tampilkan pesan dari envelope.
export const handleToastResponse = (response: ApiResponse, onClose?: () => void) => {
  if (response.success === false) toast.error(response.message);
  else { toast.success(response.message); onClose?.(); }
};

// Operasi async dengan loading → sukses/gagal. MENGEMBALIKAN promise aslinya
// (toast.promise tidak mengembalikan promise yang bisa di-await), jadi pemanggil
// bisa `await` lalu refresh, dan bisa menangkap kegagalan dengan try/catch.
export const handleToastPromise = <T,>(
  promise: Promise<T>,
  messages: { loading: string; success: string; error: string },
): Promise<T> => {
  toast.promise(promise, {
    loading: messages.loading,
    success: messages.success,
    error: (e) => (e instanceof ApiError ? e.message : messages.error),
  });
  return promise;
};
```

`lib/constant/index.ts`:

```ts
export const APP_NAME = process.env.NEXT_PUBLIC_APP_NAME || "My App";
export const API_URL = process.env.NEXT_PUBLIC_API_URL;
export const TOKEN_COOKIE_KEY = `${process.env.NEXT_PUBLIC_COOKIE_NAME}_token`;
// Daftar akses per subapp TERPUSAT di sini (single source of truth).
export const SUBAPP_ALLOWED_ROLES = ["super", "admin"] as const;
```

Aksi FE per status error: tabel di `contract.md` §5.
