# StudySnap

> An AI-powered study companion designed to help students learn from their own study material, with a long-term focus on on-device AI using Snapdragon hardware.

##  Overview

StudySnap is an AI study companion that allows students to upload study material such as PDFs and ask questions about the content.

The current prototype focuses on the core experience:

**Upload PDF → Process Content → Ask a Question → Get an AI-generated Answer**

The long-term vision is to optimize the AI inference pipeline for Snapdragon-powered PCs, enabling more private, responsive, and offline-friendly AI-assisted learning.

---

## Current Features

-  PDF upload
-  PDF text extraction
-  Question answering based on uploaded study material
-  AI-powered explanations
-  API credentials stored securely using environment variables

---

## Planned Features

-  AI-generated quizzes
-  Weak-topic detection
-  Knowledge maps
-  Adaptive "Teach Me" mode
-  Voice-based interaction
-  Image/problem understanding
-  Local/offline AI inference
-  Snapdragon NPU-accelerated AI inference

---

## Technology Stack

### Current Prototype

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python, Flask
- **AI:** Cloud-based LLM API
- **PDF Processing:** PyMuPDF
- **Configuration:** Python `dotenv`

### Future Snapdragon Integration

The AI layer is being designed to be replaceable so that the current cloud AI provider can eventually be replaced by a locally running model optimized for Snapdragon-powered PCs.

Potential technologies include:

- Qualcomm AI Hub
- Qualcomm AI Runtime
- Snapdragon Hexagon NPU
- Quantized AI models
- Local inference runtimes

> **Note:** Snapdragon is the hardware platform. The AI model itself will be a compatible model that can be optimized and executed on Snapdragon hardware through an appropriate runtime.

---

## Current Architecture

```text
Student
   │
   ▼
StudySnap Web Interface
   │
   ▼
Flask Backend
   │
   ▼
PDF Processing
   │
   ▼
Extracted Study Material
   │
   ▼
AI Provider
   │
   ▼
AI-Generated Answer

```

## Future Architecture

```text
Student
   │
   ▼
StudySnap
   │
   ▼
AI Abstraction Layer
   │
   ├───────────────┐
   ▼               ▼
Cloud AI       Local AI Model
Provider            │
                    ▼
             Qualcomm Runtime
                    │
              ┌─────┴─────┐
              ▼           ▼
             NPU       CPU / GPU
```
