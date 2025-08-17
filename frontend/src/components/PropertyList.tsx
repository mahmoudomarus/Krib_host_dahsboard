import { useState } from "react"
import { Search, Filter, MoreHorizontal, Edit, Eye, Trash2, MapPin, Star, DollarSign } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"
import { ImageWithFallback } from "./figma/ImageWithFallback"

const properties = [
  {
    id: "1",
    title: "Modern Downtown Loft",
    location: "New York, NY",
    type: "Apartment",
    bedrooms: 2,
    bathrooms: 2,
    price: 150,
    rating: 4.9,
    reviews: 127,
    status: "active",
    image: "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&h=300&fit=crop",
    bookings: 8,
    revenue: "$2,340"
  },
  {
    id: "2",
    title: "Cozy Beach House",
    location: "Miami, FL",
    type: "House",
    bedrooms: 3,
    bathrooms: 2,
    price: 220,
    rating: 4.8,
    reviews: 89,
    status: "active",
    image: "https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=400&h=300&fit=crop",
    bookings: 6,
    revenue: "$1,890"
  },
  {
    id: "3",
    title: "Mountain Cabin Retreat",
    location: "Aspen, CO",
    type: "Cabin",
    bedrooms: 4,
    bathrooms: 3,
    price: 180,
    rating: 4.7,
    reviews: 54,
    status: "active",
    image: "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop",
    bookings: 5,
    revenue: "$1,650"
  },
  {
    id: "4",
    title: "Urban Studio",
    location: "San Francisco, CA",
    type: "Studio",
    bedrooms: 1,
    bathrooms: 1,
    price: 120,
    rating: 4.6,
    reviews: 23,
    status: "draft",
    image: "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&h=300&fit=crop",
    bookings: 0,
    revenue: "$0"
  }
]

export function PropertyList() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")

  const filteredProperties = properties.filter(property => {
    const matchesSearch = property.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         property.location.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || property.status === statusFilter
    return matchesSearch && matchesStatus
  })

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="mb-2">My Properties</h1>
        <p className="text-muted-foreground">
          Manage and monitor your rental property listings.
        </p>
      </div>

      {/* Filters and Search */}
      <div className="flex gap-4 items-center">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input 
            placeholder="Search properties..." 
            className="pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Properties</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline" size="sm">
          <Filter className="h-4 w-4 mr-2" />
          More Filters
        </Button>
      </div>

      {/* Properties Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredProperties.map((property) => (
          <Card key={property.id} className="overflow-hidden">
            <div className="relative">
              <ImageWithFallback 
                src={property.image} 
                alt={property.title}
                className="w-full h-48 object-cover"
              />
              <Badge 
                variant={property.status === 'active' ? 'default' : 'secondary'}
                className="absolute top-2 left-2"
              >
                {property.status}
              </Badge>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    className="absolute top-2 right-2 h-8 w-8 p-0 bg-white/80 hover:bg-white"
                  >
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>
                    <Eye className="h-4 w-4 mr-2" />
                    View Details
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Property
                  </DropdownMenuItem>
                  <DropdownMenuItem className="text-destructive">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
            
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">{property.title}</CardTitle>
              <CardDescription className="flex items-center gap-1">
                <MapPin className="h-4 w-4" />
                {property.location}
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>{property.bedrooms} bed • {property.bathrooms} bath</span>
                <span className="font-medium">${property.price}/night</span>
              </div>
              
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 fill-current text-yellow-500" />
                  <span>{property.rating}</span>
                  <span className="text-muted-foreground">({property.reviews})</span>
                </div>
                <div className="flex items-center gap-1">
                  <DollarSign className="h-4 w-4 text-green-600" />
                  <span>{property.revenue}</span>
                </div>
              </div>
              
              <div className="flex justify-between items-center pt-2 border-t">
                <span className="text-sm text-muted-foreground">
                  {property.bookings} bookings this month
                </span>
                <Button variant="outline" size="sm">
                  Manage
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredProperties.length === 0 && (
        <div className="text-center py-12">
          <Building2 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No properties found</h3>
          <p className="text-muted-foreground mb-4">
            Try adjusting your search or filter criteria.
          </p>
          <Button>Add Your First Property</Button>
        </div>
      )}
    </div>
  )
}