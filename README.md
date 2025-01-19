# Friands - Finding Restaurants, Insights And Notably Delectable Spots
### Streamlit Restaurant Discovery App
## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Running the App](#running-the-app)
- [Behind the scene technologies](#behind-the-scene-technologies)
- [Contributing](#contributing)
- [Authors](#authors)  


## Overview

Friands (Finding Restaurants, Insights And Notably Delectable Spots) is a restaurant analytics and recommendation engine. It leverages advanced Natural Language Processing and Machine Learning techniques to provide meaningful insights about dining establishments.

![demo](.github/demo.gif)

## Features

- 🔍 Advanced restaurant search with multi-criteria filtering
- 📊 Sentiment analysis of customer reviews
- 🗺️ Geographic visualization of restaurants
- 📈 Analytics dashboards
- 🤖 Automated review summarization
- 📱 Responsive and intuitive UI

## Requirements

Make sure you have :
- [Docker Desktop](https://docs.docker.com/get-docker/) installed and running,
- [Docker Compose](https://docs.docker.com/compose/install/) installed and executable
- 10GB available disk space,
- one [Mistral API Key](https://console.mistral.ai/api-keys/)
- and a stable internet connection.

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/berangerthomas/friands
```

2. Access the local root directory of the project:
```
cd friands
```

3. Set up environment variable with your own [Mistral API Key](https://console.mistral.ai/) :
```bash
cp .env.example .env
# Then edit .env file, and replace "Insert_your_key_here" with your Mistral API key
```

## Running the App

### First Time Setup

1. Start Docker Desktop
2. Spin up services with the command:
```bash
docker-compose up
```

### Updates

To update the application with latest changes:

```bash
git pull
docker-compose up --build
```

### Service Endpoints

You can access the app through this link :
- Web UI: [http://localhost:8501](http://localhost:8501)

### Shutdown

```bash
docker-compose down
```

## Behind the scene technologies

Friands is using many differents technologies to perform its different tasks. Here's a quick description of each one :

- Main programming language : [Python](https://www.python.org/)
- Web interface : [Streamlit](https://streamlit.io/)
- containerization : [Docker](https://www.docker.com/)
- Graphs : [Plotly](https://plotly.com/python/)
- Database : [SQLite](https://www.sqlite.org/)
- Text summarization : [Mistral AI](https://mistral.ai)
- NLP :
    - [Spacy](https://spacy.io/)
    - [NLTK](https://www.nltk.org/)
    - [Fine tuned BERT model](https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment)


## Contributing

We welcome contributions! Here's how to get started:

1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Contribution Guidelines
- Adhere to existing code style (Black + PEP 8)
- Add tests for new features
- Update documentation as needed
- Reference relevant issues
- Follow conventional commits


## Authors
- [Souraya Ahmed Abderemane](https://github.com/Sahm269)
- [Lucile Perbet](https://github.com/lucilecpp)
- [Béranger Thomas](https://github.com/berangerthomas)

---

Built with ❤️ by the Friands team
