import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import guidelinesData from "@/data/guidelines.json"
import Link from "next/link"
import { Stethoscope } from "lucide-react"

export default function TherapeuticClassesPage() {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Therapeutic Classes</h1>
        <p className="text-slate-500 mt-1">Explore guidelines by Anatomical Therapeutic Chemical (ATC) classification.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {guidelinesData.map((cls) => (
          <Link key={cls.atc_code} href={`/therapeutic-classes/${cls.atc_code}`}>
            <Card className="hover:shadow-md hover:border-blue-200 transition-all group h-full">
              <CardHeader className="flex flex-row items-center space-y-0 pb-2">
                <div className="p-2 rounded-lg bg-blue-50 text-blue-600 border border-blue-100 mr-4 transition-transform group-hover:scale-110">
                  <Stethoscope className="h-5 w-5" />
                </div>
                <div>
                  <CardTitle className="text-lg group-hover:text-blue-600 transition-colors">{cls.title}</CardTitle>
                  <p className="text-xs font-mono text-slate-500">{cls.atc_code}</p>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 line-clamp-2 italic">
                  {cls.pathophysiology || "Guideline content available."}
                </p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}
