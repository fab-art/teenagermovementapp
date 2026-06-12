"use client"

import { useState, useMemo } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import drugData from "@/data/drug_master.json"
import Link from "next/link"

const ITEMS_PER_PAGE = 30

export default function MedicinesPage() {
  const [displayCount, setDisplayCount] = useState(ITEMS_PER_PAGE)

  // Get unique generic names
  const uniqueGenerics = useMemo(() => {
    return Array.from(new Set(drugData.map(d => d.generic_name))).sort()
  }, [])

  const displayedGenerics = uniqueGenerics.slice(0, displayCount)
  const hasMore = displayCount < uniqueGenerics.length

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Medicines</h1>
        <p className="text-slate-500 mt-1">Browse all {uniqueGenerics.length} generic drugs in the formulary.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {displayedGenerics.map((generic) => {
          const firstDrug = drugData.find(d => d.generic_name === generic)
          if (!firstDrug) return null;
          return (
            <Link key={generic} href={`/medicines/${firstDrug.id}`}>
              <Card className="hover:shadow-md hover:border-blue-200 transition-all group">
                <CardContent className="p-4">
                  <h3 className="font-semibold text-slate-900 leading-tight group-hover:text-blue-600 transition-colors">{generic}</h3>
                  <p className="text-[10px] text-slate-500 mt-2 uppercase tracking-widest font-mono">
                    {firstDrug.atc_code} • {firstDrug.therapeutic_class}
                  </p>
                </CardContent>
              </Card>
            </Link>
          )
        })}
      </div>

      {hasMore && (
        <div className="flex justify-center pt-8 pb-12">
          <Button
            onClick={() => setDisplayCount(prev => prev + ITEMS_PER_PAGE)}
            variant="outline"
            className="px-8 font-bold border-blue-200 text-blue-600 hover:bg-blue-50"
          >
            Load More Medicines ({uniqueGenerics.length - displayCount} remaining)
          </Button>
        </div>
      )}
    </div>
  )
}
