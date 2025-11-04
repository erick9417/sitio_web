'use client'

import { useState, useCallback } from 'react'
import { debounce } from 'lodash'

interface FiltersProps {
  onSearchChange: (search: string) => void
}

export function Filters({ onSearchChange }: FiltersProps) {
  const [searchTerm, setSearchTerm] = useState('')

  const debouncedSearch = useCallback(
    debounce((value: string) => {
      onSearchChange(value)
    }, 300),
    [onSearchChange]
  )

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setSearchTerm(value)
    debouncedSearch(value)
  }

  return (
    <div className="mb-6 flex flex-wrap gap-4">
      <div className="flex-1 min-w-[200px]">
        <input
          type="text"
          placeholder="Buscar por SKU o nombre..."
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={searchTerm}
          onChange={handleSearchChange}
        />
      </div>
      {/* Additional filters can be added here */}
    </div>
  )
}