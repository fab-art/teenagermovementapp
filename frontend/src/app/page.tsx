import { Search } from "@/components/search"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Pill, Stethoscope, CreditCard, ClipboardList, BookOpen } from "lucide-react"
import Link from "next/link"

const quickActions = [
  {
    title: "Medicines",
    description: "Browse 1,441 generic drugs",
    icon: Pill,
    href: "/medicines",
    color: "bg-blue-50 text-blue-600 border-blue-100",
  },
  {
    title: "Guidelines",
    description: "Clinical dispensing reference",
    icon: BookOpen,
    href: "/guidelines",
    color: "bg-amber-50 text-amber-600 border-amber-100",
  },
  {
    title: "Reimbursement",
    description: "Check RHIA coverage",
    icon: CreditCard,
    href: "/reimbursement",
    color: "bg-emerald-50 text-emerald-600 border-emerald-100",
  },
  {
    title: "Therapeutic Classes",
    description: "ATC classification lookup",
    icon: Stethoscope,
    href: "/therapeutic-classes",
    color: "bg-purple-50 text-purple-600 border-purple-100",
  },
]

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto space-y-12">
      <section className="text-center space-y-4 pt-12 pb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-xs font-bold uppercase tracking-widest mb-4">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          Official 2026 Guideline
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
          Rwanda Medicines <br/><span className="text-blue-600 font-serif italic">Formulary</span>
        </h1>
        <p className="text-lg text-slate-500 max-w-2xl mx-auto font-medium leading-relaxed">
          Comprehensive pharmacological & dispensing reference based on the
          <span className="text-slate-800 font-bold"> RHIA Reimbursable Medicines Tariff — January 2026.</span>
        </p>
        <div className="pt-10">
          <Search />
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-xl font-bold text-slate-900 uppercase tracking-wider flex items-center gap-3">
          <span className="h-px w-8 bg-slate-200"></span>
          Quick Navigation
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickActions.map((action) => (
            <Link key={action.title} href={action.href}>
              <Card className="hover:shadow-lg transition-all duration-300 border-slate-200 group overflow-hidden relative">
                <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                  <action.icon className="h-24 w-24 -mr-8 -mt-8" />
                </div>
                <CardHeader className="flex flex-row items-center space-y-0 pb-4">
                  <div className={`p-3 rounded-xl ${action.color} border mr-4 transition-transform group-hover:scale-110`}>
                    <action.icon className="h-6 w-6" />
                  </div>
                  <div className="space-y-1">
                    <CardTitle className="text-lg font-bold">{action.title}</CardTitle>
                    <p className="text-sm text-slate-500 font-medium">
                      {action.description}
                    </p>
                  </div>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      <section className="space-y-6 pb-20">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-900 uppercase tracking-wider flex items-center gap-3">
            <span className="h-px w-8 bg-slate-200"></span>
            Featured Classes
          </h2>
          <Link href="/therapeutic-classes" className="text-sm font-bold text-blue-600 hover:text-blue-700 uppercase tracking-wider">
            All 80+ Subclasses
          </Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { name: "Analgesics", code: "N02" },
            { name: "Antibacterials", code: "J01" },
            { name: "Antihypertensives", code: "C02" },
            { name: "Antidiabetics", code: "A10" }
          ].map((cls) => (
            <Card key={cls.code} className="hover:bg-blue-50/50 hover:border-blue-200 cursor-pointer transition-colors group">
              <CardContent className="p-6 text-center">
                <p className="text-xs font-mono text-slate-400 mb-1 group-hover:text-blue-400">{cls.code}</p>
                <p className="font-bold text-slate-900 group-hover:text-blue-600">{cls.name}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  )
}
