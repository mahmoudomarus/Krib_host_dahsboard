import { useState } from "react"
import { User, Mail, Lock, Eye, EyeOff, ArrowRight } from "lucide-react"
import KribLogo from "../assets/krib-logo.svg"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Input } from "./ui/input"
import { Label } from "./ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { Separator } from "./ui/separator"
import { useApp } from "../contexts/AppContext"

export function AuthForm() {
  const { signIn, signUp, signInWithGoogle, isLoading } = useApp()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState("")
  const [activeTab, setActiveTab] = useState("signin")
  
  // Sign In Form State
  const [signInData, setSignInData] = useState({
    email: "",
    password: ""
  })
  
  // Sign Up Form State
  const [signUpData, setSignUpData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: ""
  })

  const handleSignIn = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError("")

    try {
      await signIn(signInData.email, signInData.password)
      // signIn will throw an error if it fails, so reaching here means success
    } catch (error) {
      setError("An error occurred during sign in. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError("")

    if (signUpData.password !== signUpData.confirmPassword) {
      setError("Passwords do not match.")
      setIsSubmitting(false)
      return
    }

    if (signUpData.password.length < 6) {
      setError("Password must be at least 6 characters long.")
      setIsSubmitting(false)
      return
    }

    try {
      await signUp(signUpData.email, signUpData.password, signUpData.name)
      // signUp will throw an error if it fails, so reaching here means success
    } catch (error) {
      setError("An error occurred during sign up. Please try again.")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleGoogleSignIn = async () => {
    setIsSubmitting(true)
    setError("")

    try {
      await signInWithGoogle()
      // signInWithGoogle will throw an error if it fails, so reaching here means success
    } catch (error: any) {
      if (error.message.includes('Google authentication is not properly configured')) {
        setError("Google authentication needs to be configured in your Supabase project. Please see the setup instructions below.")
      } else {
        setError("An error occurred during Google sign-in. Please try again.")
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <div className="animate-spin h-8 w-8 border-2 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bauhaus-auth-background flex">
      {/* Swiss Bauhaus Grid System */}
      <div className="bauhaus-grid-overlay"></div>
      
      {/* Left Side - Geometric Design Elements */}
      <div className="hidden lg:flex lg:w-1/2 xl:w-3/5 relative bauhaus-left-panel">
        {/* Large Red Square - Bauhaus signature element */}
        <div className="bauhaus-red-square"></div>
        
        {/* Black Typography Block */}
        <div className="bauhaus-text-block">
          <div className="bauhaus-title">KRIB</div>
          <div className="bauhaus-subtitle">AI PROPERTY MANAGEMENT</div>
          <div className="bauhaus-line"></div>
          <div className="bauhaus-tagline">
            FORM FOLLOWS<br/>
            FUNCTION
          </div>
        </div>
        
        {/* Geometric Elements */}
        <div className="bauhaus-circle"></div>
        <div className="bauhaus-triangle"></div>
        <div className="bauhaus-small-square"></div>
        
        {/* Grid Numbers - Bauhaus style */}
        <div className="bauhaus-grid-numbers">
          <span className="bauhaus-number">01</span>
          <span className="bauhaus-number">02</span>
          <span className="bauhaus-number">03</span>
        </div>
      </div>
      
      {/* Right Side - Authentication Form */}
      <div className="w-full lg:w-1/2 xl:w-2/5 flex items-center justify-center p-8 bauhaus-form-area">
        <div className="w-full max-w-md space-y-8">
          {/* Header */}
          <div className="bauhaus-form-header">
            <div className="bauhaus-logo-section">
              <div className="bauhaus-logo-square">
                <img src={KribLogo} alt="Krib" className="h-8 w-8" />
              </div>
              <div className="bauhaus-system-text">SYSTEM</div>
            </div>
            <h1 className="bauhaus-main-title">ACCESS</h1>
            <div className="bauhaus-red-line"></div>
          </div>
          
          {/* Mode Selector - Bauhaus Style */}
          <div className="bauhaus-mode-selector">
            <div className="bauhaus-tabs">
              <button 
                onClick={() => setActiveTab("signin")}
                className={`bauhaus-tab ${activeTab === "signin" ? "bauhaus-tab-active" : ""}`}
              >
                SIGN IN
              </button>
              <button 
                onClick={() => setActiveTab("signup")}
                className={`bauhaus-tab ${activeTab === "signup" ? "bauhaus-tab-active" : ""}`}
              >
                REGISTER
              </button>
            </div>
            <div className="bauhaus-tab-indicator"></div>
          </div>

          {error && (
            <div className="bauhaus-error">
              <div className="bauhaus-error-symbol">!</div>
              <div className="bauhaus-error-text">{error}</div>
            </div>
          )}

          <Tabs value={activeTab} onValueChange={setActiveTab} className="bauhaus-form-container">
            {/* Bauhaus Separator */}
            <div className="bauhaus-separator">
              <div className="bauhaus-separator-line"></div>
              <div className="bauhaus-separator-text">AUTHENTICATION</div>
              <div className="bauhaus-separator-line"></div>
            </div>
            
            <TabsContent value="signin">
              <form onSubmit={handleSignIn} className="bauhaus-form">
                {/* Email Field */}
                <div className="bauhaus-field-group">
                  <div className="bauhaus-field-label">
                    <span>01</span>
                    <span>EMAIL</span>
                  </div>
                  <div className="bauhaus-input-container">
                    <Mail className="bauhaus-input-icon" />
                    <Input
                      id="signin-email"
                      type="email"
                      placeholder="your.email@domain.com"
                      className="bauhaus-input"
                      value={signInData.email}
                      onChange={(e) => setSignInData(prev => ({ ...prev, email: e.target.value }))}
                      required
                    />
                    <div className="bauhaus-input-line"></div>
                  </div>
                </div>
                
                {/* Password Field */}
                <div className="bauhaus-field-group">
                  <div className="bauhaus-field-label">
                    <span>02</span>
                    <span>PASSWORD</span>
                  </div>
                  <div className="bauhaus-input-container">
                    <Lock className="bauhaus-input-icon" />
                    <Input
                      id="signin-password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••••••"
                      className="bauhaus-input"
                      value={signInData.password}
                      onChange={(e) => setSignInData(prev => ({ ...prev, password: e.target.value }))}
                      required
                    />
                    <button
                      type="button"
                      className="bauhaus-input-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                    <div className="bauhaus-input-line"></div>
                  </div>
                </div>
                
                {/* Submit Button */}
                <div className="bauhaus-action-section">
                  <button 
                    type="submit" 
                    className="bauhaus-primary-button"
                    disabled={isSubmitting}
                  >
                    <span className="bauhaus-button-text">
                      {isSubmitting ? "AUTHENTICATING" : "ACCESS SYSTEM"}
                    </span>
                    <ArrowRight className="bauhaus-button-icon" />
                    <div className="bauhaus-button-bg"></div>
                  </button>
                </div>
              </form>
            </TabsContent>
            
            <TabsContent value="signup">
              <form onSubmit={handleSignUp} className="bauhaus-form">
                {/* Name Field */}
                <div className="bauhaus-field-group">
                  <div className="bauhaus-field-label">
                    <span>01</span>
                    <span>FULL NAME</span>
                  </div>
                  <div className="bauhaus-input-container">
                    <User className="bauhaus-input-icon" />
                    <Input
                      id="signup-name"
                      type="text"
                      placeholder="john.doe"
                      className="bauhaus-input"
                      value={signUpData.name}
                      onChange={(e) => setSignUpData(prev => ({ ...prev, name: e.target.value }))}
                      required
                    />
                    <div className="bauhaus-input-line"></div>
                  </div>
                </div>
                
                {/* Email Field */}
                <div className="bauhaus-field-group">
                  <div className="bauhaus-field-label">
                    <span>02</span>
                    <span>EMAIL</span>
                  </div>
                  <div className="bauhaus-input-container">
                    <Mail className="bauhaus-input-icon" />
                    <Input
                      id="signup-email"
                      type="email"
                      placeholder="john.doe@company.com"
                      className="bauhaus-input"
                      value={signUpData.email}
                      onChange={(e) => setSignUpData(prev => ({ ...prev, email: e.target.value }))}
                      required
                    />
                    <div className="bauhaus-input-line"></div>
                  </div>
                </div>
                
                {/* Password Field */}
                <div className="bauhaus-field-group">
                  <div className="bauhaus-field-label">
                    <span>03</span>
                    <span>PASSWORD</span>
                  </div>
                  <div className="bauhaus-input-container">
                    <Lock className="bauhaus-input-icon" />
                    <Input
                      id="signup-password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••••••"
                      className="bauhaus-input"
                      value={signUpData.password}
                      onChange={(e) => setSignUpData(prev => ({ ...prev, password: e.target.value }))}
                      required
                    />
                    <button
                      type="button"
                      className="bauhaus-input-toggle"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                    <div className="bauhaus-input-line"></div>
                  </div>
                </div>
                
                {/* Confirm Password Field */}
                <div className="bauhaus-field-group">
                  <div className="bauhaus-field-label">
                    <span>04</span>
                    <span>CONFIRM</span>
                  </div>
                  <div className="bauhaus-input-container">
                    <Lock className="bauhaus-input-icon" />
                    <Input
                      id="signup-confirm-password"
                      type={showPassword ? "text" : "password"}
                      placeholder="••••••••••••"
                      className="bauhaus-input"
                      value={signUpData.confirmPassword}
                      onChange={(e) => setSignUpData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                      required
                    />
                    <div className="bauhaus-input-line"></div>
                  </div>
                </div>
                
                {/* Submit Button */}
                <div className="bauhaus-action-section">
                  <button 
                    type="submit" 
                    className="bauhaus-primary-button"
                    disabled={isSubmitting}
                  >
                    <span className="bauhaus-button-text">
                      {isSubmitting ? "CREATING ACCOUNT" : "CREATE ACCOUNT"}
                    </span>
                    <ArrowRight className="bauhaus-button-icon" />
                    <div className="bauhaus-button-bg"></div>
                  </button>
                </div>
              </form>
            </TabsContent>
          </Tabs>
          
          {/* Alternative Access Method */}
          <div className="bauhaus-alternative-access">
            <div className="bauhaus-separator">
              <div className="bauhaus-separator-line"></div>
              <div className="bauhaus-separator-text">OR</div>
              <div className="bauhaus-separator-line"></div>
            </div>
            
            <button 
              onClick={handleGoogleSignIn}
              disabled={isSubmitting}
              className="bauhaus-google-button"
            >
              <div className="bauhaus-google-icon">
                <svg className="h-5 w-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
              </div>
              <span className="bauhaus-google-text">
                {isSubmitting ? "CONNECTING..." : "GOOGLE ACCESS"}
              </span>
            </button>
          </div>
          
          {/* Debug Information */}
          {error.includes('Google authentication needs to be configured') && (
            <div className="bauhaus-debug-info">
              <div className="bauhaus-debug-title">CONFIGURATION REQUIRED</div>
              <div className="bauhaus-debug-text">
                Configure Google OAuth in Supabase Dashboard
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}