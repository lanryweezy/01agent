from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi
from . import llm_provider


llm = llm_provider.get_llm(agent='summarizer', temperature=1.0)


async def fetch_and_summarize_url(url: str) -> str:
    loader = WebBaseLoader(url)
    documents = await loader.aload()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    full_text = "\n\n".join(doc.page_content for doc in docs)

    prompt = ChatPromptTemplate.from_template("Summarize the following:\n\n{input}")
    chain = prompt | llm

    result = await chain.ainvoke({"input": full_text})
    return result.content if hasattr(result, "content") else str(result)


async def fetch_and_summarize_pdf(file_path: str = None, url: str = None) -> str:
    if url:
        import aiohttp
        import tempfile
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                try:
                    temp_file.write(await response.read())
                    temp_file.close()
                    file_path = temp_file.name
                finally:
                    # Ensure the file is closed before UnstructuredPDFLoader tries to open it
                    temp_file.close()

    loader = UnstructuredPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    # Prepare the full text
    full_text = "\n\n".join(doc.page_content for doc in docs)

    prompt = ChatPromptTemplate.from_template("Summarize the following:\n\n{input}")
    chain = prompt | llm

    result = await chain.ainvoke({"input": full_text})
    return result.content if hasattr(result, "content") else str(result)


async def summarize_youtube_video(url: str) -> str:
    try:
        # Extract video ID from URL
        if "watch?v=" in url:
            video_id = url.split("watch?v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
        else:
            raise CustomError(status.HTTP_400_BAD_REQUEST, "Invalid YouTube URL format.")

        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        try:
            # Try to find an English transcript first
            transcript = transcript_list.find_transcript(["en"])
        except Exception:
            # If English not found, fallback to first available transcript
            transcript = next(iter(transcript_list))

        # Fetch the transcript content
        fetched = transcript.fetch()
        transcript_text = "\n".join([snippet.text for snippet in fetched])

        # Split the transcript into manageable chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.create_documents([transcript_text])
        full_text = "\n\n".join(chunk.page_content for chunk in chunks)

        # Use the LLM to summarize
        prompt = ChatPromptTemplate.from_template("Summarize the following YouTube transcript:\n\n{input}")
        chain = prompt | llm
        result = await chain.ainvoke({"input": full_text})

        return result.content if hasattr(result, "content") else str(result)

    except Exception as e:
        raise CustomError(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Error summarizing video: {str(e)}")


async def os_list_files(directory: str) -> str:
    import os
    try:
        files = os.listdir(directory)
        return "\n".join(files)
    except Exception as e:
        return f"Error listing files: {e}"


async def os_read_file(file_path: str) -> str:
    import os
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(5000) # Limit to 5000 chars
    except Exception as e:
        return f"Error reading file: {e}"


async def os_get_system_info() -> str:
    import platform
    import psutil
    info = {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "cpu_count": psutil.cpu_count(),
        "memory": f"{psutil.virtual_memory().total / (1024**3):.2f} GB"
    }
    return json.dumps(info, indent=2)


async def run_tool_server_side(tool_name: str, args: dict) -> str:
    if tool_name == "fetch_url":
        return await fetch_and_summarize_url(args["url"])

    if tool_name == "read_pdf":
        return await fetch_and_summarize_pdf(args.get("file_path"), args.get("url"))

    if tool_name == "summarize_youtube_video":
        return await summarize_youtube_video(args["url"])

    if tool_name == "os_list_files":
        return await os_list_files(args.get("directory", "."))

    if tool_name == "os_read_file":
        return await os_read_file(args.get("file_path"))

    if tool_name == "os_get_system_info":
        return await os_get_system_info()

    raise ValueError(f"Unsupported tool: {tool_name}")