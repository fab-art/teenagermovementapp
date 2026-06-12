"use client"

import { useFavorites } from "@/lib/favorites"
import { Card, CardContent } from "@/components/ui/card"
import drugData from "@/data/drug_master.json"
import Link from "next/link"
import { Star, Pill } from "lucide-react"

export default function FavoritesPage() {
  const { favorites } = useFavorites()

  const favoriteDrugs = drugData.filter(d => favorites.includes(d.id))

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Favorites</h1>
        <p className="text-slate-500 mt-1">Quick access to your most frequently used medicines.</p>
      </div>

      {favoriteDrugs.length === 0 ? (
        <Card className="border-dashed border-2 bg-slate-50/50">
          <CardContent className="p-12 text-center space-y-4">
            <div className="mx-auto w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center">
              <Star className="h-6 w-6 text-slate-300" />
            </div>
            <div className="space-y-1">
              <p className="text-lg font-bold text-slate-900">No favorites yet</p>
              <p className="text-sm text-slate-500 max-w-xs mx-auto">
                Tap the "Add to Favorites" star on any medicine page to save it here.
              </p>
            </div>
            <Link href="/medicines" className="inline-block text-sm font-bold text-blue-600 hover:text-blue-700 uppercase tracking-wider pt-4">
              Browse Medicines
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {favoriteDrugs.map((drug) => (
            <Link key={drug.id} href={`/medicines/${drug.id}`}>
              <Card className="hover:shadow-md hover:border-blue-200 transition-all group">
                <CardContent className="p-4 flex items-center gap-4">
                   <div className="p-2 rounded-lg bg-blue-50 text-blue-600 border border-blue-100">
                    <Pill className="h-5 w-5" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-bold text-slate-900 truncate group-hover:text-blue-600">{drug.brand_name}</h3>
                    <p className="text-xs text-slate-500 truncate">{drug.generic_name}</p>
                  </div>
                  <Star className="h-5 w-5 text-amber-400 fill-amber-400" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
