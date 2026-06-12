import drugData from "@/data/drug_master.json"
import guidelinesData from "@/data/guidelines.json"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Info, AlertCircle, Microscope, ChevronRight } from "lucide-react"
import Link from "next/link"
import { notFound } from "next/navigation"
import { FavoriteButton } from "@/components/favorite-button"

export async function generateStaticParams() {
  return drugData.map((drug) => ({
    id: drug.id,
  }))
}

export default async function MedicineDetailPage({ params }: { params: { id: string } }) {
  const { id } = await params
  const drug = drugData.find(d => d.id === id)

  if (!drug) notFound()

  const guideline = guidelinesData.find(g => g.atc_code === drug.atc_code || drug.atc_code.startsWith(g.atc_code))

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-20">
      <nav className="flex items-center gap-2 text-sm text-slate-500 mb-6">
        <Link href="/medicines" className="hover:text-blue-600">Medicines</Link>
        <ChevronRight className="h-4 w-4" />
        <span className="truncate max-w-[200px]">{drug.generic_name}</span>
      </nav>

      <div className="space-y-4">
        <div className="flex justify-between items-start gap-4">
          <div>
            <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">{drug.brand_name}</h1>
            <p className="text-xl font-medium text-slate-600 mt-2 uppercase">{drug.generic_name}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            {drug.rhia_covered && (
              <span className="px-3 py-1 rounded-full bg-emerald-100 text-emerald-700 text-xs font-bold uppercase tracking-widest shadow-sm">
                RHIA Covered
              </span>
            )}
            <span className="font-mono text-sm bg-slate-100 px-2 py-1 rounded text-slate-500 uppercase tracking-widest">
              {drug.atc_code}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-blue-700">
              <Info className="h-5 w-5" />
              Product Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Strength & Formulation</h4>
              <p className="text-lg text-slate-800 font-medium">{drug.strength_form}</p>
            </div>
            <div>
              <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Therapeutic Class</h4>
              <p className="text-lg text-slate-800 font-medium">{drug.therapeutic_class}</p>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-50 border-slate-200">
          <CardHeader>
            <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wider">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <FavoriteButton id={drug.id} />
            <button className="w-full py-3 px-4 rounded-xl bg-white border border-slate-200 text-slate-700 font-bold text-sm hover:bg-slate-50 transition-colors shadow-sm text-center">
              Share Monograph
            </button>
            <button className="w-full py-3 px-4 rounded-xl bg-blue-600 text-white font-bold text-sm hover:bg-blue-700 transition-colors shadow-sm text-center">
              Check Inventory
            </button>
          </CardContent>
        </Card>
      </div>

      {guideline && (
        <section className="space-y-6">
          <h2 className="text-2xl font-bold text-slate-900 border-b pb-4">Clinical Guidance</h2>

          <div className="space-y-6">
            {guideline.pathophysiology && (
              <div className="flex gap-4">
                <div className="mt-1 p-2 rounded-lg bg-blue-50 text-blue-600 shrink-0 h-fit">
                  <Microscope className="h-5 w-5" />
                </div>
                <div className="space-y-2">
                  <h3 className="font-bold text-slate-800 uppercase tracking-tight text-sm">Pathophysiology</h3>
                  <p className="text-slate-600 leading-relaxed">{guideline.pathophysiology}</p>
                </div>
              </div>
            )}

            {guideline.pharmacology && (
              <div className="flex gap-4">
                <div className="mt-1 p-2 rounded-lg bg-emerald-50 text-emerald-600 shrink-0 h-fit">
                  <Info className="h-5 w-5" />
                </div>
                <div className="space-y-2">
                  <h3 className="font-bold text-slate-800 uppercase tracking-tight text-sm">Pharmacology</h3>
                  <p className="text-slate-600 leading-relaxed">{guideline.pharmacology}</p>
                </div>
              </div>
            )}

            {guideline.dispensing_guidance && (
              <div className="flex gap-4">
                <div className="mt-1 p-2 rounded-lg bg-amber-50 text-amber-600 shrink-0 h-fit">
                  <AlertCircle className="h-5 w-5" />
                </div>
                <div className="space-y-2">
                  <h3 className="font-bold text-slate-800 uppercase tracking-tight text-sm">Dispensing Notes</h3>
                  <p className="text-slate-600 leading-relaxed">{guideline.dispensing_guidance}</p>
                </div>
              </div>
            )}
          </div>
        </section>
      )}
    </div>
  )
}
