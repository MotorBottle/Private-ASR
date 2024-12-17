#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
# Copyright FunASR (https://github.com/alibaba-damo-academy/FunClip). All Rights Reserved.
#  MIT License  (https://opensource.org/licenses/MIT)

from http import server
import os
import logging
import argparse
import gradio as gr
from funasr import AutoModel
from videoclipper import VideoClipper
from llm.openai_api import openai_call
from llm.qwen_api import call_qwen_model
from llm.g4f_openai_api import g4f_openai_call
from llm.private_api import openai_call
from utils.trans_utils import extract_timestamps
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 获取账号和密码，设置默认值
DEFAULT_USERNAME = os.getenv("USERNAME", "motor")
DEFAULT_PASSWORD = os.getenv("PASSWORD", "admin")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='argparse testing')
    parser.add_argument('--lang', '-l', type=str, default = "zh", help="language")
    parser.add_argument('--share', '-s', action='store_true', help="if to establish gradio share link")
    parser.add_argument('--port', '-p', type=int, default=7860, help='port number')
    parser.add_argument('--listen', action='store_true', help="if to listen to all hosts")
    args = parser.parse_args()
    
    if args.lang == 'zh':
        funasr_model = AutoModel(model="iic/speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
                                vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
                                punc_model="damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
                                spk_model="damo/speech_campplus_sv_zh-cn_16k-common",
                                )
    else:
        funasr_model = AutoModel(model="iic/speech_paraformer_asr-en-16k-vocab4199-pytorch",
                                vad_model="damo/speech_fsmn_vad_zh-cn-16k-common-pytorch",
                                punc_model="damo/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
                                spk_model="damo/speech_campplus_sv_zh-cn_16k-common",
                                )
    audio_clipper = VideoClipper(funasr_model)
    audio_clipper.lang = args.lang
    
    server_name='127.0.0.1'
    if args.listen:
        server_name = '0.0.0.0'
        

    def audio_recog(audio_input, sd_switch, hotwords, output_dir):
        return audio_clipper.recog(audio_input, sd_switch, None, hotwords, output_dir=output_dir)

    def video_recog(video_input, sd_switch, hotwords, output_dir):
        return audio_clipper.video_recog(video_input, sd_switch, hotwords, output_dir=output_dir)

    def video_clip(dest_text, video_spk_input, start_ost, end_ost, state, output_dir):
        return audio_clipper.video_clip(
            dest_text, start_ost, end_ost, state, dest_spk=video_spk_input, output_dir=output_dir
            )

    def mix_recog(video_input, audio_input, hotwords, output_dir):
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        audio_state, video_state = None, None
        if video_input is not None:
            res_text, res_srt, video_state = video_recog(
                video_input, 'No', hotwords, output_dir=output_dir)
            return res_text, res_srt, video_state, None
        if audio_input is not None:
            res_text, res_srt, audio_state = audio_recog(
                audio_input, 'No', hotwords, output_dir=output_dir)
            return res_text, res_srt, None, audio_state
    
    def mix_recog_speaker(video_input, audio_input, hotwords, output_dir):
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        audio_state, video_state = None, None
        if video_input is not None:
            res_text, res_srt, video_state = video_recog(
                video_input, 'Yes', hotwords, output_dir=output_dir)
            return res_text, res_srt, video_state, None
        if audio_input is not None:
            res_text, res_srt, audio_state = audio_recog(
                audio_input, 'Yes', hotwords, output_dir=output_dir)
            return res_text, res_srt, None, audio_state
    
    def mix_clip(dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir):
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        if video_state is not None:
            clip_video_file, message, clip_srt = audio_clipper.video_clip(
                dest_text, start_ost, end_ost, video_state, dest_spk=video_spk_input, output_dir=output_dir)
            return clip_video_file, None, message, clip_srt
        if audio_state is not None:
            (sr, res_audio), message, clip_srt = audio_clipper.clip(
                dest_text, start_ost, end_ost, audio_state, dest_spk=video_spk_input, output_dir=output_dir)
            return None, (sr, res_audio), message, clip_srt
    
    def video_clip_addsub(dest_text, video_spk_input, start_ost, end_ost, state, output_dir, font_size, font_color):
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        return audio_clipper.video_clip(
            dest_text, start_ost, end_ost, state, 
            font_size=font_size, font_color=font_color, 
            add_sub=True, dest_spk=video_spk_input, output_dir=output_dir
            )
        
    # def llm_inference(system_content, user_content, srt_text, model, apikey):
    #     SUPPORT_LLM_PREFIX = ['qwen', 'gpt', 'g4f', 'moonshot']
    #     if model.startswith('qwen'):
    #         return call_qwen_model(apikey, model, user_content+'\n'+srt_text, system_content)
    #     if model.startswith('gpt') or model.startswith('moonshot'):
    #         return openai_call(apikey, model, system_content, user_content+'\n'+srt_text)
    #     elif model.startswith('g4f'):
    #         model = "-".join(model.split('-')[1:])
    #         return g4f_openai_call(model, system_content, user_content+'\n'+srt_text)
    #     else:
    #         logging.error("LLM name error, only {} are supported as LLM name prefix."
    #                       .format(SUPPORT_LLM_PREFIX))

    def llm_inference(system_content, user_content, srt_text, model, apikey, api_base=None):
        """
        This function will check for the model prefix and call the appropriate API method (in this case, OpenAI).
        """
        return openai_call(apikey, model, system_content, user_content+'\n'+srt_text, api_base=api_base)
    
    def AI_clip(LLM_res, dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir):
        timestamp_list = extract_timestamps(LLM_res)
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        if video_state is not None:
            clip_video_file, message, clip_srt = audio_clipper.video_clip(
                dest_text, start_ost, end_ost, video_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=False)
            return clip_video_file, None, message, clip_srt
        if audio_state is not None:
            (sr, res_audio), message, clip_srt = audio_clipper.clip(
                dest_text, start_ost, end_ost, audio_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=False)
            return None, (sr, res_audio), message, clip_srt
    
    def AI_clip_subti(LLM_res, dest_text, video_spk_input, start_ost, end_ost, video_state, audio_state, output_dir):
        timestamp_list = extract_timestamps(LLM_res)
        output_dir = output_dir.strip()
        if not len(output_dir):
            output_dir = None
        else:
            output_dir = os.path.abspath(output_dir)
        if video_state is not None:
            clip_video_file, message, clip_srt = audio_clipper.video_clip(
                dest_text, start_ost, end_ost, video_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=True)
            return clip_video_file, None, message, clip_srt
        if audio_state is not None:
            (sr, res_audio), message, clip_srt = audio_clipper.clip(
                dest_text, start_ost, end_ost, audio_state, 
                dest_spk=video_spk_input, output_dir=output_dir, timestamp_list=timestamp_list, add_sub=True)
            return None, (sr, res_audio), message, clip_srt
        
    def extract_speaker_labels(subtitles):
        """
        从字幕内容中提取所有的 spkX 标识，并生成默认的映射字符串。
        :param subtitles: SRT字幕内容
        :return: 默认的说话人映射字符串 (如 "spk0:, spk1:, spk2:")
        """
        import re
        speakers = sorted(set(re.findall(r"\bspk\d+\b", subtitles)))
        return "\n".join(f"{speaker}:" for speaker in speakers)

    def prepare_speaker_map(subtitles):
        """
        根据字幕内容动态生成预填充的说话人映射规则。
        :param subtitles: 当前 SRT 字幕内容
        :return: 默认的说话人映射规则字符串
        """
        return extract_speaker_labels(subtitles)

    def parse_speaker_map(speaker_map_str):
        """
        解析用户输入的说话人映射字符串为字典。
        :param speaker_map_str: 说话人映射字符串，每行一个映射 (如 "spk0:张三\nspk1:\nspk2:王五")
        :return: 解析后的字典 (如 {"spk0": "张三", "spk2": "王五"})
        """
        try:
            return {
                item.split(":", 1)[0].strip(): item.split(":", 1)[1].strip()
                for item in speaker_map_str.splitlines()
                if ":" in item.strip() and item.split(":", 1)[1].strip()  # 忽略空值行
            }
        except ValueError:
            raise ValueError("说话人映射格式错误，请输入正确的格式，例如每行 'spk0:张三'")


    def replace_speaker_in_subtitles(subtitles, speaker_map_str):
        """
        替换字幕中的说话人标识。
        :param subtitles: 原始SRT字幕内容（字符串）
        :param speaker_map_str: 用户提供的说话人映射字符串 (如 "spk0:张三, spk1:李四")
        :return: 替换后的SRT字幕内容
        """
        # 将映射字符串解析为字典
        speaker_map = parse_speaker_map(speaker_map_str)
        
        # 替换SRT内容中的说话人
        def replace_speaker_line(line):
            for old_speaker, new_speaker in speaker_map.items():
                line = line.replace(old_speaker, new_speaker)
            return line

        # 逐行替换SRT内容
        lines = subtitles.split("\n")
        replaced_lines = [replace_speaker_line(line) for line in lines]
        return "\n".join(replaced_lines)

    def summarize_asr(system_prompt, user_prompt, asr_text, model, apikey, api_base=None):
        """
        调用LLM总结ASR识别内容
        :param system_prompt: 系统设定的Prompt
        :param user_prompt: 用户输入的Prompt
        :param asr_text: ASR识别的结果
        :param model: LLM模型名称
        :param apikey: 用户提供的API密钥
        :param api_base: 自建API的Base URL，默认为None
        :return: LLM返回的总结结果
        """
        return llm_inference(system_prompt, user_prompt, asr_text, model, apikey, api_base=api_base)


    # gradio interface
    theme = gr.Theme.load("funclip/utils/theme.json")
    with gr.Blocks(theme=theme) as funclip_service:

        video_state, audio_state = gr.State(), gr.State()
        with gr.Row():
            with gr.Column():
                with gr.Row():
                    video_input = gr.Video(label="视频输入 | Video Input")
                    audio_input = gr.Audio(label="音频输入 | Audio Input")
                with gr.Column():
                    gr.Examples(['https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E4%B8%BA%E4%BB%80%E4%B9%88%E8%A6%81%E5%A4%9A%E8%AF%BB%E4%B9%A6%EF%BC%9F%E8%BF%99%E6%98%AF%E6%88%91%E5%90%AC%E8%BF%87%E6%9C%80%E5%A5%BD%E7%9A%84%E7%AD%94%E6%A1%88-%E7%89%87%E6%AE%B5.mp4', 
                                 'https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/2022%E4%BA%91%E6%A0%96%E5%A4%A7%E4%BC%9A_%E7%89%87%E6%AE%B52.mp4', 
                                 'https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E4%BD%BF%E7%94%A8chatgpt_%E7%89%87%E6%AE%B5.mp4'],
                                [video_input],
                                label='示例视频 | Demo Video')
                    gr.Examples(['https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E8%AE%BF%E8%B0%88.mp4'],
                                [video_input],
                                label='多说话人示例视频 | Multi-speaker Demo Video')
                    gr.Examples(['https://isv-data.oss-cn-hangzhou.aliyuncs.com/ics/MaaS/ClipVideo/%E9%B2%81%E8%82%83%E9%87%87%E8%AE%BF%E7%89%87%E6%AE%B51.wav'],
                                [audio_input],
                                label="示例音频 | Demo Audio")
                    with gr.Column():
                        # with gr.Row():
                            # video_sd_switch = gr.Radio(["No", "Yes"], label="👥区分说话人 Get Speakers", value='No')
                        hotwords_input = gr.Textbox(label="🚒 热词 | Hotwords(可以为空，多个热词使用空格分隔，仅支持中文热词)")
                        output_dir = gr.Textbox(label="📁 文件输出路径 | File Output Dir (可以为空，Linux, mac系统可以稳定使用)", value=" ")
                        with gr.Row():
                            recog_button = gr.Button("👂 识别 | ASR", variant="primary")
                            recog_button2 = gr.Button("👂👫 识别+区分说话人 | ASR+SD")
                video_text_output = gr.Textbox(label="✏️ 识别结果 | Recognition Result")
                video_srt_output = gr.Textbox(label="📖 SRT字幕内容 | SRT Subtitles")
            with gr.Column():
                # 替换说话人 Tab
                with gr.Tab("🔄 替换说话人 Replace Speaker"):
                    speaker_map_input = gr.Textbox(
                        label="替换规则 | Replacement Rules (每行格式: spkX:名称)",
                        placeholder="自动生成当前字幕的spkX标识...",
                        lines=10,  # 允许多行输入
                    )
                    replace_button = gr.Button("替换 Replace", variant="primary")
                    replaced_srt_output = gr.Textbox(label="替换后的SRT字幕内容 | Replaced SRT Subtitles")

                    # 自动填充 speaker_map_input 的默认值
                    video_srt_output.change(
                        prepare_speaker_map,
                        inputs=[video_srt_output],
                        outputs=[speaker_map_input],
                    )

                    replace_button.click(
                        replace_speaker_in_subtitles,
                        inputs=[video_srt_output, speaker_map_input],
                        outputs=[replaced_srt_output],
                    )

                with gr.Tab("📄 LLM文档总结 | LLM Document Summarization"):
                    with gr.Column():
                        # 系统Prompt输入框
                        system_prompt_input = gr.Textbox(
                            label="Prompt System (系统提示词)",
                            placeholder="请输入系统Prompt，例如：你是一个语音识别总结助手...",
                            value=("你是一个语音识别总结助手，接收用户提供的语音转文本（ASR）结果，根据用户指令总结关键信息或生成内容。"
                                "语音转文本的结果以srt的形式提供，例如：\n"
                                "0  spk0\n"
                                "00:00:00,50 --> 00:00:09,810\n"
                                "语句1\n"
                                "1  spk1\n"
                                "00:00:10,270 --> 00:00:12,150\n"
                                "语句2\n"
                                "2  spk1\n"
                                "00:00:12,790 --> 00:00:13,890\n"
                                "语句3\n"
                                "如果序号后没有说话人名，则为不区分说话人asr结果")
                        )

                        user_prompt_input = gr.Textbox(
                            label="Prompt User (用户自定义提示词)",
                            placeholder="请输入用户Prompt，例如：总结以下内容的关键信息...",
                            value="总结以下内容的关键信息，讨论的主题、纪要、要点和总结，不同发言者的观点（如有），以及结论和目标（如有）"
                        )

                        # LLM模型选择框
                        llm_model = gr.Dropdown(
                            choices=["qwen2.5:32b", "gpt-3.5-turbo", "gpt-4o"],
                            value="qwen2.5:32b",
                            label="LLM Model Name",
                            allow_custom_value=True
                        )

                        # 密钥输入框，隐藏显示密码
                        apikey_input = gr.Textbox(
                            label="APIKEY",
                            placeholder="输入API Key（如需使用GPT或Qwen API）",
                            type="password",  # 默认隐藏
                        )

                        # 自建API Base URL 输入框
                        api_base_input = gr.Textbox(
                            label="API Base (可选)",
                            placeholder="请输入自建API Base（如果有的话）",
                            lines=1
                        )

                        # 总结按钮
                        summarize_button = gr.Button(
                            "总结 Summarize (使用LLM总结ASR内容)",
                            variant="primary"
                        )

                        # 总结结果显示框
                        llm_summary_result = gr.Textbox(
                            label="总结结果 | Summary Result",
                            placeholder="LLM返回的总结结果将显示在这里"
                        )

                        # 正确传递输入内容给函数
                        def get_valid_srt_output(video_srt, replaced_srt):
                            """
                            Check which SRT content is valid: replaced or original.
                            :param video_srt: Original SRT content
                            :param replaced_srt: Replaced SRT content
                            :return: The valid SRT content
                            """
                            
                            if replaced_srt and replaced_srt.strip():
                                return replaced_srt.strip()
                            else:
                                return video_srt.strip()

                        # 点击事件中调用 summarize_asr，动态选择有效的 SRT 内容
                        summarize_button.click(
                            lambda system, user, video_srt, replaced_srt, model, apikey, api_base: summarize_asr(
                                system,
                                user,
                                get_valid_srt_output(video_srt, replaced_srt),
                                model,
                                apikey,
                                api_base
                            ),
                            inputs=[
                                system_prompt_input,      # 系统提示词
                                user_prompt_input,        # 用户提示词
                                video_srt_output,         # 原始 SRT 内容
                                replaced_srt_output,      # 替换后的 SRT 内容
                                llm_model,                # 选择的 LLM 模型
                                apikey_input,             # API Key
                                api_base_input            # API Base URL
                            ],
                            outputs=[llm_summary_result]  # 输出结果
                        )

        recog_button.click(mix_recog, 
                            inputs=[video_input, 
                                    audio_input, 
                                    hotwords_input, 
                                    output_dir,
                                    ], 
                            outputs=[video_text_output, video_srt_output, video_state, audio_state])
        recog_button2.click(mix_recog_speaker, 
                            inputs=[video_input, 
                                    audio_input, 
                                    hotwords_input, 
                                    output_dir,
                                    ], 
                            outputs=[video_text_output, video_srt_output, video_state, audio_state])

    # start gradio service in local or share
    if args.listen:
        funclip_service.launch(
            share=args.share, 
            server_port=args.port, 
            server_name=server_name, 
            inbrowser=False,
            auth=(DEFAULT_USERNAME, DEFAULT_PASSWORD)  # 添加账号和密码认证
        )
    else:
        funclip_service.launch(
            share=args.share, 
            server_port=args.port, 
            server_name=server_name,
            auth=(DEFAULT_USERNAME, DEFAULT_PASSWORD)  # 添加账号和密码认证
        )