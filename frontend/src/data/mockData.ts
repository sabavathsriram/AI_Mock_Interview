/**
 * Centralized Mock Data
 * All mock data for the application in one place for easy replacement with real API data
 */

// ============================================================================
// USERS
// ============================================================================

export const mockCurrentUser = {
  id: 'user_001',
  name: 'Sarah Anderson',
  email: 'sarah.anderson@example.com',
  role: 'candidate' as const,
  joinDate: '2024-01-15',
  targetRole: 'Senior Software Engineer',
  experienceLevel: 'Mid-Level',
  preferredInterviewType: 'Technical',
  skills: ['Python', 'JavaScript', 'React', 'System Design'],
}

// ============================================================================
// RESUMES
// ============================================================================

export const mockResumes = [
  {
    id: 'resume_001',
    filename: 'Sarah_Anderson_Resume_2024.pdf',
    fileType: 'pdf',
    fileSize: 245000,
    uploadedDate: new Date('2024-01-15'),
    processingStatus: 'completed' as const,
    analysisStatus: 'completed' as const,
    isPrimary: true,
    extractedText: 'Senior Software Engineer with 5 years of experience...',
  },
  {
    id: 'resume_002',
    filename: 'Sarah_Anderson_Resume_v2.docx',
    fileType: 'docx',
    fileSize: 125000,
    uploadedDate: new Date('2024-02-10'),
    processingStatus: 'completed' as const,
    analysisStatus: 'completed' as const,
    isPrimary: false,
    extractedText: 'Full Stack Developer with expertise in modern web technologies...',
  },
]

export const mockResumeAnalysis = {
  resumeId: 'resume_001',
  extractedAt: new Date('2024-01-15'),
  candidateOverview: {
    fullName: 'Sarah Anderson',
    email: 'sarah.anderson@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    headline: 'Senior Software Engineer | Full Stack Developer',
    summary: 'Experienced software engineer with 5+ years building scalable web applications.',
  },
  education: [
    {
      degree: 'Bachelor of Science',
      field: 'Computer Science',
      institution: 'UC Berkeley',
      graduationYear: 2019,
      gpa: 3.8,
    },
  ],
  experience: [
    {
      title: 'Senior Software Engineer',
      company: 'TechCorp Inc.',
      duration: '2 years',
      startDate: new Date('2022-03-01'),
      endDate: new Date('2024-01-31'),
      description: 'Led development of customer-facing features, mentored junior developers',
      achievements: [
        'Reduced API response time by 40%',
        'Implemented microservices architecture',
        'Mentored 3 junior developers',
      ],
    },
    {
      title: 'Software Engineer',
      company: 'StartupXYZ',
      duration: '3 years',
      startDate: new Date('2019-06-01'),
      endDate: new Date('2022-02-28'),
      description: 'Built MVP and early product features',
      achievements: ['Grew user base to 100k', 'Implemented CI/CD pipeline'],
    },
  ],
  projects: [
    {
      title: 'E-commerce Platform',
      description: 'Built scalable e-commerce platform handling 1M+ transactions',
      technologies: ['React', 'Node.js', 'PostgreSQL', 'AWS'],
      link: 'https://example.com',
    },
  ],
  skills: {
    programming: ['Python', 'JavaScript', 'TypeScript', 'Go', 'SQL'],
    frameworks: ['React', 'Vue.js', 'Node.js', 'Django', 'FastAPI'],
    databases: ['PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch'],
    cloud: ['AWS', 'Docker', 'Kubernetes', 'CI/CD'],
    tools: ['Git', 'GitHub', 'Jira', 'Figma', 'VS Code'],
  },
  certifications: [
    {
      name: 'AWS Solutions Architect Associate',
      issuer: 'Amazon',
      issuedDate: new Date('2023-06-15'),
      expiryDate: new Date('2026-06-15'),
    },
    {
      name: 'Google Cloud Professional Data Engineer',
      issuer: 'Google',
      issuedDate: new Date('2023-03-20'),
    },
  ],
  primaryDomains: ['Backend Development', 'System Design', 'DevOps'],
  secondaryDomains: ['Frontend Development', 'Database Design'],
  strengths: [
    'Strong system design skills',
    'Full stack development capability',
    'Leadership and mentoring',
    'DevOps and infrastructure knowledge',
  ],
  skillGaps: ['Mobile Development', 'Machine Learning', 'Blockchain'],
}

// ============================================================================
// INTERVIEWS
// ============================================================================

