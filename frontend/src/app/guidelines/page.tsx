import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import guidelinesData from "@/data/guidelines.json"
import { BookOpen, AlertCircle, Pill, Microscope } from "lucide-react"

export default function GuidelinesPage() {
  return (
    <div className="max-w-5xl mx-auto space-y-12 pb-12">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 text-center">Dispensing Guidelines</h1>
        <p className="text-slate-500 mt-2 text-center max-w-2xl mx-auto">
          Comprehensive clinical, pharmacological, and dispensing reference for Rwanda reimbursable medicines.
        </p>
      </div>

      <div className="space-y-16">
        {guidelinesData.map((guide) => (
          <section key={guide.atc_code} className="space-y-6">
            <div className="border-b pb-4">
              <h2 className="text-2xl font-bold text-blue-900 uppercase tracking-tight flex items-center gap-2">
                <span className="text-blue-600">{guide.atc_code}</span>
                {guide.title}
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {guide.pathophysiology && (
                <Card className="border-l-4 border-l-blue-400">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                      <Microscope className="h-4 w-4" />
                      Pathophysiology
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm leading-relaxed text-slate-700">{guide.pathophysiology}</p>
                  </CardContent>
                </Card>
              )}

              {guide.pharmacology && (
                <Card className="border-l-4 border-l-emerald-400">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                      <Pill className="h-4 w-4" />
                      Pharmacology
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm leading-relaxed text-slate-700">{guide.pharmacology}</p>
                  </CardContent>
                </Card>
              )}

              {guide.dispensing_guidance && (
                <Card className="border-l-4 border-l-amber-400">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                      <AlertCircle className="h-4 w-4" />
                      Dispensing Guidance
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm leading-relaxed text-slate-700">{guide.dispensing_guidance}</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </section>
        ))}
      </div>
    </div>
  )
}
