import { useState, useEffect } from "react"
import { Search, Filter, MoreHorizontal, Edit, Eye, Trash2, MapPin, Star, DollarSign, Building2, ExternalLink } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "./ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "./ui/dialog"
import { Textarea } from "./ui/textarea"
import { Label } from "./ui/label"
import { ImageWithFallback } from "./figma/ImageWithFallback"
import { useApp } from "../contexts/AppContext"

// Property type inferred from the context
type Property = NonNullable<ReturnType<typeof useApp>['properties'][0]>

export function PropertyList() {
  const { properties, loadProperties, deleteProperty, updateProperty } = useApp()
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [selectedProperty, setSelectedProperty] = useState<Property | null>(null)
  const [isViewModalOpen, setIsViewModalOpen] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [editFormData, setEditFormData] = useState<Partial<Property>>({})

  useEffect(() => {
    loadProperties()
  }, [])

  const filteredProperties = properties.filter(property => {
    const matchesSearch = property.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         property.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         property.state.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || property.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'inactive': return 'bg-gray-100 text-gray-800'
      case 'draft': return 'bg-yellow-100 text-yellow-800'
      case 'suspended': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const handleViewProperty = (property: Property) => {
    setSelectedProperty(property)
    setIsViewModalOpen(true)
  }

  const handleEditProperty = (property: Property) => {
    setSelectedProperty(property)
    setEditFormData({
      title: property.title,
      description: property.description,
      price_per_night: property.price_per_night,
      bedrooms: property.bedrooms,
      bathrooms: property.bathrooms,
      max_guests: property.max_guests,
      status: property.status
    })
    setIsEditModalOpen(true)
  }

  const handleUpdateProperty = async () => {
    if (!selectedProperty) return
    
    try {
      await updateProperty(selectedProperty.id, editFormData)
      setIsEditModalOpen(false)
      setSelectedProperty(null)
      setEditFormData({})
    } catch (error) {
      console.error('Failed to update property:', error)
    }
  }

  const handleDeleteProperty = async (propertyId: string) => {
    if (confirm('Are you sure you want to delete this property?')) {
      try {
        await deleteProperty(propertyId)
      } catch (error) {
        console.error('Failed to delete property:', error)
      }
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1>Properties</h1>
        <p className="text-muted-foreground">
          Manage your rental properties and track their performance.
        </p>
      </div>

      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search properties..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
            <SelectItem value="suspended">Suspended</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filteredProperties.map((property) => (
          <Card key={property.id} className="overflow-hidden property-card">
            <div className="aspect-[3/2] relative">
              <ImageWithFallback
                src={property.images && property.images.length > 0 && !property.images[0].startsWith('blob:') 
                  ? property.images[0] 
                  : "/placeholder-property.jpg"}
                alt={property.title}
                className="object-cover w-full h-full rounded-t-lg"
              />
              <Badge className={`absolute top-2 right-2 ${getStatusColor(property.status)}`}>
                {property.status.charAt(0).toUpperCase() + property.status.slice(1)}
              </Badge>
              {property.images && property.images[0] && property.images[0].startsWith('blob:') && (
                <div className="absolute bottom-2 left-2 bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded">
                  Image Upload Issue
                </div>
              )}
            </div>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <CardTitle className="leading-tight truncate">{property.title}</CardTitle>
                  <CardDescription className="flex items-center mt-1">
                    <MapPin className="h-4 w-4 mr-1 flex-shrink-0" />
                    <span className="truncate">{property.city}, {property.state}</span>
                  </CardDescription>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="h-6 w-6 p-0">
                      <MoreHorizontal className="h-3 w-3" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => handleViewProperty(property)}>
                      <Eye className="h-4 w-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleEditProperty(property)}>
                      <Edit className="h-4 w-4 mr-2" />
                      Edit Property
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      className="text-red-600"
                      onClick={() => handleDeleteProperty(property.id)}
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <div className="space-y-2">
                <p className="text-muted-foreground text-sm">
                  {property.bedrooms}bd • {property.bathrooms}ba • {property.max_guests} guests
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex items-baseline">
                    <span className="font-bold text-green-600">${property.price_per_night}</span>
                    <span className="text-muted-foreground ml-1">/night</span>
                  </div>
                  {property.rating && (
                    <div className="flex items-center">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="ml-1 font-medium">{property.rating}</span>
                    </div>
                  )}
                </div>
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
            {properties.length === 0 
              ? "You haven't created any properties yet. Get started by adding your first property!" 
              : "Try adjusting your search or filter criteria."}
          </p>
          {properties.length === 0 && (
            <Button>Add Your First Property</Button>
          )}
        </div>
      )}

      {/* View Property Modal */}
      <Dialog open={isViewModalOpen} onOpenChange={setIsViewModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Property Details</DialogTitle>
          </DialogHeader>
          {selectedProperty && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="font-medium">Title</Label>
                  <p className="text-sm text-muted-foreground">{selectedProperty.title}</p>
                </div>
                <div>
                  <Label className="font-medium">Status</Label>
                  <Badge className={getStatusColor(selectedProperty.status)}>
                    {selectedProperty.status.charAt(0).toUpperCase() + selectedProperty.status.slice(1)}
                  </Badge>
                </div>
              </div>
              
              <div>
                <Label className="font-medium">Description</Label>
                <p className="text-sm text-muted-foreground mt-1">{selectedProperty.description || 'No description provided'}</p>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <Label className="font-medium">Price per night</Label>
                  <p className="text-sm text-muted-foreground">${selectedProperty.price_per_night}</p>
                </div>
                <div>
                  <Label className="font-medium">Bedrooms</Label>
                  <p className="text-sm text-muted-foreground">{selectedProperty.bedrooms}</p>
                </div>
                <div>
                  <Label className="font-medium">Bathrooms</Label>
                  <p className="text-sm text-muted-foreground">{selectedProperty.bathrooms}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="font-medium">Max Guests</Label>
                  <p className="text-sm text-muted-foreground">{selectedProperty.max_guests}</p>
                </div>
                <div>
                  <Label className="font-medium">Location</Label>
                  <p className="text-sm text-muted-foreground">{selectedProperty.city}, {selectedProperty.state}</p>
                </div>
              </div>

              {selectedProperty.amenities && selectedProperty.amenities.length > 0 && (
                <div>
                  <Label className="font-medium">Amenities</Label>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedProperty.amenities.map((amenity, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {amenity}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Edit Property Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Property</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-title">Title</Label>
              <Input
                id="edit-title"
                value={editFormData.title || ''}
                onChange={(e) => setEditFormData(prev => ({ ...prev, title: e.target.value }))}
              />
            </div>

            <div>
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                value={editFormData.description || ''}
                onChange={(e) => setEditFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="edit-price">Price per night ($)</Label>
                <Input
                  id="edit-price"
                  type="number"
                  value={editFormData.price_per_night || ''}
                  onChange={(e) => setEditFormData(prev => ({ ...prev, price_per_night: Number(e.target.value) }))}
                />
              </div>
              <div>
                <Label htmlFor="edit-status">Status</Label>
                <Select
                  value={editFormData.status || ''}
                  onValueChange={(value) => setEditFormData(prev => ({ ...prev, status: value as any }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                    <SelectItem value="suspended">Suspended</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <Label htmlFor="edit-bedrooms">Bedrooms</Label>
                <Input
                  id="edit-bedrooms"
                  type="number"
                  min="1"
                  value={editFormData.bedrooms || ''}
                  onChange={(e) => setEditFormData(prev => ({ ...prev, bedrooms: Number(e.target.value) }))}
                />
              </div>
              <div>
                <Label htmlFor="edit-bathrooms">Bathrooms</Label>
                <Input
                  id="edit-bathrooms"
                  type="number"
                  min="1"
                  value={editFormData.bathrooms || ''}
                  onChange={(e) => setEditFormData(prev => ({ ...prev, bathrooms: Number(e.target.value) }))}
                />
              </div>
              <div>
                <Label htmlFor="edit-max-guests">Max Guests</Label>
                <Input
                  id="edit-max-guests"
                  type="number"
                  min="1"
                  value={editFormData.max_guests || ''}
                  onChange={(e) => setEditFormData(prev => ({ ...prev, max_guests: Number(e.target.value) }))}
                />
              </div>
            </div>

            <div className="flex justify-end space-x-2 pt-4">
              <Button variant="outline" onClick={() => setIsEditModalOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleUpdateProperty}>
                Save Changes
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}