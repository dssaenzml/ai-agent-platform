# AI Agent Platform

A comprehensive multi-agent AI platform built with LangChain, FastAPI, and modern AI technologies. This platform demonstrates enterprise-grade AI agent development with modular architecture, supporting multiple specialized AI agents for different business domains.

## 🌟 Features

- **Multi-Agent Architecture**: Modular design supporting multiple specialized AI agents
- **LangChain Integration**: Built on LangChain framework for robust AI workflows
- **Vector Database Support**: Integration with Qdrant for semantic search and retrieval
- **Document Processing**: Advanced document processing with OCR capabilities
- **Real-time Chat Interface**: WebSocket support for real-time conversations
- **Enterprise Security**: Role-based access control and secure API endpoints
- **Scalable Deployment**: Docker containerization with Kubernetes support
- **Multi-Modal Support**: Text, audio, and image processing capabilities

## 🏗️ Architecture

The platform follows a modular architecture with the following key components:

- **API Layer**: FastAPI-based REST API with async support
- **Agent Chain**: LangChain-based processing chains for different agent types
- **Graph Processing**: Node-based workflow execution using LangGraph
- **Vector Storage**: Qdrant vector database for semantic search
- **Document Processing**: Unstructured data processing pipeline
- **Memory Management**: Persistent conversation memory with Snowflake integration

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker (optional)
- API keys for Azure OpenAI, HuggingFace, etc.

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dssaenzml/ai-agent-platform.git
cd ai-agent-platform
```

2. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .dev_env .env
# Edit .env with your API keys and configuration
```

### Running Locally

Start the development server:
```bash
uvicorn app.server:app --host 0.0.0.0 --port 8080 --env-file .env
```

The API will be available at `http://localhost:8080`

### Running with Docker

Build and run the Docker container:
```bash
docker build . -t ai-agent-platform:latest
docker run -d --name ai-agent-app --env-file .env -p 8080:8080 ai-agent-platform:latest
```

## 🔧 Configuration

### Environment Variables

Copy `.dev_env` to `.env` and configure the following key variables:

#### AI Services
- `AZURE_OPENAI_LLM_API_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_LLM_ENDPOINT`: Azure OpenAI endpoint
- `HUGGING_FACE_HUB_TOKEN`: HuggingFace token for model access

#### Vector Database
- `VEC_DB_URL`: Qdrant vector database URL
- `VEC_DB_API_KEY`: Qdrant API key

#### Storage
- `AZ_TENANT_ID`: Azure tenant ID
- `AZ_CLIENT_ID`: Azure client ID
- `AZ_SECRET_ID`: Azure secret
- `BLOB_CONTAINER_NAME`: Azure Blob Storage container

#### External Services
- `BING_SUBSCRIPTION_KEY`: Bing Search API key (for web search)

## 🤖 Available Agents

The platform supports multiple specialized AI agents:

1. **General Agent**: General-purpose conversational AI and assistance
2. **Engineering Agent**: Technical documentation and engineering queries
3. **Real Estate Agent**: Property and real estate analysis
4. **Finance Agent**: Financial analysis and reporting
5. **HR Agent**: Human resources and policy assistance
6. **Operations Agent**: Operational processes and logistics
7. **Analytics Agent**: Data analysis and business intelligence
8. **Workflow Agent**: Process automation and workflow management
9. **Procurement Agent**: Procurement processes and documentation
10. **Automation Agent**: RPA and automation assistance

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Agent Interaction
```
POST /api/v1/generalagent/generalagent_rag/invoke
POST /api/v1/financeagent/financeagent_rag/invoke
POST /api/v1/engineeringagent/engineeringagent_rag/invoke
```

### File Processing
```
POST /api/v1/generalagent/generalagent_process_kb_file/invoke
POST /api/v1/financeagent/financeagent_process_user_file/invoke
```

### Real-time Chat (Streaming)
```
POST /api/v1/generalagent/generalagent_rag/stream
POST /api/v1/financeagent/financeagent_rag/stream
```

## 🧪 Development

### Project Structure

```
ai-agent-platform/
├── app/
│   ├── api/                 # FastAPI routes and endpoints
│   ├── chain/              # LangChain processing chains
│   ├── graph/              # LangGraph node definitions
│   ├── model/              # Data models and schemas
│   ├── prompt/             # Prompt templates
│   ├── tools/              # Custom tools and integrations
│   └── vector_db/          # Vector database operations
├── docs/                   # Documentation and knowledge base
├── graphs/                 # System architecture diagrams
└── packages/               # Additional packages
```

### Adding New Agents

1. Create agent-specific modules in:
   - `app/chain/{agent_name}/`
   - `app/graph/{agent_name}/`
   - `app/model/{agent_name}/`
   - `app/prompt/{agent_name}/`

2. Add API endpoint in `app/api/endpoints/{agent_name}.py`

3. Configure vector database collection in `app/vector_db/{agent_name}.py`

### Testing

Run tests with:
```bash
python -m pytest tests/
```

## 🐳 Docker Support

### Building

```bash
docker build . -t ai-agent-platform:latest
```

### Running with GPU Support (for local LLM)

```bash
docker run -d --name ai-agent-app --gpus 1 --env-file .env -p 8080:8080 ai-agent-platform:latest
```

### Running Local LLM with vLLM

```bash
docker run -d --name llama3_service --gpus 1 \
  -v huggingface_cache:/home/huggingface_cache \
  --env "HUGGING_FACE_HUB_TOKEN=your_token_here" \
  -p 8000:8000 --ipc=host \
  vllm/vllm-openai:v0.5.4 \
  --model meta-llama/Meta-Llama-3-8B-Instruct \
  --api-key test123 \
  --dtype float16 \
  --max-model-len 2048
```

## 🌐 Production Deployment

The platform includes production-ready features:

- **Kubernetes Manifests**: Ready for K8s deployment
- **Health Checks**: Comprehensive monitoring endpoints
- **Logging**: Structured logging with request tracking
- **Rate Limiting**: Built-in API rate limiting
- **CORS Support**: Configurable CORS policies

## 🔐 Security

- API key authentication
- Role-based access control
- Input validation and sanitization
- Secure file upload handling
- Environment-based configuration

## 📚 Documentation

- [API Documentation](http://localhost:8080/docs) - Available when running locally
- [Architecture Overview](./docs/architecture.md)
- [Deployment Guide](./docs/deployment.md)
- [Agent Development Guide](./docs/agent-development.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://github.com/langchain-ai/langchain)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- Vector search by [Qdrant](https://qdrant.tech/)
- Document processing by [Unstructured](https://unstructured.io/)

## 📞 Contact

For questions and support, please open an issue in the GitHub repository.

---

**Note**: This is a portfolio project demonstrating enterprise AI agent development. Replace placeholder values in the configuration files with your actual API keys and endpoints before deployment.
