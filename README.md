# Tripping AI 🌍✈️

Tripping AI is an intelligent, generative travel planning platform that crafts hyper-personalized trip itineraries. By leveraging multiple AI agents and real-world data sources, it transforms vague travel ideas into detailed, bookable plans.

![Tripping AI Logo](logo.png)

## 🌟 Key Features

- **Generative Chat Interface**: Interact with an AI that understands your travel desires even when they are vague.
- **Dynamic Requirement Extraction**: Automatically builds a structured "Trip YAML" from your conversation to ensure all your needs are captured.
- **Vibe-Based Personalized Plans**: Generates multiple itinerary variations (e.g., "Budget Explorer", "Luxury Relaxer", "Urban Adventurer") tailored to your preferences.
- **Real-Time Data Integration**: Fetches actual hotel availability and flight information via industry-standard APIs.
- **AI-Powered Itinerary Editing**: Refine your trip using natural language commands (e.g., "Add a day in Paris", "Find cheaper hotels").
- **Cohesive Trip Packages**: Aggregates flights, stays, activities, and transfers into a single, beautiful visual timeline.

## 🏗️ Architecture at a Glance

Tripping AI is built as a microservices-based monorepo:

- **Frontend**: Next.js-powered dashboard with a responsive, premium design.
- **API Gateway**: Node.js/Express server orchestrating the flow between the UI and AI services.
- **AI Agents**: Specialized Python services for content generation, JSON manipulation, and data retrieval.
- **Data Collectors**: Dedicated services for flight, hotel, and activity discovery.
- **Cache/Storage**: MongoDB for session management and Redis for high-performance data caching.

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/)
- An Amadeus API Key (for flights)
- A Perplexity/OpenAI API Key (for LLM services)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/tripping-ai-monorepo.git
   cd tripping-ai-monorepo
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory based on the provided `.env.example` (or existing `.env`):
   ```env
   AMADEUS_CLIENT_ID=your_id
   AMADEUS_CLIENT_SECRET=your_secret
   PERPLEXITY_API_KEY=your_key
   ```

3. **Launch the Services**:
   ```bash
   docker-compose up --build
   ```

4. **Access the App**:
   Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📖 Learn More

For a deep dive into the backend architecture and service relationships, check out the [Backend Documentation](apps/README.md).
