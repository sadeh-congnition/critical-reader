class Provider:
    JINA = "Jina AI"
    OLLAMA = "Ollama"


class JINA_AI_MODELS:
    READER_LM_V2 = "ReaderLM-v2"
    JINA_EMBEDDINGS_V4 = "jina-embeddings-v4"

    @classmethod
    def reader_models(cls):
        return [cls.READER_LM_V2]


class DownloaderType:
    WEB_PAGE_SCRAPER = "Web page scraper"
    JINA_AI_READER_USING_JINA_API = "Jina AI reader using Jina API"


class ConversationStatus:
    NEW = "New"
    PROCESSING_RESOURCES = "Processing resources"


class ResourceStatus:
    NEW = "New"
    DOWNLOADED = "Downloaded"
    SCRAPED = "Scraped"
    ERROR = "Error"
    PROCESSED = "Processed"


class ChunkerType:
    FIXED = "Fixed size"
    NO_CHUNK = "No chunking"


class ProcessorType:
    SIMPLE_RAG = "Simple RAG"
