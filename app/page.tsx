"use client"

import type React from "react"

import { useState, useRef, useCallback, useEffect } from "react"
import {
  Upload,
  Mic,
  Play,
  Pause,
  Download,
  BookOpen,
  Video,
  FileText,
  Star,
  Clock,
  TrendingUp,
  Zap,
  Brain,
  Target,
  MicOff,
  Volume2,
  VolumeX,
  Bookmark,
  BookmarkCheck,
  Search,
  Share2,
  Copy,
  Check,
  AlertCircle,
  Info,
  X,
  ChevronDown,
  ChevronUp,
  SkipBack,
  SkipForward,
  Settings,
  History,
  RefreshCw,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Alert, AlertDescription } from "@/components/ui/alert"

interface AudioFile extends File {
  duration?: number
  preview?: string
}

interface Concept {
  term: string
  category: string
  relevance: number
  definition?: string
  relatedTerms: string[]
  confidence: number
}

interface Resource {
  id: string
  title: string
  description: string
  type: "document" | "video" | "practice"
  url: string
  relevanceScore: number
  difficulty: string
  duration?: number
  source: string
  credibilityScore: number
  thumbnail?: string
  isBookmarked: boolean
  readingTime?: number
}

interface TranscriptionSegment {
  text: string
  timestamp: number
  confidence: number
  speaker?: string
}

