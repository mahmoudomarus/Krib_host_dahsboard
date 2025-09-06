import { useNavigate } from 'react-router-dom'
import { Button } from './ui/button'
import { Card } from './ui/card'
import { Bot, Home, Users, TrendingUp, MapPin, Zap, Shield, Clock } from 'lucide-react'
import KribLogo from '../assets/krib-logo.svg'
import DubaiBg from '../assets/dubai-hero-bg.png'

export function Homepage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen relative">
      {/* Clear Dubai Background */}
      <div 
        className="absolute inset-0 w-full h-full"
        style={{
          backgroundImage: `url(${DubaiBg})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundColor: '#f8f9fa' // Fallback color
        }}
      >
        {/* Light overlay for text readability without blur */}
        <div className="absolute inset-0 bg-black/20"></div>
      </div>

      {/* Navigation Bar */}
      <nav className="relative z-30 flex items-center justify-between p-6">
        {/* Logo */}
        <div className="flex items-center">
          <img 
            src={KribLogo} 
            alt="Krib AI Logo" 
            className="h-10 w-auto filter drop-shadow-lg"
          />
          <span className="ml-3 text-2xl font-bold text-white drop-shadow-lg">
            Krib <span className="text-krib-lime">AI</span>
          </span>
        </div>
        
        {/* Navigation Buttons */}
        <div className="flex items-center space-x-4">
          <Button 
            variant="ghost" 
            onClick={() => navigate('/auth')}
            className="text-white hover:bg-white/20 hover:text-white border border-white/30 backdrop-blur-sm"
          >
            Sign In
          </Button>
          <Button 
            onClick={() => navigate('/auth')}
            className="bg-krib-lime hover:bg-krib-lime-dark text-krib-black font-semibold px-6 shadow-lg"
          >
            Get Started
          </Button>
        </div>
      </nav>

      {/* Hero Content */}
      <div className="relative z-20 flex items-center justify-center min-h-[calc(100vh-120px)]">
        <div className="container mx-auto px-6 text-center">
          <div className="max-w-4xl mx-auto">
            {/* Main Title */}
            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 hero-text-shadow">
              Smart Real Estate
              <br />
              <span className="text-krib-lime hero-text-shadow">Powered by AI</span>
            </h1>

            {/* Subtitle and Description */}
            <p className="text-xl md:text-2xl text-white/90 mb-8 hero-text-shadow">
              Revolutionizing property management with intelligent automation
            </p>
            <p className="text-lg text-white/80 mb-12 leading-relaxed hero-text-shadow max-w-3xl mx-auto">
              From smart pricing to automated tenant screening, Krib AI transforms how you manage properties in the UAE market.
            </p>

            {/* Call-to-Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Button 
                size="lg" 
                onClick={() => navigate('/auth')}
                className="bg-krib-lime hover:bg-krib-lime-dark text-krib-black font-semibold text-lg px-8 py-4 shadow-xl"
              >
                Start Free Trial
              </Button>
              <Button 
                variant="outline" 
                size="lg" 
                onClick={() => navigate('/auth')}
                className="border-white text-white hover:bg-white hover:text-krib-black text-lg px-8 py-4 backdrop-blur-sm"
              >
                Watch Demo
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative z-20 py-16 bg-white/10 backdrop-blur-sm">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 hero-text-shadow">
              Why Choose Krib AI?
            </h2>
            <p className="text-lg text-white/80 max-w-2xl mx-auto hero-text-shadow">
              Experience the future of property management with our cutting-edge AI technology
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 mb-16">
            <Card className="p-8 text-center bg-white/10 backdrop-blur-sm border-white/20 hover:bg-white/20 transition-all duration-300">
              <div className="w-16 h-16 bg-krib-lime rounded-full flex items-center justify-center mx-auto mb-6">
                <Zap className="w-8 h-8 text-krib-black" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Smart Automation</h3>
              <p className="text-white/80">
                Automate repetitive tasks and focus on growing your portfolio
              </p>
            </Card>

            <Card className="p-8 text-center bg-white/10 backdrop-blur-sm border-white/20 hover:bg-white/20 transition-all duration-300">
              <div className="w-16 h-16 bg-krib-lime rounded-full flex items-center justify-center mx-auto mb-6">
                <Shield className="w-8 h-8 text-krib-black" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">UAE Market Expert</h3>
              <p className="text-white/80">
                Built specifically for the UAE real estate market dynamics
              </p>
            </Card>

            <Card className="p-8 text-center bg-white/10 backdrop-blur-sm border-white/20 hover:bg-white/20 transition-all duration-300">
              <div className="w-16 h-16 bg-krib-lime rounded-full flex items-center justify-center mx-auto mb-6">
                <Clock className="w-8 h-8 text-krib-black" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Save Time</h3>
              <p className="text-white/80">
                Reduce property management time by up to 70% with AI
              </p>
            </Card>
          </div>

          {/* Final CTA */}
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-4 hero-text-shadow">
              Ready to Transform Your Property Business?
            </h3>
            <Button 
              size="lg" 
              onClick={() => navigate('/auth')}
              className="bg-krib-lime hover:bg-krib-lime-dark text-krib-black font-semibold text-lg px-8 py-4 shadow-xl"
            >
              Get Started Today
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}