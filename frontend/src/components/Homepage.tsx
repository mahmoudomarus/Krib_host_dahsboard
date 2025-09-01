import { useNavigate } from 'react-router-dom'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Bot, Home, Users, TrendingUp, MapPin, Zap, Shield, Clock } from 'lucide-react'
import KribLogo from '../assets/krib-logo.svg'

export function Homepage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen krib-homepage-background">
      {/* Hero Section */}
      <div className="relative w-full min-h-screen flex items-center justify-center overflow-hidden">
        {/* Dubai Skyline Background */}
        <div 
          className="absolute inset-0 w-full h-full"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1518684079-3c830dcef090?ixlib=rb-4.0.3&auto=format&fit=crop&w=2340&q=80')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center bottom',
            backgroundRepeat: 'no-repeat',
            backgroundColor: '#f8f9fa', // Fallback color
            minHeight: '100vh',
            width: '100%',
            height: '100%'
          }}
        >
          {/* Enhanced overlay for better text readability */}
          <div className="absolute inset-0 bg-gradient-to-b from-white/70 via-white/50 to-white/30"></div>
          
          {/* Subtle Dubai-inspired accent elements */}
          <div className="absolute top-20 right-20 w-32 h-32 bg-krib-lime-muted opacity-10 transform rotate-45 rounded-lg z-15"></div>
          <div className="absolute bottom-40 left-16 w-24 h-24 bg-krib-lime-muted opacity-10 transform rotate-12 rounded-lg z-15"></div>
          <div className="absolute top-1/3 left-1/4 w-16 h-16 bg-krib-lime-muted opacity-10 rounded-full z-15"></div>
        </div>

        {/* Main Content */}
        <div className="relative z-20 container mx-auto px-6 text-center">
          <div className="max-w-4xl mx-auto bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
            {/* Logo Area */}
            <div className="mb-8">
              <div className="inline-flex items-center justify-center mb-6">
                <img 
                  src={KribLogo} 
                  alt="Krib AI Logo" 
                  className="h-16 w-auto filter drop-shadow-lg"
                />
              </div>
              <h1 className="text-5xl md:text-6xl font-bold text-krib-black mb-4 hero-text-shadow">
                Krib <span className="text-krib-lime-dark hero-text-shadow">AI</span>
              </h1>
            </div>

            {/* Main Headline */}
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6 leading-tight hero-text-shadow">
              Your AI-Powered Real Estate Partner in the UAE
            </h2>
            
            <p className="text-xl text-gray-700 mb-8 max-w-3xl mx-auto leading-relaxed hero-text-shadow">
              Experience the future of property management with our intelligent platform. 
              From finding your dream home to maximizing rental income, Krib AI makes real estate effortless.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
              <Button 
                onClick={() => navigate('/auth')}
                className="krib-button-primary text-lg px-8 py-4 h-auto"
              >
                Get Started
                <Bot className="ml-2 w-5 h-5" />
              </Button>
              <Button 
                variant="outline" 
                className="text-lg px-8 py-4 h-auto border-krib-lime-dark hover:bg-krib-lime-muted"
              >
                Learn More
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h3 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
              How Krib AI Transforms Your Real Estate Experience
            </h3>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Powered by advanced AI technology, designed for the UAE market
            </p>
          </div>

          {/* Two Main Value Propositions */}
          <div className="grid md:grid-cols-2 gap-12 mb-20">
            {/* For Customers */}
            <Card className="krib-card p-8 text-center">
              <div className="w-16 h-16 bg-krib-lime-muted rounded-full flex items-center justify-center mx-auto mb-6">
                <Users className="w-8 h-8 text-krib-black" />
              </div>
              <h4 className="text-2xl font-bold text-gray-800 mb-4">
                Your Personal AI Realtor
              </h4>
              <p className="text-gray-600 text-lg mb-6">
                Meet your intelligent property assistant that understands your needs, 
                preferences, and budget to find the perfect home in Dubai, Abu Dhabi, and across the UAE.
              </p>
              <ul className="text-left space-y-3 text-gray-600">
                <li className="flex items-center">
                  <MapPin className="w-5 h-5 text-krib-lime-dark mr-3 flex-shrink-0" />
                  <span>Smart location matching across all 7 Emirates</span>
                </li>
                <li className="flex items-center">
                  <TrendingUp className="w-5 h-5 text-krib-lime-dark mr-3 flex-shrink-0" />
                  <span>AI-powered price predictions and market insights</span>
                </li>
                <li className="flex items-center">
                  <Zap className="w-5 h-5 text-krib-lime-dark mr-3 flex-shrink-0" />
                  <span>Instant property recommendations based on your lifestyle</span>
                </li>
              </ul>
            </Card>

            {/* For Hosts */}
            <Card className="krib-card p-8 text-center">
              <div className="w-16 h-16 bg-krib-lime-muted rounded-full flex items-center justify-center mx-auto mb-6">
                <Home className="w-8 h-8 text-krib-black" />
              </div>
              <h4 className="text-2xl font-bold text-gray-800 mb-4">
                Effortless Property Management
              </h4>
              <p className="text-gray-600 text-lg mb-6">
                Let AI handle the heavy lifting while you focus on what matters. 
                From listing optimization to guest communication, we've got you covered.
              </p>
              <ul className="text-left space-y-3 text-gray-600">
                <li className="flex items-center">
                  <Bot className="w-5 h-5 text-krib-lime-dark mr-3 flex-shrink-0" />
                  <span>AI-generated property descriptions that convert</span>
                </li>
                <li className="flex items-center">
                  <TrendingUp className="w-5 h-5 text-krib-lime-dark mr-3 flex-shrink-0" />
                  <span>Dynamic pricing optimization for maximum revenue</span>
                </li>
                <li className="flex items-center">
                  <Clock className="w-5 h-5 text-krib-lime-dark mr-3 flex-shrink-0" />
                  <span>Automated booking management and guest support</span>
                </li>
              </ul>
            </Card>
          </div>

          {/* AI Features Grid */}
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-krib-lime-muted rounded-lg flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-6 h-6 text-krib-black" />
              </div>
              <h5 className="text-lg font-semibold text-gray-800 mb-2">UAE Market Intelligence</h5>
              <p className="text-gray-600">
                Deep understanding of local markets from Dubai Marina to Abu Dhabi's Corniche
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-krib-lime-muted rounded-lg flex items-center justify-center mx-auto mb-4">
                <Shield className="w-6 h-6 text-krib-black" />
              </div>
              <h5 className="text-lg font-semibold text-gray-800 mb-2">Secure & Trusted</h5>
              <p className="text-gray-600">
                Enterprise-grade security with full compliance to UAE regulations
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-krib-lime-muted rounded-lg flex items-center justify-center mx-auto mb-4">
                <Zap className="w-6 h-6 text-krib-black" />
              </div>
              <h5 className="text-lg font-semibold text-gray-800 mb-2">Lightning Fast</h5>
              <p className="text-gray-600">
                Get instant results with our AI-powered search and recommendation engine
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-krib-lime-muted to-krib-gray-light">
        <div className="container mx-auto px-6 text-center">
          <h3 className="text-3xl md:text-4xl font-bold text-gray-800 mb-6">
            Ready to Experience the Future of Real Estate?
          </h3>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Join thousands of UAE property owners and buyers who trust Krib AI for their real estate needs.
          </p>
          <Button 
            onClick={() => navigate('/auth')}
            size="lg"
            className="krib-button-primary text-lg px-8 py-4 h-auto"
          >
            Start Your Journey
            <Bot className="ml-2 w-5 h-5" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-6 text-center">
          <div className="flex items-center justify-center mb-6">
            <div className="w-10 h-10 bg-krib-lime-dark rounded-lg flex items-center justify-center mr-3">
              <Home className="w-6 h-6 text-krib-black" />
            </div>
            <span className="text-2xl font-bold">Krib AI</span>
          </div>
          <p className="text-gray-400 mb-4">
            Transforming real estate across the UAE with artificial intelligence
          </p>
          <p className="text-gray-500 text-sm">
            © 2025 Krib AI. All rights reserved. | Dubai, UAE
          </p>
        </div>
      </footer>
    </div>
  )
}
