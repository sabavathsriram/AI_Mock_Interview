import React, { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Send,
  SkipForward,
  Clock,
  Mic,
  MicOff,
  Volume2,
  ChevronDown,
  AlertCircle,
  CheckCircle,
  Zap,
} from 'lucide-react'
import { Button } from '@/components/Button'
import { Card, CardBody } from '@/components/Card'
import { Badge } from '@/components/Badge'
import './Interview.css'

type AIState = 'thinking' | 'asking' | 'listening' | 'evaluating' | 'generating'

// This page is not currently used in the main flow - use InterviewQuestion page instead
// This is kept as a legacy backup interface
export const Interview: React.FC = () => {
  const { id } = useParams()
  const navigate = useNavigate()

  useEffect(() => {
    // Redirect to the correct interview page
    if (id) {
      navigate(`/interview/${id}/question`)
    } else {
      navigate('/interview/setup')
    }
  }, [id, navigate])

  return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <p>Redirecting to interview...</p>
    </div>
  )
}

Interview.displayName = 'Interview'
