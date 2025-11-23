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


class EventTypes:
    PROJECT_CREATED = "Project created"
    RESOURCE_ADDED = "Resource added"
    RESOURCE_PROCESSING_STARTED = "Resource processing started"
    RESOURCE_PROCESSING_ENCOUNTERED_ERROR = "Resource processing encountered error"
    RESOURCE_DOWNLOADED_AND_TEXT_EXTRACTED = "Resource downloaded and text extracted"
    RESOURCE_PROCESSED = "Resource processed"
