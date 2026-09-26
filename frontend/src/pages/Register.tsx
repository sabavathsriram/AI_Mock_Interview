import React, { useState, useMemo } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { User, Mail, Lock, Eye, EyeOff, ArrowRight, Check, X } from 'lucide-react'
import { Button, Input } from '@/components/common'
import { useAuth } from '@/contexts/AuthContext'

const calculatePasswordStrength = (password: string) => {
  let strength = 0
  if (password.length >= 8) strength++
  if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++
  if (password.match(/[0-9]/)) strength++
  if (password.match(/[^a-zA-Z0-9]/)) strength++
  return strength
}

const getPasswordStrengthLabel = (strength: number) => {
  switch (strength) {
    case 0:
    case 1:
      return { label: 'Weak', color: 'text-error-600 dark:text-error-400' }
    case 2:
      return { label: 'Fair', color: 'text-warning-600 dark:text-warning-400' }
    case 3:
      return { label: 'Good', color: 'text-primary-600 dark:text-primary-400' }
    case 4:
      return { label: 'Strong', color: 'text-success-600 dark:text-success-400' }
    default:
      return { label: 'Unknown', color: 'text-dark-600 dark:text-dark-400' }
  }
}

const getPasswordStrengthColor = (strength: number) => {
  switch (strength) {
    case 0:
    case 1:
      return 'bg-error-500'
    case 2:
      return 'bg-warning-500'
    case 3:
      return 'bg-primary-500'
    case 4:
      return 'bg-success-500'
    default:
      return 'bg-dark-300'
  }
}

