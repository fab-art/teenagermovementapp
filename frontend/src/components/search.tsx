"use client"

import * as React from "react"
import { Search as SearchIcon, Loader2, X } from "lucide-react"
import { Document } from "flexsearch"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import drugData from "@/data/drug_master.json"
import Link from "next/link"

interface Drug {
  id: string
  generic_name: string
  brand_name: string
  strength_form: string
  atc_code: string
  therapeutic_class: string
  rhia_covered: boolean
}

export function Search() {
  const [index, setIndex] = React.useState<any>(null)
  const [query, setQuery] = React.useState("")
  const [results, setResults] = React.useState<Drug[]>([])
  const [isSearching, setIsSearching] = React.useState(false)

  React.useEffect(() => {
    const idx = new Document({
      document: {
        id: "id",
        index: ["generic_name", "brand_name", "atc_code", "therapeutic_class"],
        store: true,
      },
      tokenize: "forward",
    })

    drugData.forEach((drug) => {
      idx.add(drug)
    })

    setIndex(idx)
  }, [])

  const handleSearch = (value: string) => {
    setQuery(value)
    if (!index || !value) {
      setResults([])
      return
    }

    setIsSearching(true)
    const searchResults = index.search(value, {
      enrich: true,
      suggest: true,
      limit: 10,
    })

    if (searchResults.length > 0) {
      const flattened: Drug[] = searchResults.flatMap((res: any) =>
        res.result.map((r: any) => r.doc)
      )
      // Deduplicate by ID
      const uniqueResults = Array.from(new Map(flattened.map((item: Drug) => [item.id, item])).values())
      setResults(uniqueResults.slice(0, 10))
    } else {
      setResults([])
    }
    setIsSearching(false)
  }

  const clearSearch = () => {
    setQuery("")
    setResults([])
  }

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
        <Input
          type="text"
          placeholder="Search 1,441 medicines (generic or brand)..."
          className="pl-10 pr-10 h-12 text-lg shadow-sm border-slate-200 focus:border-blue-400 transition-colors"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
        />
        {query && (
          <button
            onClick={clearSearch}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
          >
            <X className="h-5 w-5" />
          </button>
        )}
        {isSearching && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 animate-spin text-slate-400" />
        )}
      </div>

      {results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 z-50 space-y-2 bg-white/80 backdrop-blur-sm p-2 border rounded-xl shadow-xl max-h-[70vh] overflow-y-auto text-left">
          {results.map((drug) => (
            <Link key={drug.id} href={`/medicines/${drug.id}`} onClick={clearSearch}>
              <Card className="hover:bg-slate-50 cursor-pointer border-none shadow-none group">
                <CardContent className="p-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-slate-900 group-hover:text-blue-600 transition-colors">{drug.brand_name}</h3>
                      <p className="text-sm font-medium text-slate-600">{drug.generic_name}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[10px] font-mono bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded leading-none uppercase">
                          {drug.atc_code}
                        </span>
                        <span className="text-[10px] text-slate-400 border-l pl-2 leading-none">
                          {drug.therapeutic_class}
                        </span>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] bg-emerald-100 text-emerald-700 px-2 py-1 rounded-full font-bold uppercase tracking-wider shadow-sm">
                        RHIA
                      </span>
                      <p className="text-[10px] text-slate-400 mt-2 italic">{drug.strength_form}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {query && results.length === 0 && !isSearching && (
        <div className="absolute top-full left-0 right-0 mt-2 p-8 bg-white/95 backdrop-blur-sm border rounded-xl shadow-xl text-center text-slate-500 z-50">
          <p className="font-medium text-slate-800">No medicines found</p>
          <p className="text-sm text-slate-500 mt-1">Try searching by generic name, brand name, or ATC code.</p>
        </div>
      )}
    </div>
  )
}
