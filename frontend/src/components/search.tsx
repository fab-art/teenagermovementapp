"use client"

import * as React from "react"
import { Search as SearchIcon, Loader2 } from "lucide-react"
import { Document } from "flexsearch"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import drugData from "@/data/drug_master.json"

interface Drug {
  id: string
  generic_name: string
  atc_code: string
  therapeutic_class: string
  description: string
  indications: string
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
        index: ["generic_name", "atc_code", "therapeutic_class", "indications"],
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
    })

    if (searchResults.length > 0) {
      // Flatten FlexSearch results
      const flattened = searchResults.flatMap((res: any) =>
        res.result.map((r: any) => r.doc)
      )
      // Deduplicate
      const uniqueResults = Array.from(new Set(flattened.map((d: any) => d.id)))
        .map(id => flattened.find((d: any) => d.id === id))

      setResults(uniqueResults)
    } else {
      setResults([])
    }
    setIsSearching(false)
  }

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
        <Input
          type="search"
          placeholder="Search by generic name, ATC code, or therapeutic class..."
          className="pl-10 h-12 text-lg shadow-sm"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
        />
        {isSearching && (
          <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 animate-spin text-slate-400" />
        )}
      </div>

      {results.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 z-20 space-y-2">
          {results.map((drug) => (
            <Card key={drug.id} className="hover:bg-slate-50 cursor-pointer">
              <CardContent className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-slate-900">{drug.generic_name}</h3>
                    <p className="text-sm text-slate-500">{drug.therapeutic_class} • {drug.atc_code}</p>
                  </div>
                  {drug.rhia_covered && (
                    <span className="text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-medium">RHIA</span>
                  )}
                </div>
                <p className="text-sm text-slate-600 mt-1 line-clamp-1">{drug.indications}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {query && results.length === 0 && !isSearching && (
        <div className="absolute top-full left-0 right-0 mt-2 p-8 bg-white border rounded-lg shadow-lg text-center text-slate-500">
          No medicines found matching &quot;{query}&quot;
        </div>
      )}
    </div>
  )
}
