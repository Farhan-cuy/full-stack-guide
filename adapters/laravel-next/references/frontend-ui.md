# Frontend — UI pattern (dialog, kolom, layout, tour, styling)

> Konteks: ini panduan dialect Laravel API + Next.js App Router. Kata WAJIB / SELALU / "tanpa pengecualian" di file ini berarti *default adapter* bila repository memakai pola tersebut. Kontrol keamanan, integritas data, kontrak publik, dan instruksi user mengikuti Core (`../../../references/`) bila berbeda.


Muat file ini bila tugasnya membuat dialog form, kolom tabel, layout/sidebar, tour onboarding, atau styling.
Dasar (page, api, SWR, auth, toast) ada di `frontend.md`.

## Isi

- [A. DialogPopUp — form add/edit](#a-dialogpopup--form-addedit)
- [B. ColumnDef factory](#b-columndef-factory)
- [C. Layout subapp — sidebar per-role](#c-layout-subapp--sidebar-per-role)
- [D. Tour — driver.js](#d-tour--driverjs)
- [E. Styling & env](#e-styling--env)

## A. DialogPopUp — form add/edit

Satu file, zod schema di file yang sama, panggilan API di PARENT (bukan di dialog). Dialog tahu
hasil submit dari nilai kembalian `onSubmit`, sehingga bisa menutup saat sukses dan menampilkan
error per field saat 422 — tanpa kehilangan input user.

`lib/form-errors.ts`:

```ts
import type { FieldValues, Path, UseFormReturn } from "react-hook-form";

// Petakan { field: [pesan] } dari 422 BE ke RHF. Field yang tak ada di form diabaikan RHF.
export const applyServerErrors = <T extends FieldValues>(
  form: UseFormReturn<T>,
  errors: Record<string, string[]>,
) => {
  Object.entries(errors).forEach(([field, messages]) => {
    form.setError(field as Path<T>, { type: "server", message: messages[0] });
  });
};
```

Dialog:

```tsx
"use client";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { PlusCircle } from "lucide-react";
import { applyServerErrors } from "@/lib/form-errors";

// 1. Schema + type DI FILE INI. Nama type bukan `FormData` (menimpa FormData bawaan browser).
//    zod v3: { required_error: "..." } · zod v4: { error: "..." } — cek versi di package.json.
const formSchema = z.object({
  nama: z.string().min(3, "Nama minimal 3 karakter"),
  status: z.enum(["Aktif", "Nonaktif"], { required_error: "Pilih status" }),
});
type FormValues = z.infer<typeof formSchema>;

type SubmitResult = { ok: true } | { ok: false; errors?: Record<string, string[]> };

// 2. Props standar
interface DialogPopUpProps {
  mode?: "add" | "edit";
  initialData?: Item | null;                          // null kalau mode add
  onSubmit: (data: FormValues) => Promise<SubmitResult>;  // API call + toast di PARENT
  trigger?: React.ReactNode;
  open?: boolean;                                     // opsional: kontrol dari luar
  onOpenChange?: (open: boolean) => void;
}

const DialogPopUp = ({ mode = "add", initialData, onSubmit, trigger, open: extOpen, onOpenChange: extOnOpenChange }: DialogPopUpProps) => {
  const [internalOpen, setInternalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const open = extOpen ?? internalOpen;
  const setOpen = extOnOpenChange ?? setInternalOpen;
  const isEditMode = mode === "edit";

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { nama: "", status: undefined },
  });

  // Reset tiap open/mode/initialData berubah — tanpa ini data edit bocor ke mode add.
  useEffect(() => {
    if (!open) return;
    if (initialData && isEditMode) form.reset({ nama: initialData.nama ?? "", status: initialData.status });
    else form.reset({ nama: "", status: undefined });
  }, [open, initialData, isEditMode, form]);

  const handleSubmit = async (values: FormValues) => {
    setIsSubmitting(true);
    try {
      const result = await onSubmit(values);
      if (result.ok) setOpen(false);                       // tutup HANYA saat sukses
      else if (result.errors) applyServerErrors(form, result.errors); // 422 → error per field, dialog tetap terbuka
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {trigger ?? <Button size="sm"><PlusCircle className="mr-2 h-4 w-4" />Tambah</Button>}
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditMode ? "Edit" : "Tambah"} Item</DialogTitle>
        </DialogHeader>
        {/* <form onSubmit={form.handleSubmit(handleSubmit)}> field RHF; tombol submit disabled={isSubmitting} */}
      </DialogContent>
    </Dialog>
  );
};
export default DialogPopUp;
```

Aturan:
- Schema zod + `z.infer` DI FILE dialog — jangan import dari tempat lain.
- `onSubmit` = callback parent yang mengembalikan `SubmitResult` (contoh `onCreate` di `frontend.md` §3). Dialog tidak memanggil service langsung.
- Dialog hanya menutup bila `result.ok`. Jangan `setOpen(false)` tanpa melihat hasil.
- `isSubmitting` menonaktifkan tombol submit.
- Daftar dinamis (misi, syarat) → `useFieldArray`.

## B. ColumnDef factory

Kolom tabel = factory function yang menerima `currentPage`, `perPage`, `onEdit?`:

```tsx
"use client";
import { ColumnDef } from "@tanstack/react-table";
import { Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Item } from "@/types/item/item";

export const Columns = (
  currentPage: number,
  perPage: number,
  onEdit?: (row: Item) => void,
): ColumnDef<Item>[] => [
  {
    id: "no",
    header: () => <div className="text-center w-full">No</div>,
    size: 60,
    cell: ({ row }) => (
      <div className="text-center w-full">{(currentPage - 1) * perPage + row.index + 1}</div>
    ),
  },
  { accessorKey: "nama", header: "Nama", size: 140 },
  {
    id: "group",
    header: "Grup",
    size: 150,
    cell: ({ row }) => <div className="truncate">{row.original.group?.nama ?? "-"}</div>, // fallback "-" untuk null
  },
  {
    id: "actions",
    header: () => <div className="text-center w-full">Aksi</div>,
    size: 80,
    enableHiding: false,
    cell: ({ row }) => (
      <div className="flex justify-center">
        <Button variant="ghost" size="icon" onClick={() => onEdit?.(row.original)}>
          <Pencil className="h-4 w-4" />
        </Button>
      </div>
    ),
  },
];
```

Aturan:
- Kolom aksi inline ke DialogPopUp edit — jangan buat file aksi terpisah kecuali sangat kompleks.
- Kolom detail biasanya `Link` ke `/domain/detail/{id}` (ikon `Eye` + hover bg).
- Badge: helper lokal `getXxxBadgeVariant(value)` → `"success" | "destructiveOutline" | ...`.
- Tanggal: `formatDate/formatDateTime/formatDateFull` dari `lib/utils`, fallback `"-"`.
- Sel HTML (editor Tiptap): `dangerouslySetInnerHTML` + `sanitizeHtml` dari `lib/sanitize-html`; tidak pernah tanpa sanitasi.
- Hindari cast `as object | string` pada `row.getValue`; ketik kolom dari type `Item`.

## C. Layout subapp — sidebar per-role

Tiap subapp punya `layout.tsx` sendiri:

```tsx
"use client";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { SidebarMenuContent } from "@/components/sidebar-menu-content";
import { useProfile } from "@/context/profileUseContext";
import withAuth from "@/hoc/withAuth";

// 1. Sidebar data: Record<role, items[]> — tiap role punya menu berbeda
const sidebarData = {
  staff: [
    { name: "Dashboard", url: "/domain", icon: Home },
    {
      name: "Dropdown", url: "#", icon: MonitorCheck,
      subItems: [{ name: "Opsi A", url: "/domain/a" }, { name: "Opsi B", url: "/domain/b" }],
    },
  ],
  admin: [{ name: "Dashboard", url: "/domain", icon: Home }],
};

function Layout({ children }: { children: React.ReactNode }) {
  const { profile, activeTenantId } = useProfile();
  const role = profile?.roles as Role;
  const activeRole = role === "super" ? "admin" : role; // super memakai menu admin
  const items = sidebarData[activeRole as keyof typeof sidebarData] ?? [];

  return (
    <SidebarProvider>
      <AppSidebar sidebarContent={<SidebarMenuContent items={items} />} />
      {/* key = paksa remount saat ganti tenant → state basi tidak terbawa */}
      <main key={activeTenantId ?? "default"} className="...">{children}</main>
    </SidebarProvider>
  );
}

// 2. Wrap HOC auth — permission string = nama subapp di BE
export default withAuth(Layout, "domain-name");
```

Aturan:
- `sidebarData` berupa `Record` per role, bukan conditional di JSX.
- `key={activeTenantId}` di `<main>` untuk force remount saat ganti tenant (satu sumber tenant: context).
- `withAuth(Layout, "permission")` — permission = nama subapp di BE.
- Pengumuman/notifikasi global di layout, bukan di page.
- Mapping role → menu didefinisikan di sini, bukan tersebar.

## D. Tour — driver.js

**MAY.** Hanya jika saudara terdekat sudah memakai tour, atau user minta onboarding. Jangan pasang
`driver.js` di resource baru “supaya lengkap”.

1. Tambah `data-tour="nama-unik"` di target (sidebar item, card, dialog, button).
2. Buat `<XxxTourButton />` di `_components/` yang memakai `driver.js` dengan array step.
3. Auto-buka sidebar (mobile/desktop) bila step pertama menargetkan sidebar.

```tsx
const steps = [
  { element: '[data-tour="sidebar-menu"]', popover: { title: "Sidebar", description: "Navigasi utama" } },
  { element: '[data-tour="card-kpi"]', popover: { title: "KPI", description: "Ringkasan data" } },
];
// driver({ steps }).drive();   // sesuaikan dengan versi driver.js di package.json
```

Penamaan `data-tour`: `sidebar-{subapp}-{nama}` / `card-{nama}` — lowercase-dash, konsisten.

## E. Styling & env

Tailwind utility-first + variabel CSS di `app/globals.css`. Varian warna per tenant lewat CSS vars
(contoh asal: `--tenant-primary`). Env: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_COOKIE_NAME`,
`NEXT_PUBLIC_APP_NAME`, plus URL layanan lain bila ada — baca dari env, jangan hardcode.

## F. Product UI — jangan AI slop

Skill `design-taste-frontend` / landing-page taste **jangan** dipakai di tabel, dialog, sidebar,
dashboard. Di sini yang menang = halaman saudara + token yang sudah ada.

- Pakai komponen `components/ui/*` dan pola spacing/typography halaman yang ditiru. Jangan palet,
  font, radius, shadow, atau `globals.css` baru.
- Jangan gradient ungu, glass, mesh, kartu KPI hias, ilustrasi empty-state, badge “New”, copy
  Inggris generik (“Welcome back”, “Let’s get started”, “Unlock insights”).
- Satu aksi primer per layar. Copy sentence-case, nama tombol = kerjaan user (“Simpan”, “Hapus”).
- Density ikut app (tabel admin = rapat). Jangan ubah jadi “airy marketing layout”.
- Motion: tidak ada; atau yang sudah dipakai (toast, dialog). Jangan stagger fade tiap row.
- Kalau brief UI ambigu: tanya **satu** pertanyaan, atau tiru saudara. Jangan menebak look baru.

Untuk layar baru, copy, state (loading/kosong/error), dan aksesibilitas, lihat juga Core: `../../../references/frontend-design-quality.md`. Design system dan komponen yang sudah ada di repo tetap menjadi acuan utama.
