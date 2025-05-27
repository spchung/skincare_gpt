# SkincareGPT - AI Skincare Assistant

A conversational AI system that helps users discover skincare products and understand reviews through semantic search and natural language processing.

## Overview

This is a FastAPI-based chatbot that processes user queries about skincare products and reviews. It uses LangGraph for conversation orchestration and integrates with OpenAI's GPT models for intelligent responses.

There is also a Streamlit interface available in `chat_ui.py`

## Key Features

- **Intent Classification**: Automatically routes user queries (product search, review analysis, filtered search, follow-ups)
- **Semantic Search**: Vector-based search using Qdrant and sentence transformers
- **RAG System**: Retrieval-augmented generation for contextual responses
- **Memory Management**: Tracks conversation context and mentioned entities
- **User Profiling**: Initial questionnaire for personalized recommendations

## Architecture

- **Backend**: FastAPI with graph-based conversation flow (LangGraph)
- **AI**: OpenAI GPT-4o-mini + sentence transformers for embeddings
- **Data**: PostgreSQL (structured data) + Qdrant (vector search) + Redis (session cache)
- **Dataset**: Sephora products and reviews with rich metadata

## Tech Stack

```
FastAPI + LangGraph + OpenAI + Qdrant + PostgreSQL + Redis
```

## Project Structure

```
app/
├── lang_graphs/chat_v1/    # Conversation orchestration
├── models/                 # Data models (products, reviews)
├── routes/                 # API endpoints
├── semantic_search/        # Vector search logic
└── memory/                 # Context management
```

This system demonstrates advanced conversational AI patterns including multi-step reasoning, context preservation, and hybrid search approaches.