"use client"

import { useFavorites } from "@/lib/favorites"
import { Button } from "@/components/ui/button"
import { Star } from "lucide-react"

export function FavoriteButton({ id }: { id: string }) {
  const { isFavorite, toggleFavorite } = useFavorites()
  const active = isFavorite(id)

  return (
    <Button
      variant="outline"
      className={`w-full font-bold transition-all ${active ? 'bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100' : ''}`}
      onClick={() => toggleFavorite(id)}
    >
      <Star className={`mr-2 h-4 w-4 ${active ? 'fill-amber-500 text-amber-500' : ''}`} />
      {active ? 'Favorited' : 'Add to Favorites'}
    </Button>
  )
}