export const Register: React.FC = () => {
  const navigate = useNavigate()
  const { register, isLoading } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false,
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const passwordStrength = useMemo(() => calculatePasswordStrength(formData.password), [formData.password])
  const strengthLabel = getPasswordStrengthLabel(passwordStrength)

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Full name is required'
    }

    if (!formData.email) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters'
    } else if (passwordStrength < 2) {
      newErrors.password = 'Password is too weak. Add uppercase, numbers, or symbols.'
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
    }

    if (!formData.agreeTerms) {
      newErrors.agreeTerms = 'You must agree to the terms and conditions'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    try {
      await register(formData.name, formData.email, formData.password)
      navigate('/dashboard')
    } catch (error) {
      setErrors({ submit: 'Registration failed. Please try again.' })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-dark-900 dark:to-dark-800 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-secondary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">AI</span>
            </div>
            <span className="font-bold text-lg text-dark-900 dark:text-white">MockInterview</span>
          </Link>

          <h1 className="text-3xl font-bold text-dark-900 dark:text-white mb-2">Create Account</h1>
          <p className="text-dark-600 dark:text-dark-400">Join thousands preparing for interviews</p>
        </div>

        {/* Form Card */}
        <div className="bg-white dark:bg-dark-800 rounded-xl shadow-lg border border-dark-200 dark:border-dark-700 p-8 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div>
              <Input
                label="Full Name"
                type="text"
                placeholder="John Doe"
                icon={<User size={18} />}
                error={errors.name}
                value={formData.name}
                onChange={(e) => {
                  setFormData({ ...formData, name: e.target.value })
                  if (errors.name) setErrors({ ...errors, name: '' })
                }}
              />
            </div>

            {/* Email */}
            <div>
              <Input
                label="Email Address"
                type="email"
                placeholder="you@example.com"
                icon={<Mail size={18} />}
                error={errors.email}
                value={formData.email}
                onChange={(e) => {
                  setFormData({ ...formData, email: e.target.value })
                  if (errors.email) setErrors({ ...errors, email: '' })
                }}
              />
            </div>

            {/* Password */}
            <div>
              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="••••••••"
                icon={
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="text-dark-400 hover:text-dark-600 dark:hover:text-dark-300"
                  >
                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                }
                iconPosition="right"
                error={errors.password}
                value={formData.password}
                onChange={(e) => {
                  setFormData({ ...formData, password: e.target.value })
                  if (errors.password) setErrors({ ...errors, password: '' })
                }}
                helperText="Min 8 chars, mix of uppercase, numbers, symbols"
              />

              {/* Password Strength */}
              {formData.password && (
                <div className="mt-3 space-y-2">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-2 bg-dark-200 dark:bg-dark-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${getPasswordStrengthColor(passwordStrength)}`}
                        style={{ width: `${(passwordStrength / 4) * 100}%` }}
                      />
                    </div>
                    <span className={`text-sm font-semibold ${strengthLabel.color}`}>{strengthLabel.label}</span>
                  </div>

                  {/* Password Requirements */}
                  <div className="space-y-1 text-xs">
                    {[
                      { check: formData.password.length >= 8, label: 'At least 8 characters' },
                      { check: /[A-Z]/.test(formData.password), label: 'Uppercase letter' },
                      { check: /[0-9]/.test(formData.password), label: 'Number' },
                      { check: /[^a-zA-Z0-9]/.test(formData.password), label: 'Symbol (!@#$%)' },
                    ].map((req) => (
                      <div key={req.label} className="flex items-center gap-2 text-dark-600 dark:text-dark-400">
                        {req.check ? (
                          <Check size={14} className="text-success-500" />
                        ) : (
                          <X size={14} className="text-error-500" />
                        )}
                        {req.label}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <Input
                label="Confirm Password"
                type={showConfirmPassword ? 'text' : 'password'}
                placeholder="••••••••"
                icon={
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="text-dark-400 hover:text-dark-600 dark:hover:text-dark-300"
                  >
                    {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                  </button>
                }
                iconPosition="right"
                error={errors.confirmPassword}
                value={formData.confirmPassword}
                onChange={(e) => {
                  setFormData({ ...formData, confirmPassword: e.target.value })
                  if (errors.confirmPassword) setErrors({ ...errors, confirmPassword: '' })
                }}
              />
            </div>

            {/* Terms Checkbox */}
            <div>
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.agreeTerms}
                  onChange={(e) => {
                    setFormData({ ...formData, agreeTerms: e.target.checked })
                    if (errors.agreeTerms) setErrors({ ...errors, agreeTerms: '' })
                  }}
                  className="w-4 h-4 mt-1 rounded border-dark-300 dark:border-dark-600 text-primary-600 focus:ring-primary-500 cursor-pointer"
                />
                <span className="text-sm text-dark-600 dark:text-dark-400">
                  I agree to the{' '}
                  <a href="#" className="text-primary-600 dark:text-primary-400 hover:underline">
                    Terms and Conditions
                  </a>
                  {' '}and{' '}
                  <a href="#" className="text-primary-600 dark:text-primary-400 hover:underline">
                    Privacy Policy
                  </a>
                </span>
              </label>
              {errors.agreeTerms && (
                <p className="mt-1 text-sm text-error-600 dark:text-error-400">{errors.agreeTerms}</p>
              )}
            </div>

            {/* Error Message */}
            {errors.submit && (
              <div className="p-3 bg-error-50 dark:bg-error-900/20 border border-error-200 dark:border-error-700 rounded-lg text-sm text-error-700 dark:text-error-300">
                {errors.submit}
              </div>
            )}

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              isLoading={isLoading}
              icon={!isLoading ? <ArrowRight size={20} /> : undefined}
              iconPosition="right"
              className="mt-6"
            >
              Create Account
            </Button>
          </form>

          {/* Demo Notice */}
          <div className="mt-6 p-3 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-700 rounded-lg text-sm text-primary-700 dark:text-primary-300">
            💡 <strong>Demo:</strong> Fill in all fields to create a test account
          </div>
        </div>

        {/* Login Link */}
        <div className="text-center">
          <p className="text-dark-600 dark:text-dark-400">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

Register.displayName = 'Register'
