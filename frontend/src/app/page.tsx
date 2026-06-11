import { Search } from "@/components/search"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Pill, Stethoscope, CreditCard, ClipboardList } from "lucide-react"
import Link from "next/link"

const quickActions = [
  {
    title: "Medicines",
    description: "Browse all generic drugs",
    icon: Pill,
    href: "/medicines",
    color: "bg-blue-50 text-blue-600 border-blue-100",
  },
  {
    title: "Reimbursement",
    description: "Check RHIA coverage",
    icon: CreditCard,
    href: "/reimbursement",
    color: "bg-emerald-50 text-emerald-600 border-emerald-100",
  },
  {
    title: "Product Registry",
    description: "Rwanda FDA authorized products",
    icon: ClipboardList,
    href: "/product-registry",
    color: "bg-purple-50 text-purple-600 border-purple-100",
  },
  {
    title: "Guidelines",
    description: "Therapeutic class guidelines",
    icon: Stethoscope,
    href: "/guidelines",
    color: "bg-amber-50 text-amber-600 border-amber-100",
  },
]

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto space-y-12">
      <section className="text-center space-y-4 pt-8">
        <h1 className="text-4xl font-bold tracking-tight text-slate-900">
          Rwanda Medicines Formulary
        </h1>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto">
          Comprehensive access to reimbursable medicines, authorized products, and therapeutic guidelines.
        </p>
        <div className="pt-8">
          <Search />
        </div>
      </section>

      <section className="space-y-6">
        <h2 className="text-2xl font-semibold text-slate-900">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickActions.map((action) => (
            <Link key={action.title} href={action.href}>
              <Card className="hover:shadow-md transition-shadow border-slate-200">
                <CardHeader className="flex flex-row items-center space-y-0 pb-2">
                  <div className={`p-2 rounded-lg ${action.color} border mr-4`}>
                    <action.icon className="h-6 w-6" />
                  </div>
                  <div className="space-y-1">
                    <CardTitle className="text-lg">{action.title}</CardTitle>
                    <p className="text-sm text-slate-500 font-normal">
                      {action.description}
                    </p>
                  </div>
                </CardHeader>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      <section className="space-y-6 pb-12">
        <div className="flex justify-between items-center">
          <h2 className="text-2xl font-semibold text-slate-900">Featured Therapeutic Classes</h2>
          <Link href="/therapeutic-classes" className="text-sm font-medium text-blue-600 hover:underline">
            View all classes
          </Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {["Analgesics", "Antibacterials", "Antihypertensives", "Antidiabetics"].map((cls) => (
            <Card key={cls} className="hover:bg-slate-50 cursor-pointer">
              <CardContent className="p-6 text-center">
                <p className="font-medium text-slate-900">{cls}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
    </div>
  )
}
