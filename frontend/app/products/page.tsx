"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { getProducts } from "@/services/api"
import { Product } from "@/types"
import PageHeader from "@/components/PageHeader"

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")

  useEffect(() => {
    async function loadProducts() {
      try {
        setLoading(true)
        const data = await getProducts()
        setProducts(data)
      } catch (err) {
        console.error("Failed to load products", err)
        setError("Could not fetch product catalog. Ensure backend server is running.")
      } finally {
        setLoading(false)
      }
    }
    loadProducts()
  }, [])

  const categories = ["All", ...Array.from(new Set(products.map((p) => p.category).filter(Boolean)))]

  const filteredProducts = products.filter((p) => {
    const matchesSearch =
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.brand.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === "All" || p.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <main className="min-h-[calc(100vh-80px)] px-6 py-10">
      <div className="mx-auto max-w-7xl space-y-8">
        <PageHeader
          title="Product Catalog"
          description="Browse our inventory or click 'Ask AI' on any item for instant specs, compatibility, and availability answers."
        />

        {/* Filters Bar */}
        <div className="flex flex-col md:flex-row gap-4 justify-between items-center glass-panel p-4 rounded-2xl">
          {/* Search Input */}
          <div className="relative w-full md:w-80">
            <input
              type="text"
              placeholder="Search products by name, brand..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-2.5 pl-10 text-sm text-slate-100 placeholder-slate-500 outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400"
            />
            <span className="absolute left-3 top-3 text-slate-400 text-sm">🔍</span>
          </div>

          {/* Category Filter Chips */}
          <div className="flex flex-wrap gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`rounded-full px-4 py-2 text-xs font-semibold transition ${
                  selectedCategory === cat
                    ? "bg-cyan-500 text-slate-950 shadow-md shadow-cyan-500/20"
                    : "border border-slate-800 bg-slate-900 text-slate-300 hover:border-slate-700 hover:text-white"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Loading / Error States */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-cyan-500 border-t-transparent" />
            <p className="text-sm text-slate-400">Loading catalog from database...</p>
          </div>
        ) : error ? (
          <div className="rounded-2xl border border-rose-500/30 bg-rose-500/10 p-6 text-center text-rose-300">
            <p className="font-semibold">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 rounded-full bg-rose-500 px-5 py-2 text-xs font-semibold text-slate-950 hover:bg-rose-400"
            >
              Retry
            </button>
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-12 text-center text-slate-400">
            <p className="text-2xl">📦</p>
            <p className="mt-2 font-semibold text-slate-200">No products found</p>
            <p className="text-xs text-slate-400 mt-1">Try adjusting your search criteria or category filter.</p>
          </div>
        ) : (
          /* Products Grid */
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredProducts.map((product) => (
              <div key={product.id || product.name} className="glass-card rounded-3xl p-6 flex flex-col justify-between space-y-4 group">
                <div className="space-y-3">
                  {/* Top Meta Bar */}
                  <div className="flex items-center justify-between">
                    <span className="rounded-md border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-0.5 text-[11px] font-semibold text-cyan-400">
                      {product.brand || product.category}
                    </span>
                    <span className="flex items-center gap-1 text-xs font-semibold text-amber-400">
                      ★ {product.rating || "4.8"}
                    </span>
                  </div>

                  {/* Product Title */}
                  <h3 className="text-xl font-bold text-white group-hover:text-cyan-300 transition-colors">
                    {product.name}
                  </h3>

                  {/* Description */}
                  <p className="text-xs text-slate-300 line-clamp-3 leading-relaxed">
                    {product.description}
                  </p>

                  {/* Key Specifications Badges */}
                  {product.specifications && Object.keys(product.specifications).length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {Object.entries(product.specifications).slice(0, 3).map(([key, val]) => (
                        <span key={key} className="rounded-lg bg-slate-900 border border-slate-800 px-2 py-1 text-[10px] text-slate-400">
                          <strong className="text-slate-300">{key}:</strong> {val}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Price & Action Button */}
                <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
                  <div>
                    <span className="text-2xl font-extrabold text-white">₹{product.price.toLocaleString("en-IN")}</span>
                    {product.stock > 0 ? (
                      <span className="block text-[10px] text-emerald-400 font-medium">In Stock ({product.stock})</span>
                    ) : (
                      <span className="block text-[10px] text-rose-400 font-medium">Out of Stock</span>
                    )}
                  </div>

                  <Link
                    href={`/chat?q=${encodeURIComponent(`What are the key specs, availability, and features of ${product.name}?`)}`}
                    className="inline-flex items-center gap-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 px-4 py-2 text-xs font-semibold text-cyan-300 hover:bg-cyan-500 hover:text-slate-950 transition-all shadow-sm"
                  >
                    <span>Ask AI</span>
                    <span>💬</span>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}
