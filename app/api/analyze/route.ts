import { NextRequest, NextResponse } from "next/server"

const BACKEND_BASE_URL = process.env.BACKEND_BASE_URL || "http://127.0.0.1:8000"

export async function POST(req: NextRequest) {
	try {
		const formData = await req.formData()
		const audio = formData.get("audio") as File | null

		if (!audio) {
			return NextResponse.json({ error: "Missing audio file" }, { status: 400 })
		}

		// Forward to backend
		const forwardForm = new FormData()
		forwardForm.append("audio", audio)

		const res = await fetch(`${BACKEND_BASE_URL}/api/v1/analyze`, {
			method: "POST",
			body: forwardForm,
			// Do not set content-type manually; let fetch compute multipart boundary
		})

		if (!res.ok) {
			const text = await res.text()
			return NextResponse.json({ error: "Backend error", details: text }, { status: 502 })
		}

		const data = await res.json()
		return NextResponse.json(data)
	} catch (err: any) {
		return NextResponse.json({ error: "Analyze failed", details: String(err) }, { status: 500 })
	}
}
