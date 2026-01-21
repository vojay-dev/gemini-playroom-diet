# Playroom Diet

![Playroom Diet Logo](doc/banner.png)

> **Elevator Pitch**: One photo. Four AI agents map toys to O*NET professional skills, build a 6-month roadmap, and generate a Play Quest using what you own. A nutritionist for your child's play.

**Playroom Diet** is an AI-powered child development tool that transforms chaotic toy piles into science-backed growth plans. Upload a photo of your playroom, and our multi-agent AI pipeline analyzes the toys, maps them to professional skill frameworks, and generates a personalized 6-month development roadmap. Think of it as a nutritionist for your child's play, ensuring a balanced "diet" of developmental stimulation.

<!-- TODO: Add live demo link -->
<!-- **Try it yourself**: [playroom-diet.com](https://playroom-diet.com/) -->

_Keep in mind: this is a hackathon prototype. Daily limits apply to control costs._

![Playroom Mockup](doc/mockup.png)

---

## tl;dr for Judges

This project demonstrates a **multi-agent AI pipeline** using Apache Airflow and Gemini, not just a single-prompt wrapper:

1. **Agent 1**: Vision AI extracts toy inventory with bounding box coordinates
2. **Agent 2**: Maps toys to O*NET professional skill framework
3. **Agent 3**: Safety-checks recommendations against CPSC guidelines
4. **Agent 4**: Generates a Play Quest using existing toys

The result: a 6-month roadmap with shopping links, plus an immediate activity parents can do today.

<!-- TODO: Add instructions for local testing at the end -->

---

## Inspiration

Every parent has been there: a room overflowing with toys, yet somehow their child keeps reaching for the same three items. Meanwhile, developmental milestones loom, and the guilt of "am I doing enough?" creeps in.

<!-- TODO: Add mockup image -->
<!-- ![Playroom Diet](https://files.janz.sh/playroom-diet/mockup.png) -->

**The problem isn't too few toys, it's the wrong mix.**

Just like a diet needs balance across food groups, a child's play environment needs balance across developmental domains. But most parents aren't child development experts, and the toy industry's marketing doesn't help.

**Playroom Diet bridges this gap** by treating play as a child's "job" and mapping toy interactions to the same professional skill frameworks used by the US Department of Labor (O*NET). The result? Parents get clear, actionable insights instead of vague advice.

**Imagine a world where every playroom is optimized not for quantity, but for developmental quality.**

---

## What It Does

Simply upload a photo of your playroom, enter your child's age, and Playroom Diet delivers:

### 1. Toy Inventory with AI Detection
Gemini Vision analyzes the image and identifies every toy, categorizing them by type and play mode. Each toy is mapped with bounding box coordinates for visual feedback.

### 2. Skill Assessment (O*NET Framework)
The US Department of Labor's O*NET database defines the cognitive and physical abilities that predict success across 1,000+ occupations, from surgeons to software engineers. These aren't abstract concepts; they're measurable capacities like *Visualization*, *Finger Dexterity*, and *Oral Expression* that form the foundation of career readiness.

**The insight**: These abilities don't suddenly appear in adulthood. They're built through play. A child stacking blocks is training *Visualization*. Finger painting develops *Fine Motor Control*. Pretend play builds *Social Perceptiveness*.

Playroom Diet maps your toys to these O*NET abilities, scoring your playroom across 6 developmental categories:

- **Cognitive**: Problem solving, reasoning, memory
- **Fine Motor**: Finger dexterity, precision, hand-eye coordination
- **Gross Motor**: Body coordination, balance, strength
- **Social-Emotional**: Empathy, cooperation, emotional expression
- **Creative**: Imagination, artistic expression, open-ended play
- **Language**: Communication, vocabulary, storytelling

### 3. Personalized 6-Month Roadmap
Based on skill gaps, we generate a prioritized development plan:
- **Now**: Most critical gap to address immediately
- **3 Months**: Second priority for near-term growth
- **6 Months**: Third priority for longer-term development

Each recommendation includes the specific O*NET ability being developed and scientific reasoning.

### 4. Safety Verification (CPSC Guidelines)
Every toy recommendation passes through a safety audit against Consumer Product Safety Commission guidelines for the child's age. Unsafe recommendations are automatically substituted with safer alternatives.

### 5. One-Click Shopping
Approved recommendations include optimized search queries for major retailers (Amazon, Target, Walmart), avoiding generic knock-offs in favor of quality brands.

### 6. Visual Heatmap
The results page displays your original image with an AI-style detection overlay, showing exactly where toys were identified, giving parents confidence in the analysis accuracy.

### 7. Play Quest
Don't wait for new toys to arrive. A dedicated AI agent creates a fun, structured play activity using toys you already own. Each quest targets a specific O*NET skill, includes step-by-step instructions, and gives parents tips to maximize engagement. Start improving development today.

![Playroom Screenshots](doc/screenshots.png)

<!-- TODO: Add screenshots -->
<!-- ![Skill Radar](https://files.janz.sh/playroom-diet/skill-radar.png) -->
<!-- ![Heatmap](https://files.janz.sh/playroom-diet/heatmap.png) -->

---

## How It Was Built

### Tech Stack

#### Backend
- **Python 3.12 + FastAPI** for API development
- **Supabase** for database and image storage
- **Apache Airflow** for orchestrating the multi-agent pipeline
- **Gemini 3 Flash** via Airflow AI SDK for all LLM tasks
- **Pydantic** for strict data validation and structured outputs

#### Frontend
- **Vue.js 3** with Composition API
- **Vite** for blazing-fast development
- **Tailwind CSS + daisyUI** for styling
- **Chart.js** for skill radar visualization

#### Infrastructure
- **Supabase** (Postgres + Storage)
- **Apache Airflow** (workflow orchestration)

### System Architecture

```
┌─────────────┐     ┌─────────────┐     ┌───────────────────────────────────────┐
│   Frontend  │────▶│   Backend   │────▶│            Apache Airflow             │
│   (Vue.js)  │     │  (FastAPI)  │     │                                       │
└─────────────┘     └─────────────┘     │  ┌─────────┐                          │
                           │            │  │ Agent 1 │                          │
                           ▼            │  │ Vision  │──┬──────────────────┐    │
                    ┌─────────────┐     │  └─────────┘  │                  │    │
                    │  Supabase   │     │               ▼                  ▼    │
                    │  (Storage)  │◀────│  ┌─────────────────┐  ┌────────────┐  │
                    └─────────────┘     │  │ Agent 2: O*NET  │  │ Agent 4:   │  │
                                        │  │ + Agent 3: CPSC │  │ Play Quest │  │
                                        │  └────────┬────────┘  └─────┬──────┘  │
                                        │           └──────┬──────────┘         │
                                        │                  ▼                    │
                                        │           ┌────────────┐              │
                                        │           │   Save     │              │
                                        │           └────────────┘              │
                                        └───────────────────────────────────────┘
```

### The Multi-Agent Pipeline

What sets Playroom Diet apart from typical AI demos is the **orchestrated multi-agent architecture**:

**Agent 1: `analyze_image`**
- Input: Playroom photo
- Model: Gemini 3 Flash (Vision)
- Output: Structured `ToyInventory` with bounding boxes
- Purpose: Extract what's in the room with spatial coordinates

**Agent 2: `analyze_playroom`**
- Input: Toy inventory + child's age
- Model: Gemini 3 Flash
- Output: `AnalysisResult` with skill scores and roadmap
- Purpose: Map toys to O*NET abilities, identify gaps, recommend toys

**Agent 3: `safety_check`**
- Input: Roadmap recommendations + child's age
- Model: Gemini 3 Flash
- Output: `ToyRecommendation` with safety decisions
- Purpose: Validate against CPSC, substitute unsafe toys, generate shopping queries

**Agent 4: `generate_play_quest`**
- Input: Toy inventory + child's age
- Model: Gemini 3 Flash
- Output: `PlayQuest` with activity details
- Purpose: Create an immediate play activity using existing toys
- Runs in parallel with Agent 2

This pipeline ensures:
- **Separation of concerns**: Each agent has a focused task
- **Structured outputs**: Pydantic models enforce data quality
- **Deterministic flow**: Airflow manages dependencies and retries

---

## Technical Highlights

### Structured AI Outputs
Every LLM call uses Pydantic models to enforce schema compliance:

```python
class Toy(BaseModel):
    category: str
    item_name: str
    count: int
    play_mode: str
    bbox: BoundingBox  # Normalized 0-1 coordinates
```

### Resolution-Independent Detection
Bounding boxes use normalized coordinates (0-1 range), making the heatmap visualization work regardless of image resolution or display size.

### Static Token Support
The Airflow client supports both dynamic JWT authentication and static tokens, enabling flexible deployment scenarios.

### Automatic Data Cleanup
A background scheduler automatically removes scans and images older than a configurable threshold (default: 2 days), preventing storage bloat without manual intervention.

---

## What I Learned

Building Playroom Diet pushed me to think beyond single-prompt AI demos:

- **Multi-agent orchestration** with Airflow creates more robust, maintainable AI systems
- **Structured outputs** (Pydantic + JSON mode) are essential for production AI
- **Professional frameworks** (O*NET, CPSC) add credibility and real-world value
- **Visual feedback** (heatmaps, detection boxes) builds user trust in AI decisions

Most importantly: the best AI products don't just generate text, they integrate domain expertise into actionable workflows.

---

## What's Next

- **Toy Recognition Database**: Build a knowledge base of specific toys and their developmental properties
- **Progress Tracking**: Let parents log purchases and re-scan to see improvement over time
- **Personalized Recommendations**: Factor in existing toy inventory to avoid duplicates
- **Chrome Extension**: Analyze toy listings on e-commerce sites before purchase
- **Integration with Pediatricians**: Export reports in formats useful for developmental check-ups

---

## Project Structure

```
gemini-playroom-diet/
├── frontend/          # Vue.js application
├── backend/           # FastAPI server
├── airflow/           # DAG definitions and AI agents
│   └── dags/
│       └── playroom_diet.py
├── start.sh           # Local development startup script
└── README.md
```

---

## Local Development

### Prerequisites
- Python 3.12+
- Node.js 18+
- Apache Airflow 3.0+ with AI SDK
- Supabase project (or local instance)
- Gemini API access

### Quick Start

```bash
# Start all services
./start.sh

# Or individually:
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
cd airflow && airflow standalone
```

### Environment Variables

**Backend (.env)**
```
SUPABASE_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_key
AIRFLOW_HOST=http://localhost:8080
AIRFLOW_USERNAME=airflow
AIRFLOW_PASSWORD=airflow
CLEANUP_AGE_DAYS=2           # optional, default: 2
CLEANUP_INTERVAL_MINUTES=60  # optional, default: 60
```

**Airflow**
```
SUPABASE_PROJECT_URL=your_supabase_url
SUPABASE_SECRET_KEY=your_supabase_key
```

---

## Example Output

```json
{
  "status_quo": "High concentration in 'Verbal-Social' clusters. The dominance of figurines, dress-up, and books indicates strong development in Oral Expression (1.A.1.a.1) and Social Perceptiveness.",
  "skill_scores": {
    "cognitive": 65,
    "motor_fine": 45,
    "motor_gross": 30,
    "social_emotional": 85,
    "creative": 70,
    "language": 80
  },
  "roadmap": [
    {
      "timeframe": "now",
      "missing_skill": "Visualization (1.A.1.f.2)",
      "recommended_toy": "Magna-Tiles 100-Piece Set",
      "decision": "APPROVED",
      "safety_context": "Magna-Tiles use ultrasonic welding to securely encapsulate magnets, exceeding CPSC requirements."
    }
  ]
}
```

---

<!-- TODO: Add final banner/call-to-action image -->

**The skills they build today become the strengths they carry forever.**
