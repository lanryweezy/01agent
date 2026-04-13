import os
import json
import subprocess
import platform
import psutil
import pyperclip
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.document_loaders import UnstructuredPDFLoader, WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from . import llm_provider

# Tool Registry
class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self.llm = llm_provider.get_llm(agent='summarizer', temperature=1.0)

    def register(self, name: str):
        def decorator(func):
            self.tools[name] = func
            return func
        return decorator

    async def execute(self, name: str, args: dict) -> str:
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found in registry.")
        return await self.tools[name](self, **args)

registry = ToolRegistry()

# Tool Implementations

@registry.register("fetch_url")
async def fetch_and_summarize_url(reg, url: str):
    loader = WebBaseLoader(url)
    documents = await loader.aload()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    full_text = "\n\n".join(doc.page_content for doc in docs)
    prompt = ChatPromptTemplate.from_template("Summarize the following:\n\n{input}")
    chain = prompt | reg.llm
    result = await chain.ainvoke({"input": full_text})
    return result.content

@registry.register("read_pdf")
async def fetch_and_summarize_pdf(reg, file_path: str = None, url: str = None):
    if url:
        import aiohttp
        import tempfile
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(await response.read())
                    file_path = temp_file.name

    loader = UnstructuredPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    full_text = "\n\n".join(doc.page_content for doc in docs)
    prompt = ChatPromptTemplate.from_template("Summarize the following PDF content:\n\n{input}")
    chain = prompt | reg.llm
    result = await chain.ainvoke({"input": full_text})
    return result.content

@registry.register("summarize_youtube_video")
async def summarize_youtube_video(reg, url: str):
    try:
        video_id = url.split("watch?v=")[-1].split("&")[0] if "watch?v=" in url else url.split("/")[-1]
        transcript_list = YouTubeTranscriptApi().list(video_id)
        try: transcript = transcript_list.find_transcript(["en"])
        except: transcript = next(iter(transcript_list))

        fetched = transcript.fetch()
        transcript_text = "\n".join([s.text for s in fetched])
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        full_text = "\n\n".join([c.page_content for c in text_splitter.create_documents([transcript_text])])

        prompt = ChatPromptTemplate.from_template("Summarize this YouTube transcript:\n\n{input}")
        chain = prompt | reg.llm
        result = await chain.ainvoke({"input": full_text})
        return result.content
    except Exception as e:
        return f"Error summarizing video: {e}"

@registry.register("os_list_files")
async def os_list_files(reg, directory: str = "."):
    try: return "\n".join(os.listdir(directory))
    except Exception as e: return f"Error: {e}"

@registry.register("os_read_file")
async def os_read_file(reg, file_path: str):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(10000)
    except Exception as e: return f"Error: {e}"

@registry.register("os_write_file")
async def os_write_file(reg, file_path: str, content: str):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f: f.write(content)
        return f"Wrote to {file_path}"
    except Exception as e: return f"Error: {e}"

@registry.register("os_delete_file")
async def os_delete_file(reg, file_path: str):
    try:
        if os.path.isdir(file_path):
            import shutil
            shutil.rmtree(file_path)
        else: os.remove(file_path)
        return f"Deleted {file_path}"
    except Exception as e: return f"Error: {e}"

@registry.register("os_search_files")
async def os_search_files(reg, query: str, root: str = "."):
    matches = []
    try:
        for r, d, f in os.walk(root):
            for file in f:
                if query.lower() in file.lower(): matches.append(os.path.join(r, file))
            if len(matches) > 20: break
        return "\n".join(matches) or "No matches."
    except Exception as e: return f"Error: {e}"

@registry.register("os_get_system_info")
async def os_get_system_info(reg):
    info = {
        "system": platform.system(), "release": platform.release(),
        "cpu_count": psutil.cpu_count(), "memory": f"{psutil.virtual_memory().total / (1024**3):.2f} GB"
    }
    return json.dumps(info, indent=2)

@registry.register("os_clipboard_get")
async def os_clipboard_get(reg):
    return pyperclip.paste()

@registry.register("os_shell_execute")
async def os_shell_execute(reg, command: str):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    except Exception as e: return f"Error: {e}"

async def run_tool_server_side(tool_name: str, args: dict) -> str:
    return await registry.execute(tool_name, args)
