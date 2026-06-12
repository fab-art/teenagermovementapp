import guidelinesData from "@/data/guidelines.json"
import drugData from "@/data/drug_master.json"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Stethoscope, Microscope, Pill, AlertCircle, ChevronRight, ListFilter } from "lucide-react"
import Link from "next/link"
import { notFound } from "next/navigation"

export async function generateStaticParams() {
  return guidelinesData.map((guide) => ({
    id: guide.atc_code,
  }))
}

export default async function TherapeuticClassDetailPage({ params }: { params: { id: string } }) {
  const { id } = await params
  const guideline = guidelinesData.find(g => g.atc_code === id)

  if (!guideline) notFound()

  const drugsInClass = drugData.filter(d => d.atc_code === id || d.atc_code.startsWith(id))

  return (
    <div className="max-w-5xl mx-auto space-y-12 pb-20">
      <nav className="flex items-center gap-2 text-sm text-slate-500">
        <Link href="/therapeutic-classes" className="hover:text-blue-600">Classes</Link>
        <ChevronRight className="h-4 w-4" />
        <span className="font-medium text-slate-900">{guideline.title}</span>
      </nav>

      <section className="space-y-6">
        <div className="flex items-center gap-6">
          <div className="p-4 rounded-2xl bg-blue-600 text-white shadow-lg">
            <Stethoscope className="h-10 w-10" />
          </div>
          <div>
            <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">{guideline.title}</h1>
            <p className="text-lg font-mono text-blue-600 mt-1 font-bold uppercase tracking-widest">{guideline.atc_code}</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pt-8">
          <div className="lg:col-span-2 space-y-10">
            {guideline.pathophysiology && (
              <div className="space-y-3">
                <h2 className="text-lg font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <Microscope className="h-5 w-5 text-blue-500" />
                  Pathophysiology & Disease Mechanism
                </h2>
                <p className="text-slate-600 leading-relaxed text-lg">{guideline.pathophysiology}</p>
              </div>
            )}

            {guideline.pharmacology && (
              <div className="space-y-3">
                <h2 className="text-lg font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                  <Pill className="h-5 w-5 text-emerald-500" />
                  Pharmacological Principles
                </h2>
                <p className="text-slate-600 leading-relaxed text-lg">{guideline.pharmacology}</p>
              </div>
            )}

            {guideline.dispensing_guidance && (
              <div className="space-y-3 p-6 rounded-2xl bg-amber-50 border border-amber-100">
                <h2 className="text-lg font-bold text-amber-900 uppercase tracking-wider flex items-center gap-2">
                  <AlertCircle className="h-5 w-5" />
                  Clinical Dispensing Guidance
                </h2>
                <p className="text-amber-800 leading-relaxed">{guideline.dispensing_guidance}</p>
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="font-bold text-slate-900 uppercase tracking-widest text-sm flex items-center gap-2">
                <ListFilter className="h-4 w-4" />
                Medicines ({drugsInClass.length})
              </h2>
            </div>
            <div className="space-y-3">
              {drugsInClass.map((drug) => (
                <Link key={drug.id} href={`/medicines/${drug.id}`}>
                  <Card className="hover:border-blue-300 hover:shadow-sm transition-all group mb-3">
                    <CardContent className="p-4">
                      <h4 className="font-bold text-slate-900 group-hover:text-blue-600 transition-colors">{drug.brand_name}</h4>
                      <p className="text-xs text-slate-500 mt-1 uppercase truncate">{drug.generic_name}</p>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
