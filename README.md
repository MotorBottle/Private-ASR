# Audio Processor

This project is modded from **FunClip** project, built with ASR (Automatic Speech Recognition), speaker identification, SRT editing, and LLM-based summarization capabilities. It integrates **Gradio** as the user interface, providing an interactive and easy-to-use platform.

[简体中文](./README_zh.md) / [English](./README.md)

本项目基于开源项目 **FunClip** 进行修改，集成了自动语音识别 (ASR)、说话人分离、SRT 字幕编辑以及基于 LLM 的总结功能。项目使用 **Gradio** 提供了一个直观易用的用户界面。

---

## 📜 **Credits**

This project builds upon the open-source **[FunClip](https://github.com/alibaba-damo-academy/FunClip)** by [Alibaba DAMO Academy](https://github.com/alibaba-damo-academy). I modded the functionality to include:

- **ASR Summarization** using LLMs (OpenAI GPT, custom API).
- **Dynamic SRT Replacement** with speaker mapping.
- **Deployment Ready** using Docker for production environments.

---

## 🎯 **Features**

1. **Automatic Speech Recognition (ASR):**  
   - Supports video and audio inputs.  
   - Outputs text and SRT subtitles.

2. **Speaker Identification (SD):**  
   - Identifies and differentiates speakers in multi-speaker audio/video.

3. **SRT Subtitle Editing:**  
   - Replace speaker identifiers with user-defined names.

4. **LLM Summarization:**  
   - Summarize ASR results using GPT-based models.  
   - Allows custom API configurations.

5. **Deployment Options:**  
   - Lightweight Docker container for production.  
   - Python environment for development/testing.

---

## 🛠 **Requirements**

### System(2 Ways to Deploy)
- **Docker** (for containerized deployment)
- **Python 3.9+** (for manual deployment)

### Dependencies
See the `requirements.txt` file

---

## 🚀 **Deployment**

### 1. **Docker Deployment**

#### **Build the Docker Image**
Run the following command to build the Docker image:
```bash
docker build -t audio-processor:latest .
```

#### **Deploy with Docker Compose**
Use the following `docker-compose.yml` file for deployment:

```yaml
version: '3.8'

services:
  audio-processor:
    image: audio-processor:latest
    container_name: audio-processor
    ports:
      - "7860:7860"  # Map Gradio service to host port
    environment:
      - USERNAME=motor      # Username for login
      - PASSWORD=admin      # Password for login
    volumes:
      - ./.env:/app/.env    # Map .env file for credentials
```

Run the deployment:
```bash
docker-compose up -d
```

The Gradio interface will be available at:  
`http://localhost:7860`

---

### 2. **Python Deployment**

#### **Setup Environment**

1. Clone the repository:
   ```bash
   git clone https://github.com/MotorBottle/Audio-Processor.git
   cd audio-processor
   ```

2. Install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install --no-cache-dir -r requirements.txt
   ```

3. Ensure **FFmpeg** is installed(for Mac use brew):
   ```bash
   sudo apt-get update
   sudo apt-get install -y ffmpeg
   ```

#### **Run the Application**

Use the following command:
```bash
python funclip/launch.py --listen
```

The Gradio interface will be available at:  
`http://localhost:7860`

---

## ⚙️ **Environment Configuration**

All credentials and API configurations can be stored in a `.env` file.

Example `.env` file:
```bash
USERNAME=motor
PASSWORD=admin
OPENAI_API_KEY=your_openai_key
OPENAI_API_BASE=https://your-custom-api.com
```

---

## 🎥 **Usage**

1. Upload audio or video files.
2. Perform **ASR Recognition** or **Speaker Differentiation**.
3. Edit speaker names in the generated SRT subtitles.
4. Use the **LLM Summarization** feature to analyze and summarize the ASR text.

---

## 🔗 **Contributions & License**

This project is released under the **MIT License**. Contributions are welcome!

For the original FunClip repository, visit:  
[FunClip on GitHub](https://github.com/alibaba-damo-academy/FunClip)

---
