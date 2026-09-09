import { ChangeEvent, FormEvent, useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api, errorMessage } from "../../api/client";
import {
  Button,
  Card,
  ErrorBox,
  Field,
  Input,
  SectionTitle,
  Spinner,
  TextArea,
} from "../../components/ui";
import IntelligencePanel from "../ai/IntelligencePanel";
import MarketPanel from "../ai/MarketPanel";
import CaptionsPanel from "../content/CaptionsPanel";
import ImageStudioPanel from "../content/ImageStudioPanel";
import VideoStudioPanel from "../content/VideoStudioPanel";
import { Product } from "../../types";

export default function ProductPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [product, setProduct] = useState<Product | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [attrKey, setAttrKey] = useState("");
  const [attrValue, setAttrValue] = useState("");

  const load = useCallback(async () => {
    try {
      const { data } = await api.get<Product>(`/products/${id}/`);
      setProduct(data);
    } catch (err) {
      setError(errorMessage(err));
    }
  }, [id]);

  useEffect(() => {
    void load();
  }, [load]);

  const removeProduct = async () => {
    if (!product) return;
    const confirmed = window.confirm(
      `«${product.name}» و همهٔ محتوای تولیدشده‌اش (تحلیل، پوستر، کپشن، سناریو و ویدیو) ` +
        "برای همیشه حذف می‌شوند. مطمئنید؟",
    );
    if (!confirmed) return;
    setBusy(true);
    setError(null);
    try {
      await api.delete(`/products/${id}/`);
      navigate(`/stores/${product.store}`);
    } catch (err) {
      setError(errorMessage(err));
      setBusy(false);
    }
  };

  const save = async (e: FormEvent) => {
    e.preventDefault();
    if (!product) return;
    setBusy(true);
    setError(null);
    try {
      await api.patch(`/products/${id}/`, {
        name: product.name,
        price: product.price,
        stock_quantity: product.stock_quantity,
        description: product.description,
        brand: product.brand,
      });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const uploadImage = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("image", file);
      await api.post(`/products/${id}/images/`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
      e.target.value = "";
    }
  };

  const deleteImage = async (imageId: number) => {
    setBusy(true);
    try {
      await api.delete(`/products/${id}/images/${imageId}/`);
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  const addAttribute = async (e: FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.post(`/products/${id}/attributes/`, { key: attrKey, value: attrValue });
      setAttrKey("");
      setAttrValue("");
      await load();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  };

  if (!product) {
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
          <Link to={`/stores/${product.store}`} className="text-sm text-violet-600 hover:underline">
            ← بازگشت به فروشگاه
          </Link>
          <h1 className="mt-1 text-2xl font-extrabold text-slate-800">{product.name}</h1>
        </div>
        {/* a product added by mistake stays in the catalog forever otherwise —
            and the sales agent keeps offering it to customers */}
        <Button variant="secondary" disabled={busy} onClick={() => void removeProduct()}>
          🗑 حذف محصول
        </Button>
      </div>
      <ErrorBox message={error} />

      <Card>
        <SectionTitle>مشخصات محصول</SectionTitle>
        <form onSubmit={save} className="grid gap-4 sm:grid-cols-3">
          <Field label="نام">
            <Input
              value={product.name}
              onChange={(e) => setProduct({ ...product, name: e.target.value })}
            />
          </Field>
          <Field label="قیمت (تومان)">
            <Input
              type="number"
              min="0"
              value={product.price}
              onChange={(e) => setProduct({ ...product, price: e.target.value })}
            />
          </Field>
          <Field label="موجودی">
            <Input
              type="number"
              min="0"
              value={product.stock_quantity}
              onChange={(e) =>
                setProduct({ ...product, stock_quantity: Number(e.target.value) || 0 })
              }
            />
          </Field>
          <Field label="برند">
            <Input
              value={product.brand}
              onChange={(e) => setProduct({ ...product, brand: e.target.value })}
            />
          </Field>
          <div className="sm:col-span-3">
            <Field label="توضیحات">
              <TextArea
                rows={3}
                value={product.description}
                onChange={(e) => setProduct({ ...product, description: e.target.value })}
              />
            </Field>
          </div>
          <div>
            <Button type="submit" disabled={busy}>
              ذخیره تغییرات
            </Button>
          </div>
        </form>
      </Card>

      <Card>
        <div className="mb-3 flex items-center justify-between">
          <SectionTitle>تصاویر محصول</SectionTitle>
          <label className="cursor-pointer rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-violet-700">
            + آپلود تصویر
            <input type="file" accept="image/*" className="hidden" onChange={uploadImage} />
          </label>
        </div>
        {product.images.length === 0 ? (
          <p className="text-sm text-slate-400">
            تصویری آپلود نشده — برای تحلیل بصری AI حداقل یک عکس اضافه کنید.
          </p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {product.images.map((img) => (
              <div key={img.id} className="relative">
                <img
                  src={img.image}
                  alt={img.alt_text || product.name}
                  className="h-28 w-28 rounded-lg border border-slate-200 object-cover"
                />
                <button
                  onClick={() => void deleteImage(img.id)}
                  className="absolute left-1 top-1 rounded-full bg-red-600 px-2 text-xs text-white hover:bg-red-700"
                  title="حذف"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>

      <Card>
        <SectionTitle>ویژگی‌ها</SectionTitle>
        {product.attributes.length > 0 && (
          <ul className="mb-4 space-y-1 text-sm text-slate-600">
            {product.attributes.map((attr) => (
              <li key={attr.id}>
                <span className="font-semibold">{attr.key}:</span> {attr.value}
              </li>
            ))}
          </ul>
        )}
        <form onSubmit={addAttribute} className="flex flex-wrap items-end gap-3">
          <div className="w-40">
            <Field label="عنوان">
              <Input value={attrKey} onChange={(e) => setAttrKey(e.target.value)} required />
            </Field>
          </div>
          <div className="w-56">
            <Field label="مقدار">
              <Input value={attrValue} onChange={(e) => setAttrValue(e.target.value)} required />
            </Field>
          </div>
          <Button type="submit" variant="secondary" disabled={busy}>
            افزودن
          </Button>
        </form>
      </Card>

      <IntelligencePanel productId={product.id} />

      <MarketPanel productId={product.id} />

      <ImageStudioPanel product={product} />

      <CaptionsPanel productId={product.id} />

      <VideoStudioPanel productId={product.id} />
    </div>
  );
}
