"use client"

import { useState } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import drugData from "@/data/drug_master.json"
import { ClipboardList, ExternalLink } from "lucide-react"

const ITEMS_PER_PAGE = 30

export default function ProductRegistryPage() {
  const [displayCount, setDisplayCount] = useState(ITEMS_PER_PAGE)

  const displayedDrugs = drugData.slice(0, displayCount)
  const hasMore = displayCount < drugData.length

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-purple-50 text-purple-600 border border-purple-100">
          <ClipboardList className="h-8 w-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Product Registry</h1>
          <p className="text-slate-500 mt-1">Rwanda FDA Authorized Medicines and Marketing Authorizations.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {displayedDrugs.map((drug) => (
          <Card key={drug.id} className="hover:border-purple-200 transition-colors group">
            <CardContent className="p-5 flex justify-between items-center">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-slate-900 group-hover:text-purple-600 transition-colors text-lg">
                    {drug.brand_name}
                  </h3>
                  <span className="text-[10px] font-mono bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded uppercase">
                    {drug.atc_code}
                  </span>
                </div>
                <p className="text-sm font-medium text-slate-600 uppercase tracking-tight">{drug.generic_name}</p>
                <p className="text-xs text-slate-400 italic">{drug.strength_form}</p>
              </div>
              <div className="text-right space-y-2">
                <div className="px-3 py-1 rounded-lg bg-slate-50 border border-slate-100 text-[10px] font-bold text-slate-600">
                  REG: RW-FDA-{drug.atc_code}-{drug.id.split('-').pop()}
                </div>
                <button className="inline-flex items-center gap-1.5 text-xs font-bold text-purple-600 hover:text-purple-700 uppercase tracking-wider">
                  View Certificate
                  <ExternalLink className="h-3 w-3" />
                </button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center pt-8 pb-12">
          <Button
            onClick={() => setDisplayCount(prev => prev + ITEMS_PER_PAGE)}
            variant="outline"
            className="px-8 font-bold border-purple-200 text-purple-600 hover:bg-purple-50"
          >
            Load More Products ({drugData.length - displayCount} remaining)
          </Button>
        </div>
      )}
    </div>
  )
}
