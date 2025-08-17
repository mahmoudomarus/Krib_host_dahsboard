import { useState } from "react"
import { ArrowLeft, ArrowRight, Bot, User, Upload, Check, MapPin, Home, Camera, Sparkles } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Label } from "./ui/label"
import { Textarea } from "./ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"
import { Checkbox } from "./ui/checkbox"
import { Badge } from "./ui/badge"
import { Progress } from "./ui/progress"
import { useApp } from "../contexts/AppContext"

type WizardStep = 'basic-info' | 'ai-description' | 'images' | 'amenities' | 'preview' | 'published'

interface PropertyData {
  title: string
  address: string
  city: string
  state: string
  country: string
  property_type: string
  bedrooms: string
  bathrooms: string
  max_guests: string
  price_per_night: string
  description: string
  images: string[]
  amenities: string[]
}

const amenitiesList = [
  "WiFi", "Kitchen", "Washing Machine", "Air Conditioning", "Heating", "TV", "Parking",
  "Pool", "Hot Tub", "Gym", "Balcony", "Garden", "Pet Friendly", "Smoking Allowed",
  "Fireplace", "Elevator", "Wheelchair Accessible", "Beach Access", "Mountain View"
]

export function AddPropertyWizard() {
  const { createProperty, generateAIDescription } = useApp()
  const [currentStep, setCurrentStep] = useState<WizardStep>('basic-info')
  const [isPublishing, setIsPublishing] = useState(false)
  const [propertyData, setPropertyData] = useState<PropertyData>({
    title: '',
    address: '',
    city: '',
    state: '',
    country: 'USA',
    property_type: '',
    bedrooms: '',
    bathrooms: '',
    max_guests: '',
    price_per_night: '',
    description: '',
    images: [],
    amenities: []
  })
  const [isGeneratingDescription, setIsGeneratingDescription] = useState(false)
  const [aiMessages, setAiMessages] = useState<Array<{role: 'user' | 'ai', content: string}>>([])

  const steps = [
    { id: 'basic-info', title: 'Basic Information', icon: Home },
    { id: 'ai-description', title: 'AI Description', icon: Bot },
    { id: 'images', title: 'Images', icon: Camera },
    { id: 'amenities', title: 'Amenities', icon: Sparkles },
    { id: 'preview', title: 'Preview', icon: Check },
  ]

  const currentStepIndex = steps.findIndex(step => step.id === currentStep)
  const progress = ((currentStepIndex + 1) / steps.length) * 100

  const handleBasicInfoSubmit = () => {
    if (propertyData.title && propertyData.location && propertyData.propertyType) {
      setCurrentStep('ai-description')
      // Simulate AI conversation start
      setAiMessages([
        {
          role: 'ai',
          content: `Great! I can see you're adding "${propertyData.title}" in ${propertyData.location}. Let me generate a compelling description for your ${propertyData.propertyType.toLowerCase()}. I'll highlight the key features and make it attractive to potential guests.`
        }
      ])
    }
  }

  const generateDescription = () => {
    setIsGeneratingDescription(true)
    
    // Simulate API call to generate description
    setTimeout(() => {
      const generatedDescription = `Experience the perfect blend of comfort and style at this stunning ${propertyData.propertyType.toLowerCase()} in ${propertyData.location}. This beautifully appointed ${propertyData.bedrooms}-bedroom space offers a serene retreat for up to ${propertyData.maxGuests} guests.

The space features modern amenities and thoughtful design throughout. Whether you're here for business or leisure, you'll find everything you need for a memorable stay. The location provides easy access to local attractions while maintaining a peaceful atmosphere.

Perfect for families, couples, or business travelers looking for a home away from home. Book now for an unforgettable experience!`

      setPropertyData(prev => ({ ...prev, description: generatedDescription }))
      setAiMessages(prev => [...prev, 
        {
          role: 'user',
          content: 'Please generate a description for my property.'
        },
        {
          role: 'ai',
          content: 'Perfect! I\'ve created a compelling description for your property. Here\'s what I came up with:'
        }
      ])
      setIsGeneratingDescription(false)
    }, 2000)
  }

  const handleImageUpload = () => {
    // Simulate image upload
    const sampleImages = [
      "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=400&h=300&fit=crop",
      "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=400&h=300&fit=crop"
    ]
    setPropertyData(prev => ({ ...prev, images: sampleImages }))
  }

  const toggleAmenity = (amenity: string) => {
    setPropertyData(prev => ({
      ...prev,
      amenities: prev.amenities.includes(amenity)
        ? prev.amenities.filter(a => a !== amenity)
        : [...prev.amenities, amenity]
    }))
  }

  const handlePublish = async () => {
    setIsPublishing(true)
    
    try {
      const propertyPayload = {
        title: propertyData.title,
        location: propertyData.location,
        propertyType: propertyData.propertyType,
        bedrooms: parseInt(propertyData.bedrooms),
        bathrooms: parseInt(propertyData.bathrooms),
        maxGuests: parseInt(propertyData.maxGuests),
        price: parseInt(propertyData.price),
        description: propertyData.description,
        images: propertyData.images,
        amenities: propertyData.amenities
      }

      const createdProperty = await createProperty(propertyPayload)
      
      if (createdProperty) {
        setCurrentStep('published')
      } else {
        // Handle error - could show a toast or error message
        console.error('Failed to create property')
      }
    } catch (error) {
      console.error('Error creating property:', error)
    } finally {
      setIsPublishing(false)
    }
  }

  const renderStepContent = () => {
    switch (currentStep) {
      case 'basic-info':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Home className="h-5 w-5" />
                Basic Property Information
              </CardTitle>
              <CardDescription>
                Let's start with the essential details about your property.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Property Title</Label>
                  <Input 
                    id="title"
                    placeholder="e.g., Cozy Downtown Apartment"
                    value={propertyData.title}
                    onChange={(e) => setPropertyData(prev => ({ ...prev, title: e.target.value }))}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="location">Location</Label>
                  <Input 
                    id="location"
                    placeholder="e.g., New York, NY"
                    value={propertyData.location}
                    onChange={(e) => setPropertyData(prev => ({ ...prev, location: e.target.value }))}
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="propertyType">Property Type</Label>
                  <Select value={propertyData.propertyType} onValueChange={(value) => setPropertyData(prev => ({ ...prev, propertyType: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="apartment">Apartment</SelectItem>
                      <SelectItem value="house">House</SelectItem>
                      <SelectItem value="condo">Condo</SelectItem>
                      <SelectItem value="studio">Studio</SelectItem>
                      <SelectItem value="cabin">Cabin</SelectItem>
                      <SelectItem value="villa">Villa</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bedrooms">Bedrooms</Label>
                  <Select value={propertyData.bedrooms} onValueChange={(value) => setPropertyData(prev => ({ ...prev, bedrooms: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Beds" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1,2,3,4,5,6].map(num => (
                        <SelectItem key={num} value={num.toString()}>{num}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bathrooms">Bathrooms</Label>
                  <Select value={propertyData.bathrooms} onValueChange={(value) => setPropertyData(prev => ({ ...prev, bathrooms: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Baths" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1,2,3,4,5,6].map(num => (
                        <SelectItem key={num} value={num.toString()}>{num}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxGuests">Max Guests</Label>
                  <Select value={propertyData.maxGuests} onValueChange={(value) => setPropertyData(prev => ({ ...prev, maxGuests: value }))}>
                    <SelectTrigger>
                      <SelectValue placeholder="Guests" />
                    </SelectTrigger>
                    <SelectContent>
                      {[1,2,3,4,5,6,7,8,9,10].map(num => (
                        <SelectItem key={num} value={num.toString()}>{num}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="price">Price per Night (USD)</Label>
                <Input 
                  id="price"
                  type="number"
                  placeholder="150"
                  value={propertyData.price}
                  onChange={(e) => setPropertyData(prev => ({ ...prev, price: e.target.value }))}
                />
              </div>
              
              <Button onClick={handleBasicInfoSubmit} className="w-full">
                Continue to AI Description
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </CardContent>
          </Card>
        )

      case 'ai-description':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                AI-Powered Description Generation
              </CardTitle>
              <CardDescription>
                Let our AI create a compelling description for your property.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* AI Chat Interface */}
              <div className="border rounded-lg p-4 h-64 overflow-y-auto bg-muted/20">
                {aiMessages.map((message, index) => (
                  <div key={index} className={`flex gap-3 mb-4 ${message.role === 'user' ? 'justify-end' : ''}`}>
                    <div className={`flex gap-3 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        message.role === 'ai' ? 'bg-primary text-primary-foreground' : 'bg-secondary'
                      }`}>
                        {message.role === 'ai' ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                      </div>
                      <div className={`rounded-lg p-3 ${
                        message.role === 'ai' ? 'bg-secondary' : 'bg-primary text-primary-foreground'
                      }`}>
                        <p className="text-sm">{message.content}</p>
                      </div>
                    </div>
                  </div>
                ))}
                
                {isGeneratingDescription && (
                  <div className="flex gap-3 mb-4">
                    <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="bg-secondary rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <div className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full"></div>
                        <span className="text-sm">Generating description...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              {!propertyData.description ? (
                <Button onClick={generateDescription} disabled={isGeneratingDescription} className="w-full">
                  Generate Description with AI
                </Button>
              ) : (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Generated Description</Label>
                    <Textarea 
                      value={propertyData.description}
                      onChange={(e) => setPropertyData(prev => ({ ...prev, description: e.target.value }))}
                      className="min-h-[120px]"
                    />
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={generateDescription} variant="outline">
                      Regenerate
                    </Button>
                    <Button onClick={() => setCurrentStep('images')} className="flex-1">
                      Continue to Images
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )

      case 'images':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5" />
                Property Images
              </CardTitle>
              <CardDescription>
                Add photos to showcase your property. Great photos increase bookings by 40%.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {propertyData.images.length === 0 ? (
                <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
                  <Upload className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="font-medium mb-2">Upload Property Photos</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Add up to 20 high-quality photos of your property
                  </p>
                  <Button onClick={handleImageUpload}>
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Photos
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {propertyData.images.map((image, index) => (
                      <div key={index} className="relative">
                        <img 
                          src={image} 
                          alt={`Property ${index + 1}`}
                          className="w-full h-32 object-cover rounded-lg"
                        />
                        {index === 0 && (
                          <Badge className="absolute top-2 left-2">Main Photo</Badge>
                        )}
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={handleImageUpload}>
                      Add More Photos
                    </Button>
                    <Button onClick={() => setCurrentStep('amenities')} className="flex-1">
                      Continue to Amenities
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )

      case 'amenities':
        return (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                Property Amenities
              </CardTitle>
              <CardDescription>
                Select all amenities available at your property.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {amenitiesList.map((amenity) => (
                  <div key={amenity} className="flex items-center space-x-2">
                    <Checkbox 
                      id={amenity}
                      checked={propertyData.amenities.includes(amenity)}
                      onCheckedChange={() => toggleAmenity(amenity)}
                    />
                    <Label htmlFor={amenity} className="text-sm">{amenity}</Label>
                  </div>
                ))}
              </div>
              
              <div className="pt-4">
                <Button onClick={() => setCurrentStep('preview')} className="w-full">
                  Continue to Preview
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )

      case 'preview':
        return (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Check className="h-5 w-5" />
                  Preview Your Listing
                </CardTitle>
                <CardDescription>
                  Review how your property will appear to potential guests.
                </CardDescription>
              </CardHeader>
            </Card>
            
            {/* Property Preview */}
            <Card>
              <CardContent className="p-0">
                {propertyData.images[0] && (
                  <img 
                    src={propertyData.images[0]} 
                    alt={propertyData.title}
                    className="w-full h-64 object-cover rounded-t-lg"
                  />
                )}
                <div className="p-6 space-y-4">
                  <div>
                    <h2 className="text-xl font-semibold">{propertyData.title}</h2>
                    <p className="text-muted-foreground flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      {propertyData.location}
                    </p>
                  </div>
                  
                  <div className="flex gap-4 text-sm">
                    <span>{propertyData.bedrooms} bed</span>
                    <span>{propertyData.bathrooms} bath</span>
                    <span>{propertyData.maxGuests} guests</span>
                    <span className="font-semibold">${propertyData.price}/night</span>
                  </div>
                  
                  <p className="text-sm">{propertyData.description}</p>
                  
                  <div>
                    <h4 className="font-medium mb-2">Amenities</h4>
                    <div className="flex flex-wrap gap-2">
                      {propertyData.amenities.slice(0, 6).map((amenity) => (
                        <Badge key={amenity} variant="secondary">{amenity}</Badge>
                      ))}
                      {propertyData.amenities.length > 6 && (
                        <Badge variant="outline">+{propertyData.amenities.length - 6} more</Badge>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setCurrentStep('basic-info')}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Edit Details
              </Button>
              <Button onClick={handlePublish} className="flex-1" disabled={isPublishing}>
                {isPublishing ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin h-4 w-4 border-2 border-primary-foreground border-t-transparent rounded-full"></div>
                    Publishing...
                  </div>
                ) : (
                  "Publish Property"
                )}
              </Button>
            </div>
          </div>
        )

      case 'published':
        return (
          <Card>
            <CardContent className="p-8 text-center space-y-4">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                <Check className="h-8 w-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-semibold">Property Published Successfully!</h2>
              <p className="text-muted-foreground">
                Your property "{propertyData.title}" is now live and available for booking.
              </p>
              <div className="flex gap-2 justify-center">
                <Button onClick={() => setCurrentStep('basic-info')}>
                  Add Another Property
                </Button>
                <Button variant="outline">
                  View Property
                </Button>
              </div>
            </CardContent>
          </Card>
        )

      default:
        return null
    }
  }

  if (currentStep === 'published') {
    return (
      <div className="p-6">
        {renderStepContent()}
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="mb-2">Add New Property</h1>
        <p className="text-muted-foreground">
          Create a stunning property listing with AI assistance.
        </p>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span>Progress</span>
          <span>{Math.round(progress)}% Complete</span>
        </div>
        <Progress value={progress} className="h-2" />
      </div>

      {/* Step Indicators */}
      <div className="flex justify-center">
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {steps.map((step, index) => {
            const isActive = step.id === currentStep
            const isCompleted = index < currentStepIndex
            const Icon = step.icon
            
            return (
              <div key={step.id} className="flex items-center gap-2">
                <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
                  isActive ? 'bg-primary text-primary-foreground border-primary' :
                  isCompleted ? 'bg-secondary text-secondary-foreground border-secondary' :
                  'bg-background border-border'
                }`}>
                  <Icon className="h-4 w-4" />
                  <span className="text-sm font-medium hidden sm:inline">{step.title}</span>
                </div>
                {index < steps.length - 1 && (
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                )}
              </div>
            )
          })}
        </div>
      </div>

      {renderStepContent()}
    </div>
  )
}