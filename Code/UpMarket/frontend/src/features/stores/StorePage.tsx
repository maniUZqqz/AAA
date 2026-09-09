import { FormEvent, useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api, errorMessage, fetchAllPages } from "../../api/client";
import {
  Button,
  Card,
  EmptyState,
  ErrorBox,
  Field,
  Input,
  SectionTitle,
  Spinner,
  TextArea,
} from "../../components/ui";
import { Product, Store, StoreProfile } from "../../types";

export default function StorePage() {
  const { id } = useParams<{ id: string }>();
  const [store, setStore] = useState<Store | null>(null);
  const [profile, setProfile] = useState<StoreProfile | null>(null);
  const [products, setProducts] = useState<Product[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // product form
  const [productName, setProductName] = useState("");
  const [price, setPrice] = useState("");
  const [stock, setStock] = useState("0");
  const [productDescription, setProductDescription] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [storeRes, profileRes, productList] = await Promise.all([
        api.get<Store>(`/stores/${id}/`),
        api.get<StoreProfile>(`/stores/${id}/profile/`),
        fetchAllPages<Product>(`/products/?store=${id}`),
      ]);
      setStore(storeRes.data);
      setProfile(profileRes.data);
      setProducts(productList);
    } catch (err) {
      setError(errorMessage(err));
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  const saveProfile = async (e: FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setBusy(true);
    setError(null);
    setNotice(null);
    try {
      await api.patch(`/stores/${id}/profile/`, {
        brand_voice: profile.brand_voice,
        tone: profile.tone,
        shipping_policy: profile.shipping_policy,
        return_policy: profile.return_policy,
        payment_info: profile.payment_info,
      });
      setNotice("پروفایل برند ذخیره شد ✅");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const createProduct = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await api.post("/products/", {
        store: Number(id),
        name: productName,
        price: price || "0",
        stock_quantity: Number(stock) || 0,
        description: productDescription,
      });
      setProductName("");
      setPrice("");
      setStock("0");
      setProductDescription("");
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  if (!store || !profile) {
    return (
      <div className="py-10 text-center">
        {error ? <ErrorBox message={error} /> : <Spinner />}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <Link to="/" className="text-sm text-violet-600 hover:underline">
            ← بازگشت به داشبورد
          </Link>
          <h1 className="mt-1 text-2xl font-extrabold text-slate-800">{store.name}</h1>
          {store.business_type && <p className="text-sm text-violet-600">{store.business_type}</p>}
        </div>
        <div className="flex gap-2">
          <Link
            to={`/stores/${store.id}/sales`}
            className="rounded-lg bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-800 transition hover:bg-slate-300"
          >
            💰 فروش و پشتیبانی
          </Link>
          <Link
            to={`/stores/${store.id}/analytics`}
            className="rounded-lg bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-800 transition hover:bg-slate-300"
          >
            📈 آمار
          </Link>
          <Link
            to={`/stores/${store.id}/campaigns`}
            className="rounded-lg bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-800 transition hover:bg-slate-300"
          >
            📣 کمپین‌ها
          </Link>
          <Link
            to={`/stores/${store.id}/chat`}
            className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-violet-700"
          >
            💬 چت فروش (آزمایشی)
          </Link>
        </div>
      </div>
      <ErrorBox message={error} />
      {notice && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-2 text-sm text-green-700">
          {notice}
        </div>
      )}

      <Card>
        <SectionTitle>پروفایل برند</SectionTitle>
        <form onSubmit={saveProfile} className="grid gap-4 sm:grid-cols-2">
          <Field label="لحن برند">
            <Input
              value={profile.tone}
              onChange={(e) => setProfile({ ...profile, tone: e.target.value })}
              placeholder="مثلاً صمیمی، رسمی، لوکس…"
            />
          </Field>
          <Field label="صدای برند">
            <Input
              value={profile.brand_voice}
              onChange={(e) => setProfile({ ...profile, brand_voice: e.target.value })}
            />
          </Field>
          <Field label="قوانین ارسال">
            <TextArea
              rows={2}
              value={profile.shipping_policy}
              onChange={(e) => setProfile({ ...profile, shipping_policy: e.target.value })}
            />
          </Field>
          <Field label="قوانین مرجوعی">
            <TextArea
              rows={2}
              value={profile.return_policy}
              onChange={(e) => setProfile({ ...profile, return_policy: e.target.value })}
            />
          </Field>
          <div className="sm:col-span-2">
            <Field label="اطلاعات پرداخت (شماره کارت/شبا — ایجنت فروش عیناً همین را به مشتری می‌دهد)">
              <TextArea
                rows={2}
                value={profile.payment_info}
                onChange={(e) => setProfile({ ...profile, payment_info: e.target.value })}
                placeholder="مثلاً: کارت 6037-99XX-XXXX-1234 بانک ملی به نام ... — بعد از واریز، رسید را در چت بفرستید."
              />
            </Field>
          </div>
          <div>
            <Button type="submit" disabled={busy}>
              ذخیره پروفایل
            </Button>
          </div>
        </form>
      </Card>

      <Card>
        <SectionTitle>افزودن محصول</SectionTitle>
        <form onSubmit={createProduct} className="grid gap-4 sm:grid-cols-3">
          <Field label="نام محصول *">
            <Input value={productName} onChange={(e) => setProductName(e.target.value)} required />
          </Field>
          <Field label="قیمت (تومان)">
            <Input
              type="number"
              min="0"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
            />
          </Field>
          <Field label="موجودی">
            <Input type="number" min="0" value={stock} onChange={(e) => setStock(e.target.value)} />
          </Field>
          <div className="sm:col-span-3">
            <Field label="توضیحات">
              <TextArea
                rows={2}
                value={productDescription}
                onChange={(e) => setProductDescription(e.target.value)}
              />
            </Field>
          </div>
          <div>
            <Button type="submit" disabled={busy}>
              افزودن محصول
            </Button>
          </div>
        </form>
      </Card>

      <div>
        <SectionTitle>محصولات ({products?.length ?? 0})</SectionTitle>
        {products === null ? (
          <Spinner />
        ) : products.length === 0 ? (
          <EmptyState>هنوز محصولی ثبت نشده است.</EmptyState>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((product) => (
              <Link key={product.id} to={`/products/${product.id}`}>
                <Card className="transition hover:border-violet-300 hover:shadow-md">
                  {product.images.length > 0 && (
                    <img
                      src={product.images[0].image}
                      alt={product.name}
                      className="mb-3 h-32 w-full rounded-lg object-cover"
                    />
                  )}
                  <h3 className="font-bold text-slate-800">{product.name}</h3>
                  <p className="mt-1 text-sm text-violet-700">
                    {Number(product.price).toLocaleString("fa-IR")} تومان
                  </p>
                  <p className="mt-1 text-xs text-slate-400">موجودی: {product.stock_quantity}</p>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
