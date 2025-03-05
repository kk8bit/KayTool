import os
import json
import re
import torch


JSON_DIR = os.path.join(os.path.dirname(__file__), "../json")

class StrongPrompt:
    
    _styles_data = None
    
    @classmethod
    def _load_styles(cls):
        if cls._styles_data is not None:
            return
        
        file_path = os.path.join(JSON_DIR, "Strong_Prompt.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                cls._styles_data = json.load(f)
        except Exception as e:
            print(f"Error loading Strong Prompt JSON: {e}")
            cls._styles_data = []

    @classmethod
    def INPUT_TYPES(cls) -> dict:
        cls._load_styles()
        
        styles = [entry["name"] for entry in cls._styles_data or [] if "name" in entry]

        input_types = {
            "required": {
                "positive": ("STRING", {"multiline": True, "placeholder": "positive", "tooltip": "The positive prompt text. (正向提示词文本。)"}),  
                "negative": ("STRING", {"multiline": True, "placeholder": "negative", "tooltip": "The negative prompt text. (负向提示词文本。)"}),  
                "clip": ("CLIP", {"tooltip": "The CLIP model used for encoding the prompts. (用于编码提示词的CLIP模型。)"})  
            },
            "optional": {},
            "hidden": {
                "unique_id": "UNIQUE_ID",
            }
        }

        
        input_types["required"]["Negative_Out"] = ("BOOLEAN", {"default": True, "label": "Enable Negative Output (启用负向输出)", "tooltip": "Toggle to enable/disable the output of negative prompt. (切换以启用或禁用负向提示词输出。)"})

        for i in range(1, 7): 
            input_types["required"][f'Strong_Prompt_{i}'] = (styles, {"default": None, "tooltip": f"Select a preset style for position {i}. (选择位置 {i} 的预设样式。)"})

        
        input_types["required"]["Strong_Prompt_Switch"] = ("BOOLEAN", {"default": True, "label": "Enable Presets (启用预设)", "tooltip": "Toggle to enable/disable the use of presets. (切换以启用或禁用预设的使用)"})

       
        input_types["required"]["IDs"] = ("STRING", {"default": "", "multiline": False, "tooltip": "Enter style IDs separated by commas (001,002,003). (输入预设序号或由逗号分隔的序号（例如：001,002,003)"})
        
        
        input_types["required"]["IDs_Switch"] = ("BOOLEAN", {"default": True, "label": "Enable IDs (启用ID)", "tooltip": "Toggle to enable/disable the use of style IDs. (切换以启用或禁用样式ID的使用)"})
        
        return input_types

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "STRING", "STRING")  
    RETURN_NAMES = ("positive", "negative", "positive_text", "negative_text")
    OUTPUT_TOOLTIPS = (
        "A conditioning containing the embedded positive prompt used to guide the diffusion model. (包含嵌入式正向提示词的条件化对象，用于引导扩散模型)",
        "A conditioning containing the embedded negative prompt used to guide the diffusion model. (包含嵌入式负向提示词的条件化对象，用于引导扩散模型)",
        "The final synthesized positive prompt text before converting into conditioning. (转换为条件化对象之前的最终合成正向提示词文本)",
        "The final synthesized negative prompt text before converting into conditioning. (转换为条件化对象之前的最终合成负向提示词文本)"
    )
    FUNCTION = "encode_prompts"
    CATEGORY = "KayTool"
    DESCRIPTION = "Generates and encodes positive and negative prompts using a CLIP model into embeddings that can be used to guide the diffusion model. (使用CLIP模型生成并编码正向和负向提示词，转换为可用于指导扩散模型的嵌入)"

    def encode_prompts(self, clip, positive='', negative='', IDs='', Strong_Prompt_Switch=True, IDs_Switch=True, Negative_Out=True, **kwargs):
        self._load_styles()

        all_styles = {re.split('-', entry["name"], maxsplit=1)[0].strip(): entry for entry in self._styles_data or [] if "name" in entry}
        positive_prompt, negative_prompt = '', ''

       
        if Strong_Prompt_Switch:
            for i in range(1, 7):
                style_name = kwargs.get(f'Strong_Prompt_{i}')
                if style_name and style_name != "None":
                    style = all_styles.get(re.split('-', style_name, maxsplit=1)[0].strip(), {})
                    if 'positive' in style and style['positive']:
                        positive_prompt += (', ' if positive_prompt else '') + style['positive']

                    if 'negative' in style and style['negative']:
                        negative_prompt += (', ' if negative_prompt else '') + style['negative']

        
        positive_prompt = positive if not Strong_Prompt_Switch or not positive_prompt else positive + ', ' + positive_prompt
        negative_prompt = negative if not Strong_Prompt_Switch or not negative_prompt else negative + ', ' + negative_prompt

       
        if IDs_Switch and IDs:
            selected_style_names = []
            ids = [id.strip() for id in IDs.split(',')]
            for id in ids:
                if id in all_styles:
                    selected_style_names.append(all_styles[id]["name"])

            for style_name in selected_style_names:
                style = all_styles.get(re.split('-', style_name, maxsplit=1)[0].strip(), {})
                if 'positive' in style and style['positive']:
                    positive_prompt += (', ' if positive_prompt else '') + style['positive']

                if 'negative' in style and style['negative']:
                    negative_prompt += (', ' if negative_prompt else '') + style['negative']

        
        positive_prompt = positive_prompt.strip(', ')
        negative_prompt = negative_prompt.strip(', ')

        print(f"🟢Final Positive Prompt: {positive_prompt}")

        if Negative_Out:
            print(f"🔴Final Negative Prompt: {negative_prompt}")
        else:
            print("🔵Negative Prompt Zeroed Out.")
            negative_prompt = ''  

        try:
            positive_conditioning = clip.encode_from_tokens_scheduled(clip.tokenize(positive_prompt or ""))
            
            if Negative_Out:
                negative_conditioning = clip.encode_from_tokens_scheduled(clip.tokenize(negative_prompt or ""))
            else:
                
                negative_conditioning = self.zero_out(clip.encode_from_tokens_scheduled(clip.tokenize(negative_prompt or "")))

            
            return (positive_conditioning, negative_conditioning, positive_prompt, negative_prompt if Negative_Out else "")
        except Exception as e:
            print(f"Error during encoding: {e}")
            raise RuntimeError(f"Failed to encode prompts: {e}") from e

    def zero_out(self, conditioning):
        """Zero out the conditioning tensors."""
        c = []
        for t in conditioning:
            d = t[1].copy()
            pooled_output = d.get("pooled_output", None)
            if pooled_output is not None:
                d["pooled_output"] = torch.zeros_like(pooled_output)
            n = [torch.zeros_like(t[0]), d]
            c.append(n)
        return c


os.makedirs(JSON_DIR, exist_ok=True)