export default function AILearningAid() {
  const [uploadedFiles, setUploadedFiles] = useState<AudioFile[]>([])
  const [currentFileIndex, setCurrentFileIndex] = useState(0)
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const [audioLevel, setAudioLevel] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStep, setProcessingStep] = useState(0)
  const [processingProgress, setProcessingProgress] = useState(0)
  const [transcriptionSegments, setTranscriptionSegments] = useState<TranscriptionSegment[]>([])
  const [editedTranscription, setEditedTranscription] = useState("")
  const [isTranscriptionEdited, setIsTranscriptionEdited] = useState(false)
  const [concepts, setConcepts] = useState<Concept[]>([])
  const [recommendations, setRecommendations] = useState<Resource[]>([])
  const [activeTab, setActiveTab] = useState("upload")
  const [searchQuery, setSearchQuery] = useState("")
  const [filterDifficulty, setFilterDifficulty] = useState("all")
  const [filterType, setFilterType] = useState("all")
  const [sortBy, setSortBy] = useState("relevance")
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [playbackRate, setPlaybackRate] = useState(1)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [showFullTranscription, setShowFullTranscription] = useState(false)
  const [selectedConcepts, setSelectedConcepts] = useState<string[]>([])
  const [conceptViewMode, setConceptViewMode] = useState<"tags" | "map" | "list">("tags")
  const [bookmarkedResources, setBookmarkedResources] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isExporting, setIsExporting] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [sessions, setSessions] = useState<any[]>([])
  const [copiedText, setCopiedText] = useState<string | null>(null)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const audioRef = useRef<HTMLAudioElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const audioLevelIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const handleFileUpload = useCallback(async (files: FileList) => {
    const validFiles: AudioFile[] = []
    const maxSize = 50 * 1024 * 1024 // 50MB
    // Common MIME types for audio uploads
    const supportedFormats = [
      "audio/mp3", // rarely used, some browsers
      "audio/mpeg", // MP3 (most browsers)
      "audio/wav",
      "audio/x-wav",
      "audio/m4a",
      "audio/x-m4a",
      "audio/aac",
      "audio/ogg",
      "audio/webm", // recordings from MediaRecorder
    ]

    for (let i = 0; i < files.length; i++) {
      const file = files[i] as AudioFile

      // Validate file size
      if (file.size > maxSize) {
        setError(`File "${file.name}" is too large. Maximum size is 50MB.`)
        continue
      }

      // Validate file type with MIME + extension fallback
      const lowerName = file.name.toLowerCase()
      const extAllowed = [".mp3", ".wav", ".m4a", ".aac", ".ogg", ".webm"].some((ext) => lowerName.endsWith(ext))
      if (!supportedFormats.includes(file.type) && !extAllowed) {
        setError(`File "${file.name}" is not a supported audio format (type: ${file.type || "unknown"}).`)
        continue
      }

      // Create audio preview
      const audioUrl = URL.createObjectURL(file)
      const audio = new Audio(audioUrl)

      try {
        await new Promise((resolve, reject) => {
          audio.addEventListener("loadedmetadata", () => {
            file.duration = audio.duration
            file.preview = audioUrl
            resolve(null)
          })
          audio.addEventListener("error", reject)
        })

        validFiles.push(file)
      } catch (error) {
        setError(`Failed to load audio file "${file.name}"`)
      }
    }

    if (validFiles.length > 0) {
      setUploadedFiles(validFiles)
      setCurrentFileIndex(0)
      setActiveTab("processing")
      setSuccess(`Successfully uploaded ${validFiles.length} file(s)`)
      // Send first file to backend for analysis
      try {
        await analyzeBackend(validFiles[0])
      } catch (err) {
        setError("Analysis failed. Falling back to demo mode.")
        simulateProcessing()
      }
    }
  }, [])

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        },
      })

      // Set up audio context for level monitoring
      audioContextRef.current = new AudioContext()
      analyserRef.current = audioContextRef.current.createAnalyser()
      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)

      // Start level monitoring
      const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount)
      audioLevelIntervalRef.current = setInterval(() => {
        if (analyserRef.current) {
          analyserRef.current.getByteFrequencyData(dataArray)
          const average = dataArray.reduce((a, b) => a + b) / dataArray.length
          setAudioLevel(average / 255)
        }
      }, 100)

      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: "audio/webm;codecs=opus",
      })

      const chunks: BlobPart[] = []

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data)
        }
      }

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunks, { type: "audio/webm" })
        const file = new File([blob], `recording-${Date.now()}.webm`, { type: "audio/webm" }) as AudioFile
        file.duration = recordingTime
        file.preview = URL.createObjectURL(blob)

        setUploadedFiles([file])
        setCurrentFileIndex(0)
        stream.getTracks().forEach((track) => track.stop())

        if (audioContextRef.current) {
          audioContextRef.current.close()
        }

        if (audioLevelIntervalRef.current) {
          clearInterval(audioLevelIntervalRef.current)
        }

        setActiveTab("processing")
        // Send recording to backend for analysis
        ;(async () => {
          try {
            await analyzeBackend(file)
          } catch (err) {
            setError("Analysis failed. Falling back to demo mode.")
            simulateProcessing()
          }
        })()
      }

      mediaRecorderRef.current.start(1000)
      setIsRecording(true)
      setRecordingTime(0)

      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1)
      }, 1000)
    } catch (error) {
      setError("Failed to access microphone. Please check permissions.")
    }
  }, [recordingTime])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsPaused(false)
      setAudioLevel(0)

      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current)
      }

      if (audioLevelIntervalRef.current) {
        clearInterval(audioLevelIntervalRef.current)
      }
    }
  }, [isRecording])

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume()
        recordingIntervalRef.current = setInterval(() => {
          setRecordingTime((prev) => prev + 1)
        }, 1000)
      } else {
        mediaRecorderRef.current.pause()
        if (recordingIntervalRef.current) {
          clearInterval(recordingIntervalRef.current)
        }
      }
      setIsPaused(!isPaused)
    }
  }, [isRecording, isPaused])

  // Send audio file to backend for analysis
  const analyzeBackend = useCallback(async (file: File) => {
    setIsProcessing(true)
    setProcessingStep(0)
    setProcessingProgress(0)
    setError(null)

    try {
      const form = new FormData()
      form.append("audio", file)

      const res = await fetch("/api/analyze", {
        method: "POST",
        body: form,
      })

      if (!res.ok) {
        throw new Error(`Backend error ${res.status}`)
      }

      const data = await res.json()

      // Map transcript
      const text: string = data?.transcript?.text || ""
      setEditedTranscription(text)

      // Map segments
      const segs = Array.isArray(data?.segments)
        ? (data.segments as any[]).map((s) => ({
            text: String(s.text ?? ""),
            timestamp: Number(s.timestamp ?? 0),
            confidence: Number(s.confidence ?? 0.9),
          }))
        : []
      setTranscriptionSegments(segs)

      // Map concepts
      const conceptItems = Array.isArray(data?.concepts)
        ? (data.concepts as any[]).map((c) => ({
            term: String(c.term ?? ""),
            category: String(c.category ?? "General"),
            relevance: Number(c.relevance ?? 0),
            confidence: Number(c.confidence ?? 0.8),
            relatedTerms: [],
          }))
        : []
      setConcepts(conceptItems)

      // Map recommendations
      const recs = Array.isArray(data?.recommendations)
        ? (data.recommendations as any[]).map((r) => ({
            id: String(r.id ?? crypto.randomUUID()),
            title: String(r.title ?? "Untitled"),
            description: String(r.description ?? ""),
            type: (r.type ?? "document") as any,
            url: String(r.url ?? "#"),
            relevanceScore: Number(r.relevanceScore ?? 0),
            difficulty: String(r.difficulty ?? "beginner"),
            duration: r.duration ? Number(r.duration) : undefined,
            readingTime: r.readingTime ? Number(r.readingTime) : undefined,
            source: String(r.source ?? "Unknown"),
            credibilityScore: Number(r.credibilityScore ?? 90),
            thumbnail: r.thumbnail ?? undefined,
            isBookmarked: Boolean(r.isBookmarked ?? false),
          }))
        : []
      setRecommendations(recs)

      setIsProcessing(false)
      setProcessingProgress(100)
      setActiveTab("results")
      setSuccess("Analysis complete! Your voice note has been processed by the backend.")
    } catch (e: any) {
      setIsProcessing(false)
      setActiveTab("upload")
      throw e
    }
  }, [])

  const simulateProcessing = useCallback(() => {
    setIsProcessing(true)
    setProcessingStep(0)
    setProcessingProgress(0)
    setError(null)

    const steps = [
      { name: "Uploading...", duration: 2000 },
      { name: "Transcribing...", duration: 8000 },
      { name: "Extracting concepts...", duration: 4000 },
      { name: "Finding recommendations...", duration: 3000 },
    ]

    let currentStep = 0
    let currentProgress = 0

    const updateProgress = () => {
      if (currentStep < steps.length) {
        const stepProgress = Math.min(currentProgress + Math.random() * 15, 100)
        setProcessingProgress(stepProgress)

        if (stepProgress >= 100) {
          currentStep++
          setProcessingStep(currentStep)
          currentProgress = 0

          if (currentStep < steps.length) {
            setTimeout(updateProgress, 500)
          } else {
            // Processing complete
            setIsProcessing(false)
            setProcessingProgress(100)

            // Set enhanced mock data
            const mockTranscription =
              "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. Neural networks are inspired by biological neurons and consist of interconnected nodes. Deep learning uses multiple layers to model complex patterns in data. These systems can recognize images, understand speech, and make predictions based on historical data."

            const segments: TranscriptionSegment[] = [
              {
                text: "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
                timestamp: 0,
                confidence: 0.95,
              },
              {
                text: "Neural networks are inspired by biological neurons and consist of interconnected nodes.",
                timestamp: 8.5,
                confidence: 0.92,
              },
              {
                text: "Deep learning uses multiple layers to model complex patterns in data.",
                timestamp: 16.2,
                confidence: 0.88,
              },
              {
                text: "These systems can recognize images, understand speech, and make predictions based on historical data.",
                timestamp: 24.1,
                confidence: 0.94,
              },
            ]

            setTranscriptionSegments(segments)
            setEditedTranscription(mockTranscription)

            setConcepts([
              {
                term: "Machine Learning",
                category: "AI",
                relevance: 95,
                confidence: 0.95,
                definition: "A method of data analysis that automates analytical model building",
                relatedTerms: ["Artificial Intelligence", "Deep Learning", "Neural Networks"],
              },
              {
                term: "Neural Networks",
                category: "AI",
                relevance: 88,
                confidence: 0.92,
                definition: "Computing systems inspired by biological neural networks",
                relatedTerms: ["Machine Learning", "Deep Learning", "Artificial Intelligence"],
              },
              {
                term: "Deep Learning",
                category: "AI",
                relevance: 82,
                confidence: 0.88,
                definition: "Machine learning methods based on artificial neural networks",
                relatedTerms: ["Neural Networks", "Machine Learning", "Pattern Recognition"],
              },
              {
                term: "Algorithms",
                category: "Computer Science",
                relevance: 75,
                confidence: 0.85,
                definition: "Step-by-step procedures for calculations and data processing",
                relatedTerms: ["Programming", "Data Structures", "Computer Science"],
              },
              {
                term: "Data Patterns",
                category: "Statistics",
                relevance: 68,
                confidence: 0.78,
                definition: "Regularities and trends found in datasets",
                relatedTerms: ["Statistics", "Data Analysis", "Pattern Recognition"],
              },
              {
                term: "Pattern Recognition",
                category: "AI",
                relevance: 72,
                confidence: 0.82,
                definition: "The ability to identify regularities in data",
                relatedTerms: ["Machine Learning", "Computer Vision", "Data Patterns"],
              },
            ])

            setRecommendations([
              {
                id: "1",
                title: "Introduction to Machine Learning",
                description: "Comprehensive guide covering ML fundamentals with practical examples and exercises",
                type: "document",
                url: "https://example.com/ml-intro",
                relevanceScore: 95,
                difficulty: "beginner",
                source: "MIT OpenCourseWare",
                credibilityScore: 98,
                readingTime: 45,
                isBookmarked: false,
                thumbnail: "/placeholder-6ur2j.png",
              },
              {
                id: "2",
                title: "Neural Networks Explained",
                description: "Visual explanation of how neural networks work with interactive demonstrations",
                type: "video",
                url: "https://youtube.com/watch?v=example",
                relevanceScore: 90,
                difficulty: "intermediate",
                duration: 15,
                source: "3Blue1Brown",
                credibilityScore: 96,
                isBookmarked: false,
                thumbnail: "/neural-network-visualization.png",
              },
              {
                id: "3",
                title: "Deep Learning Practice Problems",
                description: "Hands-on exercises for deep learning concepts with step-by-step solutions",
                type: "practice",
                url: "https://kaggle.com/learn/deep-learning",
                relevanceScore: 85,
                difficulty: "advanced",
                source: "Kaggle Learn",
                credibilityScore: 94,
                isBookmarked: false,
                thumbnail: "/coding-practice.png",
              },
              {
                id: "4",
                title: "Pattern Recognition in AI",
                description: "Advanced concepts in pattern recognition and their applications in modern AI systems",
                type: "document",
                url: "https://example.com/pattern-recognition",
                relevanceScore: 78,
                difficulty: "advanced",
                source: "Stanford AI Lab",
                credibilityScore: 97,
                readingTime: 60,
                isBookmarked: false,
                thumbnail: "/pattern-recognition-algorithms.png",
              },
              {
                id: "5",
                title: "Building Your First Neural Network",
                description: "Step-by-step tutorial for creating and training your first neural network",
                type: "video",
                url: "https://youtube.com/watch?v=example2",
                relevanceScore: 82,
                difficulty: "beginner",
                duration: 25,
                source: "Sentdex",
                credibilityScore: 89,
                isBookmarked: false,
                thumbnail: "/neural-network-tutorial.png",
              },
              {
                id: "6",
                title: "AI Algorithm Challenges",
                description: "Interactive coding challenges to test your understanding of AI algorithms",
                type: "practice",
                url: "https://example.com/ai-challenges",
                relevanceScore: 76,
                difficulty: "intermediate",
                source: "LeetCode",
                credibilityScore: 91,
                isBookmarked: false,
                thumbnail: "/algorithm-coding-challenges.png",
              },
            ])

            setActiveTab("results")
            setSuccess("Analysis complete! Your voice note has been processed successfully.")
          }
        } else {
          currentProgress += Math.random() * 10
          setTimeout(updateProgress, 200)
        }
      }
    }

    setTimeout(updateProgress, 500)
  }, [])

  const togglePlayback = useCallback(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
      } else {
        audioRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }, [isPlaying])

  const handleTimeUpdate = useCallback(() => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime)
    }
  }, [])

  const handleLoadedMetadata = useCallback(() => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration)
    }
  }, [])

  const seekTo = useCallback((time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time
      setCurrentTime(time)
    }
  }, [])

  const changePlaybackRate = useCallback((rate: number) => {
    if (audioRef.current) {
      audioRef.current.playbackRate = rate
      setPlaybackRate(rate)
    }
  }, [])

  const toggleMute = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.muted = !isMuted
      setIsMuted(!isMuted)
    }
  }, [isMuted])

  const changeVolume = useCallback((newVolume: number) => {
    if (audioRef.current) {
      audioRef.current.volume = newVolume
      setVolume(newVolume)
    }
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragOver(false)
      const files = e.dataTransfer.files
      if (files.length > 0) {
        handleFileUpload(files)
      }
    },
    [handleFileUpload],
  )

  const toggleConceptSelection = useCallback((term: string) => {
    setSelectedConcepts((prev) => (prev.includes(term) ? prev.filter((t) => t !== term) : [...prev, term]))
  }, [])

  const toggleBookmark = useCallback((resourceId: string) => {
    setBookmarkedResources((prev) =>
      prev.includes(resourceId) ? prev.filter((id) => id !== resourceId) : [...prev, resourceId],
    )

    setRecommendations((prev) =>
      prev.map((rec) => (rec.id === resourceId ? { ...rec, isBookmarked: !rec.isBookmarked } : rec)),
    )
  }, [])

  const exportTranscription = useCallback(
    async (format: "txt" | "pdf" | "json") => {
      setIsExporting(true)

      try {
        let content = ""
        let filename = ""
        let mimeType = ""

        switch (format) {
          case "txt":
            content = editedTranscription
            filename = `transcription-${Date.now()}.txt`
            mimeType = "text/plain"
            break
          case "json":
            const exportData = {
              transcription: editedTranscription,
              segments: transcriptionSegments,
              concepts: concepts,
              timestamp: new Date().toISOString(),
            }
            content = JSON.stringify(exportData, null, 2)
            filename = `analysis-${Date.now()}.json`
            mimeType = "application/json"
            break
          case "pdf":
            // Simulate PDF generation
            content = `AI Learning Aid - Transcription Report\n\nDate: ${new Date().toLocaleDateString()}\n\nTranscription:\n${editedTranscription}\n\nKey Concepts:\n${concepts.map((c) => `- ${c.term} (${c.relevance}%)`).join("\n")}`
            filename = `report-${Date.now()}.txt`
            mimeType = "text/plain"
            break
        }

        const blob = new Blob([content], { type: mimeType })
        const url = URL.createObjectURL(blob)
        const a = document.createElement("a")
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)

        setSuccess(`Successfully exported as ${format.toUpperCase()}`)
      } catch (error) {
        setError("Failed to export file")
      } finally {
        setIsExporting(false)
      }
    },
    [editedTranscription, transcriptionSegments, concepts],
  )

  const copyToClipboard = useCallback(async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedText(type)
      setTimeout(() => setCopiedText(null), 2000)
    } catch (error) {
      setError("Failed to copy to clipboard")
    }
  }, [])

  const filteredAndSortedRecommendations = recommendations
    .filter((rec) => {
      const matchesSearch =
        rec.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        rec.description.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesDifficulty = filterDifficulty === "all" || rec.difficulty === filterDifficulty
      const matchesType = filterType === "all" || rec.type === filterType
      return matchesSearch && matchesDifficulty && matchesType
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "relevance":
          return b.relevanceScore - a.relevanceScore
        case "difficulty":
          const difficultyOrder = { beginner: 1, intermediate: 2, advanced: 3 }
          return (
            difficultyOrder[a.difficulty as keyof typeof difficultyOrder] -
            difficultyOrder[b.difficulty as keyof typeof difficultyOrder]
          )
        case "duration":
          return (a.duration || a.readingTime || 0) - (b.duration || b.readingTime || 0)
        case "credibility":
          return b.credibilityScore - a.credibilityScore
        default:
          return 0
      }
    })

  const formatTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }, [])

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [error])

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000)
      return () => clearTimeout(timer)
    }
  }, [success])

  useEffect(() => {
    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current)
      }
      if (audioLevelIntervalRef.current) {
        clearInterval(audioLevelIntervalRef.current)
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }
    }
  }, [])

  return (
    <TooltipProvider>
      <div className="min-h-screen bg-background">
        {error && (
          <Alert className="fixed top-4 right-4 z-50 max-w-md border-destructive bg-destructive/10">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              {error}
              <Button variant="ghost" size="sm" onClick={() => setError(null)}>
                <X className="h-4 w-4" />
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="fixed top-4 right-4 z-50 max-w-md border-green-500 bg-green-50">
            <Check className="h-4 w-4 text-green-600" />
            <AlertDescription className="flex items-center justify-between text-green-800">
              {success}
              <Button variant="ghost" size="sm" onClick={() => setSuccess(null)}>
                <X className="h-4 w-4" />
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Header */}
        <header className="border-b border-border bg-card">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-primary" />
                <h1 className="text-2xl font-bold text-foreground font-[var(--font-heading)]">AI Learning Aid</h1>
              </div>
              <nav className="hidden md:flex space-x-6">
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  How it Works
                </Button>
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  Features
                </Button>
                <Button
                  variant="ghost"
                  className="text-muted-foreground hover:text-foreground"
                  onClick={() => setShowHistory(!showHistory)}
                >
                  <History className="h-4 w-4 mr-2" />
                  History
                </Button>
                <Button variant="ghost" className="text-muted-foreground hover:text-foreground">
                  <Settings className="h-4 w-4 mr-2" />
                  Settings
                </Button>
              </nav>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          {activeTab === "upload" && (
            <div className="max-w-4xl mx-auto">
              {/* Hero Section */}
              <div className="text-center mb-12">
                <h2 className="text-4xl md:text-5xl font-bold text-foreground mb-4 font-[var(--font-heading)]">
                  Turn Your Voice Notes into <span className="text-primary">Smart Study Guides</span>
                </h2>
                <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
                  Upload voice recordings and get AI-powered transcriptions, key concept extraction, and personalized
                  learning resource recommendations.
                </p>
              </div>

              {/* How It Works */}
              <div className="grid md:grid-cols-4 gap-6 mb-12">
                {[
                  { icon: Upload, title: "Upload", desc: "Voice notes or record directly" },
                  { icon: Zap, title: "Transcribe", desc: "AI converts speech to text" },
                  { icon: Target, title: "Extract", desc: "Key concepts identified" },
                  { icon: BookOpen, title: "Recommend", desc: "Personalized learning resources" },
                ].map((step, index) => (
                  <Card key={index} className="text-center hover:shadow-lg transition-all duration-300 hover:scale-105">
                    <CardContent className="pt-6">
                      <step.icon className="h-12 w-12 text-primary mx-auto mb-4" />
                      <h3 className="font-semibold text-foreground mb-2 font-[var(--font-heading)]">{step.title}</h3>
                      <p className="text-sm text-muted-foreground">{step.desc}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Upload Section */}
              <Card className="mb-8">
                <CardHeader>
                  <CardTitle className="font-[var(--font-heading)]">Upload Your Voice Note</CardTitle>
                  <CardDescription>
                    Supported formats: MP3, WAV, M4A, AAC, OGG (max 50MB) • Batch upload supported
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6">
                    {/* Enhanced File Upload */}
                    <div
                      className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 cursor-pointer ${
                        isDragOver
                          ? "border-primary bg-primary/5 scale-105"
                          : "border-border hover:border-primary hover:bg-primary/5"
                      }`}
                      onDragOver={handleDragOver}
                      onDragLeave={handleDragLeave}
                      onDrop={handleDrop}
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Upload
                        className={`h-12 w-12 mx-auto mb-4 transition-colors ${isDragOver ? "text-primary" : "text-muted-foreground"}`}
                      />
                      <p className="text-foreground font-medium mb-2">
                        {isDragOver ? "Drop your files here" : "Drag & drop your audio files"}
                      </p>
                      <p className="text-sm text-muted-foreground mb-4">
                        or click to browse • Multiple files supported
                      </p>
                      <Button variant="outline" className="transition-all hover:scale-105 bg-transparent">
                        <Upload className="h-4 w-4 mr-2" />
                        Choose Files
                      </Button>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".mp3,.wav,.m4a,.aac,.ogg,.webm,audio/*"
                        multiple
                        className="hidden"
                        onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
                      />
                    </div>

                    {/* Enhanced Voice Recording */}
                    <div className="border border-border rounded-lg p-8 text-center">
                      <div className="relative mb-4">
                        <Mic
                          className={`h-12 w-12 mx-auto transition-all duration-300 ${
                            isRecording
                              ? "text-destructive animate-pulse scale-110"
                              : "text-muted-foreground hover:text-primary"
                          }`}
                        />
                        {isRecording && (
                          <div className="absolute inset-0 rounded-full border-2 border-destructive animate-ping" />
                        )}
                      </div>

                      <p className="text-foreground font-medium mb-2">Record directly in browser</p>
                      <p className="text-sm text-muted-foreground mb-4">
                        {isRecording
                          ? `Recording: ${formatTime(recordingTime)} ${isPaused ? "(Paused)" : ""}`
                          : "Click to start recording"}
                      </p>

                      {/* Audio level indicator */}
                      {isRecording && (
                        <div className="w-full bg-muted rounded-full h-2 mb-4">
                          <div
                            className="bg-primary h-2 rounded-full transition-all duration-100"
                            style={{ width: `${audioLevel * 100}%` }}
                          />
                        </div>
                      )}

                      <div className="flex gap-2 justify-center">
                        {!isRecording ? (
                          <Button onClick={startRecording} className="transition-all hover:scale-105">
                            <Mic className="h-4 w-4 mr-2" />
                            Start Recording
                          </Button>
                        ) : (
                          <>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button variant="outline" onClick={pauseRecording}>
                                  {isPaused ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>{isPaused ? "Resume" : "Pause"}</TooltipContent>
                            </Tooltip>
                            <Button variant="destructive" onClick={stopRecording}>
                              <MicOff className="h-4 w-4 mr-2" />
                              Stop Recording
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* File Preview */}
                  {uploadedFiles.length > 0 && (
                    <div className="mt-6 p-4 bg-muted rounded-lg">
                      <h4 className="font-medium mb-3">Uploaded Files ({uploadedFiles.length})</h4>
                      <div className="space-y-2">
                        {uploadedFiles.map((file, index) => (
                          <div key={index} className="flex items-center justify-between p-2 bg-background rounded">
                            <div className="flex items-center gap-3">
                              <FileText className="h-4 w-4 text-primary" />
                              <div>
                                <p className="text-sm font-medium">{file.name}</p>
                                <p className="text-xs text-muted-foreground">
                                  {(file.size / 1024 / 1024).toFixed(1)} MB
                                  {file.duration && ` • ${formatTime(file.duration)}`}
                                </p>
                              </div>
                            </div>
                            {file.preview && (
                              <Button variant="ghost" size="sm">
                                <Play className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Features Highlights */}
              <div className="grid md:grid-cols-3 gap-6">
                {[
                  { icon: TrendingUp, title: "High Accuracy", desc: "Advanced AI transcription with 95%+ accuracy" },
                  { icon: Brain, title: "Smart Concepts", desc: "Automatically extract key learning concepts" },
                  { icon: Star, title: "Personalized", desc: "Tailored resource recommendations" },
                ].map((feature, index) => (
                  <Card key={index} className="hover:shadow-md transition-all duration-300 hover:scale-105">
                    <CardContent className="pt-6">
                      <feature.icon className="h-8 w-8 text-accent mb-3" />
                      <h3 className="font-semibold text-foreground mb-2 font-[var(--font-heading)]">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground">{feature.desc}</p>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {activeTab === "processing" && (
            <div className="max-w-2xl mx-auto text-center">
              <Card>
                <CardContent className="pt-8 pb-8">
                  <div className="relative mb-6">
                    <Brain className="h-16 w-16 text-primary mx-auto animate-pulse" />
                    <div className="absolute inset-0 rounded-full border-2 border-primary/20 animate-spin" />
                  </div>

                  <h2 className="text-2xl font-bold text-foreground mb-4 font-[var(--font-heading)]">
                    Processing Your Voice Note
                  </h2>
                  <p className="text-muted-foreground mb-6">
                    Our AI is analyzing your audio and extracting insights...
                  </p>

                  <div className="space-y-4">
                    <div className="relative">
                      <Progress value={processingProgress} className="w-full h-3" />
                      <span className="absolute right-0 top-4 text-xs text-muted-foreground">
                        {Math.round(processingProgress)}%
                      </span>
                    </div>

                    <div className="flex justify-between text-sm">
                      {["Upload", "Transcribe", "Extract", "Recommend"].map((step, index) => (
                        <div key={step} className="flex flex-col items-center">
                          <div
                            className={`w-8 h-8 rounded-full flex items-center justify-center mb-1 transition-all ${
                              index < processingStep
                                ? "bg-primary text-primary-foreground"
                                : index === processingStep
                                  ? "bg-primary/20 text-primary animate-pulse"
                                  : "bg-muted text-muted-foreground"
                            }`}
                          >
                            {index < processingStep ? (
                              <Check className="h-4 w-4" />
                            ) : (
                              <span className="text-xs">{index + 1}</span>
                            )}
                          </div>
                          <span
                            className={`text-xs ${
                              index < processingStep
                                ? "text-primary"
                                : index === processingStep
                                  ? "text-foreground font-medium"
                                  : "text-muted-foreground"
                            }`}
                          >
                            {step}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-6 p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">
                      {processingStep === 0 && "Uploading and validating your audio file..."}
                      {processingStep === 1 && "Converting speech to text using advanced AI models..."}
                      {processingStep === 2 && "Analyzing content and extracting key learning concepts..."}
                      {processingStep === 3 && "Finding personalized learning resources..."}
                    </p>
                  </div>

                  <p className="text-sm text-muted-foreground mt-4">
                    Estimated time remaining: {Math.max(0, 4 - processingStep)} minutes
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === "results" && (
            <div className="max-w-6xl mx-auto">
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-foreground mb-2 font-[var(--font-heading)]">
                  Analysis Complete!
                </h2>
                <p className="text-muted-foreground">Here's what we found in your voice note:</p>
              </div>

              <div className="grid lg:grid-cols-2 gap-8 mb-8">
                {/* Enhanced Transcription */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2 font-[var(--font-heading)]">
                        <FileText className="h-5 w-5" />
                        Transcription
                      </CardTitle>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary" className="text-xs">
                          94% confidence
                        </Badge>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <Info className="h-4 w-4" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent>
                            <p>AI-generated transcript with confidence scoring</p>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                    </div>
                    <CardDescription>
                      AI-generated transcript • Click segments to jump to audio position
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {/* Audio Player */}
                    {uploadedFiles[currentFileIndex]?.preview && (
                      <div className="mb-4 p-4 bg-muted rounded-lg">
                        <audio
                          ref={audioRef}
                          src={uploadedFiles[currentFileIndex].preview}
                          onTimeUpdate={handleTimeUpdate}
                          onLoadedMetadata={handleLoadedMetadata}
                          onEnded={() => setIsPlaying(false)}
                        />

                        <div className="flex items-center gap-4 mb-3">
                          <Button variant="outline" size="sm" onClick={togglePlayback}>
                            {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                          </Button>

                          <div className="flex-1">
                            <Slider
                              value={[currentTime]}
                              max={duration}
                              step={0.1}
                              onValueChange={([value]) => seekTo(value)}
                              className="w-full"
                            />
                          </div>

                          <span className="text-xs text-muted-foreground min-w-[80px]">
                            {formatTime(currentTime)} / {formatTime(duration)}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Button variant="ghost" size="sm" onClick={() => seekTo(Math.max(0, currentTime - 10))}>
                              <SkipBack className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => seekTo(Math.min(duration, currentTime + 10))}
                            >
                              <SkipForward className="h-4 w-4" />
                            </Button>

                            <Select
                              value={playbackRate.toString()}
                              onValueChange={(value) => changePlaybackRate(Number.parseFloat(value))}
                            >
                              <SelectTrigger className="w-20 h-8">
                                <SelectValue />
                              </SelectTrigger>
                              <SelectContent>
                                <SelectItem value="0.5">0.5x</SelectItem>
                                <SelectItem value="0.75">0.75x</SelectItem>
                                <SelectItem value="1">1x</SelectItem>
                                <SelectItem value="1.25">1.25x</SelectItem>
                                <SelectItem value="1.5">1.5x</SelectItem>
                                <SelectItem value="2">2x</SelectItem>
                              </SelectContent>
                            </Select>
                          </div>

                          <div className="flex items-center gap-2">
                            <Button variant="ghost" size="sm" onClick={toggleMute}>
                              {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                            </Button>
                            <Slider
                              value={[volume]}
                              max={1}
                              step={0.1}
                              onValueChange={([value]) => changeVolume(value)}
                              className="w-20"
                            />
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Transcription Text */}
                    <div className="relative">
                      <Textarea
                        value={editedTranscription}
                        onChange={(e) => {
                          setEditedTranscription(e.target.value)
                          setIsTranscriptionEdited(true)
                        }}
                        className={`min-h-[200px] resize-none transition-all ${showFullTranscription ? "min-h-[400px]" : ""}`}
                        placeholder="Your transcription will appear here..."
                      />

                      {isTranscriptionEdited && (
                        <Badge variant="outline" className="absolute top-2 right-2 text-xs">
                          Edited
                        </Badge>
                      )}
                    </div>

                    {/* Transcription Segments */}
                    {transcriptionSegments.length > 0 && (
                      <div className="mt-4">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setShowFullTranscription(!showFullTranscription)}
                          className="mb-2"
                        >
                          {showFullTranscription ? (
                            <ChevronUp className="h-4 w-4 mr-2" />
                          ) : (
                            <ChevronDown className="h-4 w-4 mr-2" />
                          )}
                          {showFullTranscription ? "Hide" : "Show"} Segments
                        </Button>

                        {showFullTranscription && (
                          <div className="space-y-2 max-h-40 overflow-y-auto">
                            {transcriptionSegments.map((segment, index) => (
                              <div
                                key={index}
                                className="p-2 bg-muted rounded cursor-pointer hover:bg-muted/80 transition-colors"
                                onClick={() => seekTo(segment.timestamp)}
                              >
                                <div className="flex items-center justify-between mb-1">
                                  <span className="text-xs text-muted-foreground">{formatTime(segment.timestamp)}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {Math.round(segment.confidence * 100)}%
                                  </Badge>
                                </div>
                                <p className="text-sm">{segment.text}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    <div className="flex justify-between items-center mt-4">
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" onClick={togglePlayback}>
                          <Play className="h-4 w-4 mr-2" />
                          Play Audio
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyToClipboard(editedTranscription, "transcription")}
                        >
                          {copiedText === "transcription" ? (
                            <Check className="h-4 w-4 mr-2" />
                          ) : (
                            <Copy className="h-4 w-4 mr-2" />
                          )}
                          Copy
                        </Button>
                      </div>

                      <div className="flex gap-2">
                        <Select onValueChange={(format) => exportTranscription(format as "txt" | "pdf" | "json")}>
                          <SelectTrigger className="h-8" disabled={isExporting}>
                            <SelectValue placeholder={isExporting ? "Exporting..." : "Export"} />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="txt">Export as TXT</SelectItem>
                            <SelectItem value="json">Export as JSON</SelectItem>
                            <SelectItem value="pdf">Export as PDF</SelectItem>
                          </SelectContent>
                        </Select>

                        <Button variant="outline" size="sm">
                          <Share2 className="h-4 w-4 mr-2" />
                          Share
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Enhanced Key Concepts */}
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="flex items-center gap-2 font-[var(--font-heading)]">
                        <Target className="h-5 w-5" />
                        Key Concepts
                      </CardTitle>
                      <div className="flex items-center gap-2">
                        <Select value={conceptViewMode} onValueChange={(value) => setConceptViewMode(value as any)}>
                          <SelectTrigger className="w-24 h-8">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="tags">Tags</SelectItem>
                            <SelectItem value="list">List</SelectItem>
                            <SelectItem value="map">Map</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <CardDescription>
                      Extracted learning concepts with relevance scores • Click to select
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {conceptViewMode === "tags" && (
                      <div className="space-y-3">
                        {concepts.map((concept, index) => (
                          <div
                            key={index}
                            className={`flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all hover:scale-105 ${
                              selectedConcepts.includes(concept.term)
                                ? "bg-primary/10 border border-primary"
                                : "bg-muted hover:bg-muted/80"
                            }`}
                            onClick={() => toggleConceptSelection(concept.term)}
                          >
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge variant="secondary" className="text-xs">
                                  {concept.category}
                                </Badge>
                                <Badge variant="outline" className="text-xs">
                                  {Math.round(concept.confidence * 100)}% confidence
                                </Badge>
                              </div>
                              <p className="font-medium text-foreground">{concept.term}</p>
                              {concept.definition && (
                                <p className="text-xs text-muted-foreground mt-1">{concept.definition}</p>
                              )}
                            </div>
                            <div className="text-right ml-4">
                              <p className="text-sm font-medium text-primary">{concept.relevance}%</p>
                              <div className="w-16 h-2 bg-border rounded-full mt-1">
                                <div
                                  className="h-full bg-primary rounded-full transition-all duration-500"
                                  style={{ width: `${concept.relevance}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}

                    {conceptViewMode === "list" && (
                      <div className="space-y-2">
                        {concepts
                          .sort((a, b) => b.relevance - a.relevance)
                          .map((concept, index) => (
                            <div key={index} className="flex items-center justify-between p-2 hover:bg-muted rounded">
                              <div className="flex items-center gap-3">
                                <span className="text-sm font-mono text-muted-foreground">#{index + 1}</span>
                                <div>
                                  <p className="font-medium">{concept.term}</p>
                                  <p className="text-xs text-muted-foreground">{concept.category}</p>
                                </div>
                              </div>
                              <div className="text-right">
                                <p className="text-sm font-medium text-primary">{concept.relevance}%</p>
                                <p className="text-xs text-muted-foreground">
                                  {Math.round(concept.confidence * 100)}% conf.
                                </p>
                              </div>
                            </div>
                          ))}
                      </div>
                    )}

                    {conceptViewMode === "map" && (
                      <div className="text-center py-8">
                        <Brain className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <p className="text-muted-foreground">Interactive concept map coming soon!</p>
                        <p className="text-xs text-muted-foreground mt-2">
                          This will show relationships between concepts
                        </p>
                      </div>
                    )}

                    <div className="mt-4 pt-4 border-t">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-muted-foreground">
                          {selectedConcepts.length} of {concepts.length} concepts selected
                        </p>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => copyToClipboard(concepts.map((c) => c.term).join(", "), "concepts")}
                          >
                            {copiedText === "concepts" ? (
                              <Check className="h-4 w-4 mr-2" />
                            ) : (
                              <Copy className="h-4 w-4 mr-2" />
                            )}
                            Copy All
                          </Button>
                          <Button variant="outline" size="sm">
                            <Download className="h-4 w-4 mr-2" />
                            Export
                          </Button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Enhanced Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 font-[var(--font-heading)]">
                    <BookOpen className="h-5 w-5" />
                    Learning Recommendations
                  </CardTitle>
                  <CardDescription>
                    Personalized resources based on your voice note content • {filteredAndSortedRecommendations.length}{" "}
                    resources found
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {/* Enhanced Filters */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search recommendations..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                      />
                    </div>

                    <Select value={filterDifficulty} onValueChange={setFilterDifficulty}>
                      <SelectTrigger>
                        <SelectValue placeholder="Difficulty" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Levels</SelectItem>
                        <SelectItem value="beginner">Beginner</SelectItem>
                        <SelectItem value="intermediate">Intermediate</SelectItem>
                        <SelectItem value="advanced">Advanced</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={filterType} onValueChange={setFilterType}>
                      <SelectTrigger>
                        <SelectValue placeholder="Content Type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="document">Documents</SelectItem>
                        <SelectItem value="video">Videos</SelectItem>
                        <SelectItem value="practice">Practice</SelectItem>
                      </SelectContent>
                    </Select>

                    <Select value={sortBy} onValueChange={setSortBy}>
                      <SelectTrigger>
                        <SelectValue placeholder="Sort by" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="relevance">Relevance</SelectItem>
                        <SelectItem value="difficulty">Difficulty</SelectItem>
                        <SelectItem value="duration">Duration</SelectItem>
                        <SelectItem value="credibility">Credibility</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <Tabs defaultValue="all" className="w-full">
                    <TabsList className="grid w-full grid-cols-4">
                      <TabsTrigger value="all">All ({recommendations.length})</TabsTrigger>
                      <TabsTrigger value="document">
                        Documents ({recommendations.filter((r) => r.type === "document").length})
                      </TabsTrigger>
                      <TabsTrigger value="video">
                        Videos ({recommendations.filter((r) => r.type === "video").length})
                      </TabsTrigger>
                      <TabsTrigger value="practice">
                        Practice ({recommendations.filter((r) => r.type === "practice").length})
                      </TabsTrigger>
                    </TabsList>

                    <TabsContent value="all" className="mt-6">
                      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredAndSortedRecommendations.map((rec) => (
                          <Card
                            key={rec.id}
                            className="hover:shadow-lg transition-all duration-300 hover:scale-105 group"
                          >
                            <CardContent className="pt-6">
                              {/* Resource thumbnail */}
                              {rec.thumbnail && (
                                <div className="relative mb-4 rounded-lg overflow-hidden">
                                  <img
                                    src={rec.thumbnail || "/placeholder.svg"}
                                    alt={rec.title}
                                    className="w-full h-32 object-cover group-hover:scale-110 transition-transform duration-300"
                                  />
                                  <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors" />
                                  {rec.type === "video" && (
                                    <div className="absolute inset-0 flex items-center justify-center">
                                      <div className="bg-black/50 rounded-full p-2">
                                        <Play className="h-6 w-6 text-white" />
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}

                              <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-2">
                                  {rec.type === "document" && <FileText className="h-5 w-5 text-blue-500" />}
                                  {rec.type === "video" && <Video className="h-5 w-5 text-red-500" />}
                                  {rec.type === "practice" && <Target className="h-5 w-5 text-green-500" />}
                                  <Badge variant="outline" className="text-xs">
                                    {rec.difficulty}
                                  </Badge>
                                </div>
                                <div className="flex items-center gap-1">
                                  <span className="text-sm font-medium text-primary">{rec.relevanceScore}%</span>
                                  <Tooltip>
                                    <TooltipTrigger asChild>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => toggleBookmark(rec.id)}
                                        className="h-8 w-8 p-0"
                                      >
                                        {rec.isBookmarked ? (
                                          <BookmarkCheck className="h-4 w-4 text-primary" />
                                        ) : (
                                          <Bookmark className="h-4 w-4" />
                                        )}
                                      </Button>
                                    </TooltipTrigger>
                                    <TooltipContent>
                                      {rec.isBookmarked ? "Remove bookmark" : "Add bookmark"}
                                    </TooltipContent>
                                  </Tooltip>
                                </div>
                              </div>

                              <h3 className="font-semibold text-foreground mb-2 font-[var(--font-heading)] line-clamp-2">
                                {rec.title}
                              </h3>
                              <p className="text-sm text-muted-foreground mb-3 line-clamp-3">{rec.description}</p>

                              <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                                <div className="flex items-center gap-2">
                                  <span>{rec.source}</span>
                                  <Badge variant="outline" className="text-xs">
                                    {rec.credibilityScore}% credible
                                  </Badge>
                                </div>
                                {(rec.duration || rec.readingTime) && (
                                  <span className="flex items-center gap-1">
                                    <Clock className="h-3 w-3" />
                                    {rec.duration ? `${rec.duration}min` : `${rec.readingTime}min read`}
                                  </span>
                                )}
                              </div>

                              <div className="flex gap-2">
                                <Button size="sm" className="flex-1" asChild>
                                  <a href={rec.url} target="_blank" rel="noopener noreferrer">
                                    {rec.type === "video" ? "Watch" : rec.type === "practice" ? "Practice" : "Read"}
                                  </a>
                                </Button>
                                <Button size="sm" variant="outline">
                                  <Share2 className="h-4 w-4" />
                                </Button>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>

                      {filteredAndSortedRecommendations.length === 0 && (
                        <div className="text-center py-12">
                          <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                          <h3 className="font-semibold text-foreground mb-2">No resources found</h3>
                          <p className="text-muted-foreground">Try adjusting your search or filter criteria</p>
                        </div>
                      )}
                    </TabsContent>

                    {["document", "video", "practice"].map((type) => (
                      <TabsContent key={type} value={type} className="mt-6">
                        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                          {filteredAndSortedRecommendations
                            .filter((rec) => rec.type === type)
                            .map((rec) => (
                              <Card
                                key={rec.id}
                                className="hover:shadow-lg transition-all duration-300 hover:scale-105 group"
                              >
                                <CardContent className="pt-6">
                                  {/* Same enhanced card content as above */}
                                  {rec.thumbnail && (
                                    <div className="relative mb-4 rounded-lg overflow-hidden">
                                      <img
                                        src={rec.thumbnail || "/placeholder.svg"}
                                        alt={rec.title}
                                        className="w-full h-32 object-cover group-hover:scale-110 transition-transform duration-300"
                                      />
                                      <div className="absolute inset-0 bg-black/20 group-hover:bg-black/10 transition-colors" />
                                      {rec.type === "video" && (
                                        <div className="absolute inset-0 flex items-center justify-center">
                                          <div className="bg-black/50 rounded-full p-2">
                                            <Play className="h-6 w-6 text-white" />
                                          </div>
                                        </div>
                                      )}
                                    </div>
                                  )}

                                  <div className="flex items-start justify-between mb-3">
                                    <Badge variant="outline" className="text-xs">
                                      {rec.difficulty}
                                    </Badge>
                                    <div className="flex items-center gap-1">
                                      <span className="text-sm font-medium text-primary">{rec.relevanceScore}%</span>
                                      <Button
                                        variant="ghost"
                                        size="sm"
                                        onClick={() => toggleBookmark(rec.id)}
                                        className="h-8 w-8 p-0"
                                      >
                                        {rec.isBookmarked ? (
                                          <BookmarkCheck className="h-4 w-4 text-primary" />
                                        ) : (
                                          <Bookmark className="h-4 w-4" />
                                        )}
                                      </Button>
                                    </div>
                                  </div>

                                  <h3 className="font-semibold text-foreground mb-2 font-[var(--font-heading)]">
                                    {rec.title}
                                  </h3>
                                  <p className="text-sm text-muted-foreground mb-3">{rec.description}</p>

                                  <div className="flex items-center justify-between text-xs text-muted-foreground mb-4">
                                    <span>{rec.source}</span>
                                    {(rec.duration || rec.readingTime) && (
                                      <span className="flex items-center gap-1">
                                        <Clock className="h-3 w-3" />
                                        {rec.duration ? `${rec.duration}min` : `${rec.readingTime}min read`}
                                      </span>
                                    )}
                                  </div>

                                  <div className="flex gap-2">
                                    <Button size="sm" className="flex-1" asChild>
                                      <a href={rec.url} target="_blank" rel="noopener noreferrer">
                                        {rec.type === "video" ? "Watch" : rec.type === "practice" ? "Practice" : "Read"}
                                      </a>
                                    </Button>
                                    <Button size="sm" variant="outline">
                                      <Share2 className="h-4 w-4" />
                                    </Button>
                                  </div>
                                </CardContent>
                              </Card>
                            ))}
                        </div>
                      </TabsContent>
                    ))}
                  </Tabs>
                </CardContent>
              </Card>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer className="border-t border-border bg-card mt-16">
          <div className="container mx-auto px-4 py-8">
            <div className="grid md:grid-cols-4 gap-8">
              <div>
                <div className="flex items-center space-x-2 mb-4">
                  <Brain className="h-6 w-6 text-primary" />
                  <span className="font-bold text-foreground font-[var(--font-heading)]">AI Learning Aid</span>
                </div>
                <p className="text-sm text-muted-foreground">
                  Transform your voice notes into smart study guides with AI-powered insights.
                </p>
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-3 font-[var(--font-heading)]">Features</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>Voice Transcription</li>
                  <li>Concept Extraction</li>
                  <li>Smart Recommendations</li>
                  <li>Study Analytics</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-3 font-[var(--font-heading)]">Support</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>Help Center</li>
                  <li>Contact Us</li>
                  <li>Privacy Policy</li>
                  <li>Terms of Service</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibent text-foreground mb-3 font-[var(--font-heading)]">Connect</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>Twitter</li>
                  <li>LinkedIn</li>
                  <li>GitHub</li>
                  <li>Blog</li>
                </ul>
              </div>
            </div>
            <div className="border-t border-border mt-8 pt-8 text-center text-sm text-muted-foreground">
              <p>&copy; 2024 AI Learning Aid. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>
    </TooltipProvider>
  )
}
