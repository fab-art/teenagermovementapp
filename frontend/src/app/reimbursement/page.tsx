"use client"

import { useState, useMemo } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import drugData from "@/data/drug_master.json"
import { CheckCircle2, CreditCard } from "lucide-react"

const ITEMS_PER_PAGE = 30

export default function ReimbursementPage() {
  const [displayCount, setDisplayCount] = useState(ITEMS_PER_PAGE)

  const reimbursableDrugs = useMemo(() => {
    return drugData.filter(d => d.rhia_covered)
  }, [])

  const displayedDrugs = reimbursableDrugs.slice(0, displayCount)
  const hasMore = displayCount < reimbursableDrugs.length

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex items-center gap-4">
        <div className="p-3 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-100">
          <CreditCard className="h-8 w-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold text-slate-900">RHIA Reimbursement</h1>
          <p className="text-slate-500 mt-1">Search medicines covered under the Rwanda Health Insurance Authority.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {displayedDrugs.map((drug) => (
          <Card key={drug.id} className="border-l-4 border-l-emerald-500">
            <CardContent className="p-4 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-slate-900">{drug.brand_name}</h3>
                <p className="text-sm text-slate-600">{drug.generic_name}</p>
                <p className="text-xs text-slate-400 mt-1 uppercase">{drug.atc_code}</p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-emerald-50 text-emerald-700 text-[10px] font-bold">
                  <CheckCircle2 className="h-3 w-3" />
                  COVERED
                </span>
                <p className="text-[10px] text-slate-400 italic">{drug.strength_form}</p>
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
            className="px-8 font-bold border-emerald-200 text-emerald-600 hover:bg-emerald-50"
          >
            Load More Coverages ({reimbursableDrugs.length - displayCount} remaining)
          </Button>
        </div>
      )}
    </div>
  )
}
