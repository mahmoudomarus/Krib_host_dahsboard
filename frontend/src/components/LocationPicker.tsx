import { useState, useCallback, useRef, useEffect } from "react"
import { GoogleMap, useJsApiLoader, Marker } from "@react-google-maps/api"
import { Search, MapPin, Loader2, AlertTriangle } from "lucide-react"
import { Input } from "./ui/input"
import { Button } from "./ui/button"
import { Card, CardContent } from "./ui/card"
import { Alert, AlertDescription } from "./ui/alert"

interface LocationPickerProps {
  initialLat?: number
  initialLng?: number
  initialAddress?: string
  onLocationChange: (lat: number, lng: number, address: string) => void
}

const mapContainerStyle = {
  width: "100%",
  height: "500px",
}

const defaultCenter = {
  lat: 25.2048,
  lng: 55.2708,
}

const GOOGLE_MAPS_LIBRARIES: ("places")[] = ["places"]

export function LocationPicker({
  initialLat,
  initialLng,
  initialAddress,
  onLocationChange,
}: LocationPickerProps) {
  const { isLoaded, loadError } = useJsApiLoader({
    id: "google-map-script",
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY || "",
    libraries: GOOGLE_MAPS_LIBRARIES,
  })

  const [markerPosition, setMarkerPosition] = useState<{ lat: number; lng: number } | null>(
    initialLat && initialLng ? { lat: initialLat, lng: initialLng } : null
  )
  const [searchQuery, setSearchQuery] = useState(initialAddress || "")
  const [mapCenter, setMapCenter] = useState(
    initialLat && initialLng ? { lat: initialLat, lng: initialLng } : defaultCenter
  )
  const [isGeocoding, setIsGeocoding] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const mapRef = useRef<google.maps.Map | null>(null)

  const onMapLoad = useCallback((map: google.maps.Map) => {
    mapRef.current = map
  }, [])

  const reverseGeocode = async (lat: number, lng: number) => {
    if (!isLoaded) return

    setIsGeocoding(true)
    setError(null)

    try {
      const geocoder = new google.maps.Geocoder()
      const result = await geocoder.geocode({ location: { lat, lng } })

      if (result.results && result.results[0]) {
        const address = result.results[0].formatted_address
        setSearchQuery(address)
        onLocationChange(lat, lng, address)
      }
    } catch (err) {
      console.error("Geocoding error:", err)
      setError("Failed to get address for this location")
    } finally {
      setIsGeocoding(false)
    }
  }

  const handleMapClick = useCallback(
    (e: google.maps.MapMouseEvent) => {
      if (e.latLng) {
        const lat = e.latLng.lat()
        const lng = e.latLng.lng()
        setMarkerPosition({ lat, lng })
        reverseGeocode(lat, lng)
      }
    },
    [isLoaded]
  )

  const handleSearch = async () => {
    if (!searchQuery.trim() || !isLoaded) return

    setIsGeocoding(true)
    setError(null)

    try {
      const geocoder = new google.maps.Geocoder()
      const result = await geocoder.geocode({ address: searchQuery })

      if (result.results && result.results[0]) {
        const location = result.results[0].geometry.location
        const lat = location.lat()
        const lng = location.lng()
        const address = result.results[0].formatted_address

        setMarkerPosition({ lat, lng })
        setMapCenter({ lat, lng })
        setSearchQuery(address)
        onLocationChange(lat, lng, address)

        if (mapRef.current) {
          mapRef.current.panTo({ lat, lng })
          mapRef.current.setZoom(15)
        }
      } else {
        setError("Location not found. Please try a different search.")
      }
    } catch (err: any) {
      console.error("Search error:", err)
      if (err?.message?.includes("REQUEST_DENIED") || err?.message?.includes("API")) {
        setError("Google Maps API error. Check that Geocoding API is enabled and API key is valid.")
      } else {
        setError("Failed to search for location. Please try again.")
      }
    } finally {
      setIsGeocoding(false)
    }
  }

  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser")
      return
    }

    setIsGeocoding(true)
    setError(null)

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const lat = position.coords.latitude
        const lng = position.coords.longitude

        setMarkerPosition({ lat, lng })
        setMapCenter({ lat, lng })
        reverseGeocode(lat, lng)

        if (mapRef.current) {
          mapRef.current.panTo({ lat, lng })
          mapRef.current.setZoom(15)
        }
      },
      (error) => {
        console.error("Geolocation error:", error)
        setError("Failed to get your location. Please check your browser permissions.")
        setIsGeocoding(false)
      }
    )
  }

  if (loadError) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Google Maps failed to load. Ensure VITE_GOOGLE_MAPS_API_KEY is set and has Maps JavaScript API + Geocoding API enabled in Google Cloud Console. Domain restrictions must allow host.krib.ae.
        </AlertDescription>
      </Alert>
    )
  }

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center h-[500px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search for an address or area in UAE..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            className="pl-10"
            disabled={isGeocoding}
          />
        </div>
        <Button onClick={handleSearch} disabled={isGeocoding || !searchQuery.trim()}>
          {isGeocoding ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Searching...
            </>
          ) : (
            "Search"
          )}
        </Button>
        <Button variant="outline" onClick={handleGetCurrentLocation} disabled={isGeocoding}>
          <MapPin className="h-4 w-4" />
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {markerPosition && (
        <Card>
          <CardContent className="pt-4">
            <div className="space-y-2">
              <div className="flex items-start gap-2">
                <MapPin className="h-5 w-5 text-primary mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium">Selected Location</p>
                  <p className="text-sm text-muted-foreground">{searchQuery || "Location set"}</p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Coordinates: {markerPosition.lat.toFixed(6)}, {markerPosition.lng.toFixed(6)}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="rounded-lg overflow-hidden border">
        <GoogleMap
          mapContainerStyle={mapContainerStyle}
          center={mapCenter}
          zoom={markerPosition ? 15 : 11}
          onClick={handleMapClick}
          onLoad={onMapLoad}
          options={{
            streetViewControl: false,
            mapTypeControl: false,
            fullscreenControl: false,
          }}
        >
          {markerPosition && (
            <Marker
              position={markerPosition}
              animation={google.maps.Animation.DROP}
            />
          )}
        </GoogleMap>
      </div>

      <p className="text-sm text-muted-foreground text-center">
        Click anywhere on the map to set your property location
      </p>
    </div>
  )
}