export const mockInterviews = [
  {
    id: 'interview_001',
    type: 'Technical' as const,
    difficulty: 'Hard' as 'Hard' | 'Easy' | 'Medium',
    startDate: new Date('2024-02-01T10:00:00'),
    endDate: new Date('2024-02-01T10:45:00'),
    duration: 45,
    status: 'completed' as const,
    score: 78,
    skillEvaluated: 'System Design',
    questionsAsked: 12,
    correctAnswers: 9,
  },
  {
    id: 'interview_002',
    type: 'Behavioral' as const,
    difficulty: 'Medium' as const,
    startDate: new Date('2024-02-05T14:00:00'),
    endDate: new Date('2024-02-05T14:30:00'),
    duration: 30,
    status: 'completed' as const,
    score: 85,
    skillEvaluated: 'Communication',
    questionsAsked: 8,
    correctAnswers: 7,
  },
  {
    id: 'interview_003',
    type: 'Coding' as const,
    difficulty: 'Hard' as const,
    startDate: new Date('2024-02-10T11:00:00'),
    endDate: new Date('2024-02-10T12:15:00'),
    duration: 75,
    status: 'completed' as const,
    score: 72,
    skillEvaluated: 'Data Structures',
    questionsAsked: 3,
    correctAnswers: 2,
  },
]

export const mockInterviewResults = {
  interviewId: 'interview_001',
  totalScore: 78,
  sections: [
    {
      name: 'Technical Knowledge',
      score: 85,
      maxScore: 100,
      description: 'Understanding of core concepts',
    },
    {
      name: 'Problem Solving',
      score: 75,
      maxScore: 100,
      description: 'Approach to solving problems',
    },
    {
      name: 'Communication',
      score: 72,
      maxScore: 100,
      description: 'Clarity of explanation',
    },
    {
      name: 'Code Quality',
      score: 80,
      maxScore: 100,
      description: 'Quality and efficiency',
    },
  ],
  strengths: [
    'Excellent understanding of design patterns',
    'Clear communication of approach',
    'Considers edge cases',
  ],
  areasForImprovement: [
    'Could optimize space complexity further',
    'Try to explain assumptions upfront',
  ],
  recommendations: [
    'Practice more medium-level design problems',
    'Focus on API design patterns',
    'Improve time management during interviews',
  ],
  questionReviews: [
    {
      questionId: 'q_001',
      question: 'Design a URL shortener service',
      candidateAnswer: 'Created hash-based solution with load balancing',
      score: 85,
      strengths: ['Considered scalability', 'Discussed trade-offs'],
      improvements: ['Could discuss caching strategy'],
      concept: 'System Design',
    },
  ],
}

// ============================================================================
// JOB DESCRIPTIONS
// ============================================================================

export const mockJobDescriptions = [
  {
    id: 'job_001',
    title: 'Senior Software Engineer',
    company: 'TechCorp Inc.',
    savedDate: new Date('2024-02-01'),
    requiredSkills: [
      'Python',
      'JavaScript',
      'React',
      'Node.js',
      'System Design',
      'SQL',
    ],
    preferredSkills: [
      'TypeScript',
      'AWS',
      'Docker',
      'Kubernetes',
      'GraphQL',
    ],
    experienceLevel: 'Senior',
    yearsRequired: 5,
    description: 'Looking for a senior engineer to lead our platform development...',
  },
]

export const mockJobAlignment = {
  resumeSkills: ['Python', 'JavaScript', 'React', 'SQL', 'AWS', 'Docker'],
  requiredSkills: ['Python', 'JavaScript', 'React', 'Node.js', 'System Design', 'SQL'],
  preferredSkills: ['TypeScript', 'AWS', 'Docker', 'Kubernetes', 'GraphQL'],
  matchingRequired: ['Python', 'JavaScript', 'React', 'SQL'],
  missingRequired: ['Node.js', 'System Design'],
  matchingPreferred: ['AWS', 'Docker'],
  missingPreferred: ['TypeScript', 'Kubernetes', 'GraphQL'],
  alignmentScore: 67,
}

// ============================================================================
// INTERVIEW QUESTIONS
// ============================================================================

export const mockInterviewQuestions = [
  {
    id: 'q_001',
    text: 'Design a URL shortener service that can handle millions of requests.',
    category: 'System Design',
    difficulty: 'Hard' as const,
    followUp: [
      'How would you handle conflicts?',
      'What about analytics?',
    ],
  },
  {
    id: 'q_002',
    text: 'Implement a LRU cache in Python.',
    category: 'Data Structures',
    difficulty: 'Medium' as const,
  },
  {
    id: 'q_003',
    text: 'Tell me about a time you had to debug a production issue.',
    category: 'Behavioral',
    difficulty: 'Medium' as const,
  },
]

// ============================================================================
// SKILLS
// ============================================================================

