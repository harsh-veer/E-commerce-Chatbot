"use client"

import { useEffect, useState } from "react"
import { getProducts, createProduct, updateProduct, deleteProduct } from "@/services/api"
import { Product } from "@/types"
import PageHeader from "@/components/PageHeader"
import { useAuth } from "@/context/AuthContext"

export default function AdminPage() {
  const { user } = useAuth()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [successMsg, setSuccessMsg] = useState("")

  // Form State
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    brand: "",
    category: "",
    price: 0,
    discount: 0,
    rating: 4.5,
    stock: 10,
    description: "",
    specificationsStr: "",
  })

  const loadCatalog = async () => {
    try {
      setLoading(true)
      const data = await getProducts()
      setProducts(data)
    } catch (err) {
      console.error("Failed to load products", err)
      setError("Failed to load product catalog.")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCatalog()
  }, [])

  const handleOpenAdd = () => {
    setEditingProduct(null)
    setFormData({
      name: "",
      brand: "",
      category: "Electronics",
      price: 29999,
      discount: 0,
      rating: 4.5,
      stock: 25,
      description: "",
      specificationsStr: "RAM: 16GB, Storage: 512GB SSD",
    })
    setIsFormOpen(true)
  }

  const handleOpenEdit = (product: Product) => {
    setEditingProduct(product)
    const specsStr = product.specifications
      ? Object.entries(product.specifications)
          .map(([k, v]) => `${k}: ${v}`)
          .join(", ")
      : ""
    setFormData({
      name: product.name || "",
      brand: product.brand || "",
      category: product.category || "",
      price: product.price || 0,
      discount: product.discount || 0,
      rating: product.rating || 4.5,
      stock: product.stock || 0,
      description: product.description || "",
      specificationsStr: specsStr,
    })
    setIsFormOpen(true)
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this product?")) return
    try {
      await deleteProduct(id)
      setSuccessMsg("Product deleted successfully.")
      loadCatalog()
    } catch (err) {
      console.error("Delete failed", err)
      setError("Failed to delete product. Ensure admin credentials.")
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setSuccessMsg("")

    // Parse specifications comma separated key:value
    const specs: Record<string, string> = {}
    if (formData.specificationsStr) {
      formData.specificationsStr.split(",").forEach((item) => {
        const [k, v] = item.split(":")
        if (k && v) {
          specs[k.trim()] = v.trim()
        }
      })
    }

    const payload: Partial<Product> = {
      name: formData.name,
      brand: formData.brand,
      category: formData.category,
      price: Number(formData.price),
      discount: Number(formData.discount),
      rating: Number(formData.rating),
      stock: Number(formData.stock),
      description: formData.description,
      specifications: specs,
      images: [],
    }

    try {
      if (editingProduct?.id) {
        await updateProduct(editingProduct.id, payload)
        setSuccessMsg("Product updated successfully!")
      } else {
        await createProduct(payload)
        setSuccessMsg("New product created and added to catalog!")
      }
      setIsFormOpen(false)
      loadCatalog()
    } catch (err) {
      console.error("Save product failed", err)
      setError("Could not save product. Verify admin token.")
    }
  }

  return (
    <main className="min-h-[calc(100vh-80px)] px-6 py-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <PageHeader
            title="Product Catalog Admin"
            description="Manage inventory items. Add, edit, or remove products indexed by the RAG vector engine."
          />
          <button
            onClick={handleOpenAdd}
            className="rounded-full bg-cyan-500 px-6 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-400 transition shadow-lg shadow-cyan-500/20"
          >
            + Add New Product
          </button>
        </div>

        {/* Feedback Banners */}
        {error ? (
          <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-4 text-xs text-rose-300">
            {error}
          </div>
        ) : null}
        {successMsg ? (
          <div className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-xs text-emerald-300">
            {successMsg}
          </div>
        ) : null}

        {/* Modal / Form Overlay */}
        {isFormOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm">
            <div className="glass-panel w-full max-w-2xl rounded-3xl p-8 space-y-6 max-h-[90vh] overflow-y-auto border border-cyan-500/30">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-bold text-white">
                  {editingProduct ? "Edit Product" : "Add New Product"}
                </h3>
                <button
                  onClick={() => setIsFormOpen(false)}
                  className="rounded-full p-2 text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  ✕
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Product Name</label>
                    <input
                      type="text"
                      required
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-sm text-slate-100 outline-none focus:border-cyan-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Brand</label>
                    <input
                      type="text"
                      required
                      value={formData.brand}
                      onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                      className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-sm text-slate-100 outline-none focus:border-cyan-400"
                    />
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Category</label>
                    <input
                      type="text"
                      required
                      value={formData.category}
                      onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                      className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-sm text-slate-100 outline-none focus:border-cyan-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Price (₹)</label>
                    <input
                      type="number"
                      step="1"
                      required
                      value={formData.price}
                      onChange={(e) => setFormData({ ...formData, price: Number(e.target.value) })}
                      className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-sm text-slate-100 outline-none focus:border-cyan-400"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1">Stock</label>
                    <input
                      type="number"
                      required
                      value={formData.stock}
                      onChange={(e) => setFormData({ ...formData, stock: Number(e.target.value) })}
                      className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-sm text-slate-100 outline-none focus:border-cyan-400"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">Description</label>
                  <textarea
                    rows={3}
                    required
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-sm text-slate-100 outline-none focus:border-cyan-400"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 mb-1">
                    Specifications (Comma Separated Key: Value)
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Battery: 12 Hours, Screen: 15.6 inch"
                    value={formData.specificationsStr}
                    onChange={(e) => setFormData({ ...formData, specificationsStr: e.target.value })}
                    className="w-full rounded-xl border border-slate-700 bg-slate-950 p-2.5 text-sm text-slate-100 outline-none focus:border-cyan-400"
                  />
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setIsFormOpen(false)}
                    className="rounded-full border border-slate-700 px-5 py-2 text-xs font-semibold text-slate-300 hover:bg-slate-800"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="rounded-full bg-cyan-500 px-6 py-2 text-xs font-semibold text-slate-950 hover:bg-cyan-400"
                  >
                    {editingProduct ? "Save Changes" : "Create Product"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Catalog Table */}
        <div className="glass-panel overflow-hidden rounded-3xl border border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-xs uppercase text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4 font-semibold">Product</th>
                  <th className="px-6 py-4 font-semibold">Category</th>
                  <th className="px-6 py-4 font-semibold">Price</th>
                  <th className="px-6 py-4 font-semibold">Stock</th>
                  <th className="px-6 py-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-xs text-slate-400">
                      Loading product data...
                    </td>
                  </tr>
                ) : products.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-12 text-center text-xs text-slate-400">
                      No products in database. Click 'Add New Product' to get started.
                    </td>
                  </tr>
                ) : (
                  products.map((p) => (
                    <tr key={p.id || p.name} className="hover:bg-slate-900/40 transition">
                      <td className="px-6 py-4">
                        <div className="font-semibold text-white">{p.name}</div>
                        <div className="text-xs text-cyan-400">{p.brand}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="rounded-md border border-slate-800 bg-slate-900 px-2.5 py-1 text-xs text-slate-300">
                          {p.category}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-semibold text-white">₹{p.price?.toLocaleString("en-IN")}</td>
                      <td className="px-6 py-4">
                        {p.stock > 0 ? (
                          <span className="text-xs text-emerald-400 font-medium">In Stock ({p.stock})</span>
                        ) : (
                          <span className="text-xs text-rose-400 font-medium">Out of Stock</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-right">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => handleOpenEdit(p)}
                            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-semibold text-slate-300 hover:border-cyan-400 hover:text-cyan-300"
                          >
                            Edit
                          </button>
                          <button
                            onClick={() => handleDelete(p.id)}
                            className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-1 text-xs font-semibold text-rose-400 hover:bg-rose-500 hover:text-slate-950"
                          >
                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </main>
  )
}
