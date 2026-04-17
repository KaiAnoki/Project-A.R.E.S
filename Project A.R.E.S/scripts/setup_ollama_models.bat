@echo off
echo Pulling recommended local models for ARES...
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
ollama pull phi3:mini
echo Done.