export const mockSkills = [
  {
    name: 'Python',
    category: 'Programming Language',
    level: 'Advanced' as 'Advanced' | 'Beginner' | 'Intermediate',
    confidence: 94,
    lastAssessed: new Date('2024-02-01'),
    evidenceCount: 15,
    trend: 'stable' as const,
  },
  {
    name: 'JavaScript',
    category: 'Programming Language',
    level: 'Advanced' as const,
    confidence: 90,
    lastAssessed: new Date('2024-02-01'),
    evidenceCount: 12,
    trend: 'improving' as const,
  },
  {
    name: 'React',
    category: 'Frontend Framework',
    level: 'Intermediate' as const,
    confidence: 78,
    lastAssessed: new Date('2024-02-01'),
    evidenceCount: 8,
    trend: 'stable' as const,
  },
  {
    name: 'System Design',
    category: 'Core Competency',
    level: 'Intermediate' as const,
    confidence: 72,
    lastAssessed: new Date('2024-02-01'),
    evidenceCount: 5,
    trend: 'improving' as const,
  },
  {
    name: 'Data Structures',
    category: 'Core Competency',
    level: 'Advanced' as const,
    confidence: 85,
    lastAssessed: new Date('2024-02-01'),
    evidenceCount: 18,
    trend: 'stable' as const,
  },
  {
    name: 'Communication',
    category: 'Soft Skill',
    level: 'Intermediate' as const,
    confidence: 81,
    lastAssessed: new Date('2024-02-01'),
    evidenceCount: 7,
    trend: 'improving' as const,
  },
]

// ============================================================================
// LEARNING RESOURCES
// ============================================================================

export const mockLearningResources = [
  {
    id: 'resource_001',
    title: 'System Design Interview Guide',
    description: 'Comprehensive guide to cracking system design interviews',
    type: 'Article',
    difficulty: 'Hard',
    duration: 45,
    skillTags: ['System Design'],
    category: 'System Design',
    link: 'https://example.com',
  },
  {
    id: 'resource_002',
    title: 'Data Structures Masterclass',
    description: 'Deep dive into essential data structures',
    type: 'Video',
    difficulty: 'Medium',
    duration: 120,
    skillTags: ['Data Structures', 'Algorithms'],
    category: 'DSA',
    link: 'https://example.com',
  },
  {
    id: 'resource_003',
    title: 'React Advanced Patterns',
    description: 'Learn advanced React patterns and hooks',
    type: 'Documentation',
    difficulty: 'Medium',
    duration: 60,
    skillTags: ['React', 'Frontend'],
    category: 'Frontend',
    link: 'https://example.com',
  },
]

export const mockResourceCategories = [
  'DSA',
  'Java',
  'Python',
  'JavaScript',
  'React',
  'Backend',
  'DBMS',
  'OS',
  'CN',
  'OOP',
  'System Design',
  'AI/ML',
  'Cloud',
  'Behavioral Interview',
]

// ============================================================================
// LEARNING ROADMAP
// ============================================================================

export const mockLearningRoadmap = [
  {
    id: 'roadmap_001',
    topic: 'Advanced System Design',
    whyRecommended: 'Your interview showed weakness in system design. Strengthen this skill.',
    currentLevel: 'Intermediate',
    targetLevel: 'Advanced',
    estimatedEffort: '20 hours',
    resources: ['System Design Interview Guide', 'System Design Primer'],
    concepts: ['Scalability', 'Load Balancing', 'Caching', 'Database Design'],
    status: 'In Progress',
  },
  {
    id: 'roadmap_002',
    topic: 'Behavioral Interview Mastery',
    whyRecommended: 'Improve storytelling and communication skills',
    currentLevel: 'Beginner',
    targetLevel: 'Intermediate',
    estimatedEffort: '8 hours',
    resources: ['STAR Method Guide', 'Behavioral Interview Examples'],
    concepts: ['STAR Method', 'Storytelling', 'Conflict Resolution'],
    status: 'Not Started',
  },
]

// ============================================================================
// STATISTICS
// ============================================================================

export const mockStats = {
  totalInterviews: 12,
  averageScore: 78,
  bestScore: 92,
  worstScore: 65,
  interviewsThisMonth: 4,
  completionRate: 100,
  strongestSkill: 'Data Structures',
  weakestSkill: 'System Design',
  improvementTrend: 'positive' as const,
  skillsImproved: 3,
}

export const mockProgressData = [
  { date: '2024-01-01', score: 65 },
  { date: '2024-01-08', score: 68 },
  { date: '2024-01-15', score: 72 },
  { date: '2024-01-22', score: 70 },
  { date: '2024-01-29', score: 75 },
  { date: '2024-02-05', score: 78 },
  { date: '2024-02-12', score: 82 },
]

// ============================================================================
// INTERVIEW SETUP OPTIONS
// ============================================================================

export const interviewTypes = ['Technical', 'HR', 'Behavioral', 'System Design', 'Coding', 'Mixed'] as const
export const interviewDifficulties = ['Easy', 'Medium', 'Hard', 'Adaptive'] as const
export const interviewDurations = [15, 30, 45, 60] as const
export const interviewModes = ['Text', 'Voice', 'Video'] as const

// ============================================================================
// FEATURE FLAGS
// ============================================================================

export const featureFlags = {
  videoInterview: false,
  voiceInterview: true,
  advancedAnalytics: false,
  collaborativeInterview: false,
  customQuestions: false,
}
